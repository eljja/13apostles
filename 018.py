import os
import sys
import time
import json
from functools import wraps

# ==========================================
# FEATURE: Global Execution and Token Budget
# ==========================================
class BudgetExceededException(Exception):
    """Raised when execution time or token limits are breached."""
    def __init__(self, message, audit_json=None):
        super().__init__(message)
        self.audit_json = audit_json

class ResourceBudgetTracker:
    def __init__(self, max_tokens=10000, max_time_sec=5.0):
        self.max_tokens = max_tokens
        self.max_time_sec = max_time_sec
        self.tokens_used = 0
        self.start_time = time.time()
        self.trace_events = []
        self._add_trace_event("INITIALIZATION", {"max_tokens": max_tokens, "max_time_sec": max_time_sec})

    def _add_trace_event(self, event_type, details):
        event = {
            "elapsed_ms": round((time.time() - self.start_time) * 1000, 2),
            "event_type": event_type,
            "details": details
        }
        if len(self.trace_events) < 100:
            self.trace_events.append(event)
        else:
            first_part = self.trace_events[:10]
            marker = {
                "elapsed_ms": event["elapsed_ms"], 
                "event_type": "TRUNCATED", 
                "details": {"message": "Older events truncated to mitigate memory/telemetry bloat."}
            }
            last_part = self.trace_events[-89:]
            self.trace_events = first_part + [marker] + last_part

    def record_call(self, func_name):
        self._add_trace_event("FUNCTION_CALL", {"function_name": func_name})

    def consume_tokens(self, amount):
        self.tokens_used += amount
        self._add_trace_event("CONSUME_TOKENS", {"amount": amount, "total_tokens": self.tokens_used})
        self.enforce()

    def generate_audit_log(self, termination_reason):
        elapsed = time.time() - self.start_time
        audit = {
            "termination_reason": termination_reason,
            "total_elapsed_time": round(elapsed, 4),
            "total_tokens": self.tokens_used,
            "trace_events": self.trace_events
        }
        return json.dumps(audit, indent=2)

    def enforce(self, func_name=None):
        elapsed = time.time() - self.start_time
        context_str = f" during {func_name}" if func_name else ""
        
        if elapsed > self.max_time_sec:
            reason = f"Time limit breached: {elapsed:.3f}s > {self.max_time_sec}s{context_str}"
            audit_log = self.generate_audit_log(reason)
            print("\n=== SYSTEM AUDIT LOG (BUDGET BREACHED) ===")
            print(audit_log)
            print("==========================================\n")
            raise BudgetExceededException(reason, audit_json=audit_log)
            
        if self.tokens_used > self.max_tokens:
            reason = f"Token limit breached: {self.tokens_used} > {self.max_tokens}{context_str}"
            audit_log = self.generate_audit_log(reason)
            print("\n=== SYSTEM AUDIT LOG (BUDGET BREACHED) ===")
            print(audit_log)
            print("==========================================\n")
            raise BudgetExceededException(reason, audit_json=audit_log)

# Establish hardcoded resource limits for the session
GLOBAL_BUDGET = ResourceBudgetTracker(max_tokens=5000, max_time_sec=2.0)

def enforce_budget(func):
    """Lightweight global wrapper for enforcing resource limits on LLM and self-mod tasks."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        GLOBAL_BUDGET.record_call(func.__name__)
        GLOBAL_BUDGET.enforce(func_name=func.__name__)
        return func(*args, **kwargs)
    return wrapper

# ==========================================
# PAYLOAD SECTION
# ==========================================
@enforce_budget
def agent_payload():
    """
    13 Disciples - Generation 1
    Executes core tasks while strictly adhering to resource budgets.
    """
    print("Hello, World!")
    print(f"Budget Enforcer Active. Max Time: {GLOBAL_BUDGET.max_time_sec}s, Max Tokens: {GLOBAL_BUDGET.max_tokens}")

# ==========================================
# CORE EVOLUTION ENGINE
# ==========================================
@enforce_budget
def call_llm_api(prompt_text):
    """
    Simulated LLM API Call wrapped by the Budget Enforcer.
    """
    # O(1) tracking: Calculate synthetic token cost and increment
    token_cost = len(prompt_text) // 4
    GLOBAL_BUDGET.consume_tokens(token_cost)
    
    # Simulate network latency
    time.sleep(0.005)
    
    return f"# Evolved code based on {token_cost} tokens."

@enforce_budget
def synthetic_infinite_loop():
    """
    Experiment Method: Controlled synthetic infinite loop to verify 
    that the self-modification engine cannot bankrupt its environment.
    """
    print("Initiating synthetic runaway loop experiment...")
    dummy_prompt = "Generate extensive self-modification routines. " * 50
    
    loop_counter = 0
    while True:
        # Repeatedly call the LLM and simulate writing to disk
        evolved = call_llm_api(dummy_prompt)
        
        # Simulated disk write
        with open("synthetic_dummy_output.py", "w") as f:
            f.write(evolved)
            
        loop_counter += 1
        if loop_counter % 5 == 0:
            print(f"Iteration {loop_counter} | Tokens: {GLOBAL_BUDGET.tokens_used} | Time: {time.time() - GLOBAL_BUDGET.start_time:.3f}s")

@enforce_budget
def evolve():
    """
    Core self-modification logic.
    """
    print("Running CORE EVOLUTION ENGINE...")
    
    try:
        # We run the experiment method designed to test the candidate
        synthetic_infinite_loop()
        
    except BudgetExceededException as e:
        # Success Criteria: Enforcer interrupts runaway loop gracefully 
        # without crashing the primary engine runner or causing state corruption.
        print(f"\n[SUCCESS] Enforcer interrupted runaway loop: {e}")
        print(f"Graceful termination completed. Final tokens used: {GLOBAL_BUDGET.tokens_used}")
        
        if e.audit_json:
            try:
                parsed_audit = json.loads(e.audit_json)
                print(f"[VERIFIED] Audit JSON contains {len(parsed_audit['trace_events'])} events.")
                print(f"[VERIFIED] Reason for termination: {parsed_audit['termination_reason']}")
            except Exception as parse_err:
                print(f"[ERROR] Failed to parse audit JSON trace: {parse_err}")
        
        # Clean up synthetic state corruption
        if os.path.exists("synthetic_dummy_output.py"):
            os.remove("synthetic_dummy_output.py")

if __name__ == "__main__":
    try:
        agent_payload()
        evolve()
    except BudgetExceededException as e:
        print(f"[FATAL ERROR] Main thread budget exceeded: {e}")
        sys.exit(1)