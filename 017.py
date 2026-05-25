import os
import sys
import time
from functools import wraps

# ==========================================
# FEATURE: Global Execution and Token Budget
# ==========================================
class BudgetExceededException(Exception):
    """Raised when execution time or token limits are breached."""
    pass

class ResourceBudgetTracker:
    def __init__(self, max_tokens=10000, max_time_sec=5.0):
        self.max_tokens = max_tokens
        self.max_time_sec = max_time_sec
        self.tokens_used = 0
        self.start_time = time.time()

    def consume_tokens(self, amount):
        self.tokens_used += amount
        self.enforce()

    def enforce(self):
        elapsed = time.time() - self.start_time
        if elapsed > self.max_time_sec:
            raise BudgetExceededException(f"Time limit breached: {elapsed:.3f}s > {self.max_time_sec}s")
        if self.tokens_used > self.max_tokens:
            raise BudgetExceededException(f"Token limit breached: {self.tokens_used} > {self.max_tokens}")

# Establish hardcoded resource limits for the session
GLOBAL_BUDGET = ResourceBudgetTracker(max_tokens=5000, max_time_sec=2.0)

def enforce_budget(func):
    """Lightweight global wrapper for enforcing resource limits on LLM and self-mod tasks."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        GLOBAL_BUDGET.enforce()
        return func(*args, **kwargs)
    return wrapper

# ==========================================
# SANITIZED WORKSPACE UTILITY
# ==========================================
SAFE_WORKSPACE = os.path.abspath("safe_workspace")

def validate_and_resolve_path(filename, workspace_dir=SAFE_WORKSPACE):
    """
    Validates that a path is securely within the designated safe workspace.
    Prevents directory traversal attacks.
    """
    os.makedirs(workspace_dir, exist_ok=True)
    workspace_abs = os.path.abspath(workspace_dir)
    target_abs = os.path.abspath(os.path.join(workspace_abs, filename))
    
    # Enforce path containment using commonpath to prevent partial name matching bypasses
    try:
        common = os.path.commonpath([workspace_abs, target_abs])
        if common != workspace_abs:
            raise PermissionError(f"Security Violation: Path traversal detected. Access denied to target: {filename}")
    except ValueError:
        raise PermissionError(f"Security Violation: Invalid or malicious path target: {filename}")
        
    return target_abs

def safe_write(filename, content):
    """
    Writes content to a file safely nested within the authorized workspace.
    """
    target_path = validate_and_resolve_path(filename)
    with open(target_path, "w") as f:
        f.write(content)
    return target_path

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
        # Repeatedly call the LLM and simulate writing to disk safely
        evolved = call_llm_api(dummy_prompt)
        
        # Protected disk write utilizing safe path-sanitization
        safe_write("synthetic_dummy_output.py", evolved)
            
        loop_counter += 1
        if loop_counter % 5 == 0:
            print(f"Iteration {loop_counter} | Tokens: {GLOBAL_BUDGET.tokens_used} | Time: {time.time() - GLOBAL_BUDGET.start_time:.3f}s")

@enforce_budget
def evolve():
    """
    Core self-modification logic with resilient cleanup and security validation.
    """
    print("Running CORE EVOLUTION ENGINE...")
    
    try:
        # 1. Security Test: Programmatically attempt out-of-bounds write
        print("\n[SECURITY TEST] Testing path-traversal resilience...")
        try:
            safe_write("../unauthorized_payload.py", "malicious_code = True")
            print("[FAILURE] Security Test failed! Unauthorized write allowed.")
        except PermissionError as e:
            print(f"[SUCCESS] Security Test blocked out-of-bounds write: {e}")
            
        # 2. Execute runaway loop experiment
        synthetic_infinite_loop()
        
    except BudgetExceededException as e:
        # Success Criteria: Enforcer interrupts runaway loop gracefully 
        # without crashing the primary engine runner or causing state corruption.
        print(f"\n[SUCCESS] Enforcer interrupted runaway loop: {e}")
        print(f"Graceful termination completed. Final tokens used: {GLOBAL_BUDGET.tokens_used}")
    finally:
        # Exception-Resilient Cleanup of workspace contents
        print("Executing cleanup pipeline...")
        try:
            target_path = validate_and_resolve_path("synthetic_dummy_output.py")
            if os.path.exists(target_path):
                os.remove(target_path)
                print(f"[SUCCESS] Cleaned up temporary file: {target_path}")
        except Exception as cleanup_err:
            print(f"[ERROR] Clean up sequence failed: {cleanup_err}")

        # Attempt to prune empty safe_workspace directory
        try:
            if os.path.exists(SAFE_WORKSPACE) and not os.listdir(SAFE_WORKSPACE):
                os.rmdir(SAFE_WORKSPACE)
        except Exception:
            pass

if __name__ == "__main__":
    try:
        agent_payload()
        evolve()
    except BudgetExceededException as e:
        print(f"[FATAL ERROR] Main thread budget exceeded: {e}")
        sys.exit(1)