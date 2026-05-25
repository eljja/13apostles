# Summary of reasoning: 
# The program is updated to incorporate the SEST-SDP diagnostic framework by adding telemetry counters and a scaling log to `ExecutionState`.
# We instrument `is_probable_prime` to record sieve discards and Miller-Rabin loops, track transitions in `search_primes`, and print a structured post-mortem JSON audit block at termination.

import os
import sys
import time
import random
import json
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

# Establish resource limits (5.0s per target budget constraint)
GLOBAL_BUDGET = ResourceBudgetTracker(max_tokens=5000, max_time_sec=5.0)

def enforce_budget(func):
    """Lightweight global wrapper for enforcing resource limits on LLM and self-mod tasks."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        GLOBAL_BUDGET.enforce()
        return func(*args, **kwargs)
    return wrapper

# ==========================================
# FEATURE: Persistent State Registry
# ==========================================
class ExecutionState:
    def __init__(self):
        self.best_prime = None
        self.bit_size = 0
        self.total_attempts = 0
        self.elapsed_time_at_discovery = 0.0
        # SEST-SDP Extended Telemetry
        self.sieve_discards = 0
        self.mr_evaluations = 0
        self.mr_witness_loops = 0
        self.trajectory_log = []

# Global state tracker instance
EXECUTION_STATE = ExecutionState()

# ==========================================
# STATIC IMMUTABLE SIEVE PRIMES
# ==========================================
SIEVE_PRIMES = (3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113)

# ==========================================
# PAYLOAD: PrimeOrganism-0 Search Engine
# ==========================================
def is_probable_prime(n, k=5):
    """
    Miller-Rabin primality test with adaptive rounds, sieve pre-filtering, and embedded temporal checks.
    """
    # Deterministic Range Guard
    if n <= 113:
        is_p = n in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113)
        if not is_p:
            EXECUTION_STATE.sieve_discards += 1
        return is_p
    
    # Pre-filtering: Even numbers and sieve prime divisibility
    if n % 2 == 0:
        EXECUTION_STATE.sieve_discards += 1
        return False
    for p in SIEVE_PRIMES:
        if n % p == 0:
            EXECUTION_STATE.sieve_discards += 1
            return False

    EXECUTION_STATE.mr_evaluations += 1

    # Write n-1 as d * 2^s
    s = 0
    d = n - 1
    while d % 2 == 0:
        s += 1
        d //= 2

    # Witness loop
    for _ in range(k):
        EXECUTION_STATE.mr_witness_loops += 1
        # Cooperatively enforce budget inside witness evaluation
        GLOBAL_BUDGET.enforce()
        a = random.randint(2, n - 2)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(s - 1):
            EXECUTION_STATE.mr_witness_loops += 1
            # Cooperatively enforce budget inside deep exponentiation loops
            GLOBAL_BUDGET.enforce()
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True

def search_primes():
    """
    Core search loop that scales candidate bit-sizes dynamically and
    evaluates fitness with division-by-zero safeguards.
    """
    bit_size = 16
    start_time = time.time()
    total_attempts = 0
    attempts_at_current_level = 0
    
    print("Initiating PrimeOrganism-0 Search Engine...")
    while True:
        # Cooperatively enforce budget inside generator loop
        GLOBAL_BUDGET.enforce()
        
        # Generate random odd integer of bit_size
        lower = (1 << (bit_size - 1)) | 1
        upper = (1 << bit_size) - 1
        candidate = random.randint(lower, upper)
        candidate |= 1  # Ensure odd
        
        total_attempts += 1
        attempts_at_current_level += 1
        EXECUTION_STATE.total_attempts = total_attempts
        
        if is_probable_prime(candidate, k=5):
            elapsed_time = time.time() - start_time
            # Division-by-zero protection in fitness calculation
            safe_attempts = max(total_attempts, 1)
            safe_elapsed = max(elapsed_time, 0.001)
            fitness = bit_size / (safe_attempts * safe_elapsed)
            
            print(f"[FOUND] {bit_size}-bit Prime: {candidate}")
            print(f"        Elapsed: {elapsed_time:.4f}s | Fitness: {fitness:.6f}")
            
            # Persist successful state immediately to shield against stack unwinding data loss
            EXECUTION_STATE.best_prime = candidate
            EXECUTION_STATE.bit_size = bit_size
            EXECUTION_STATE.elapsed_time_at_discovery = elapsed_time
            
            # TEMPORAL SCALING GUARD:
            # Estimate if the remaining time budget is sufficient for the next step.
            # If remaining time is less than 15% of total budget, freeze bit-size scaling.
            remaining_time = GLOBAL_BUDGET.max_time_sec - (time.time() - GLOBAL_BUDGET.start_time)
            time_threshold = 0.15 * GLOBAL_BUDGET.max_time_sec
            
            if remaining_time < time_threshold:
                print(f"[GUARD] Remaining time ({remaining_time:.3f}s) < threshold ({time_threshold:.3f}s). Freezing bit-size scaling at {bit_size} bits.")
                EXECUTION_STATE.trajectory_log.append({
                    "event": "scaling_frozen",
                    "bit_size": bit_size,
                    "attempts_at_level": attempts_at_current_level,
                    "elapsed_time": elapsed_time
                })
            else:
                # Double the target bit-size upon successful discovery
                old_bit_size = bit_size
                bit_size *= 2
                EXECUTION_STATE.trajectory_log.append({
                    "event": "scale_up",
                    "from_bit_size": old_bit_size,
                    "to_bit_size": bit_size,
                    "attempts_at_level": attempts_at_current_level,
                    "elapsed_time": elapsed_time
                })
                attempts_at_current_level = 0

@enforce_budget
def agent_payload():
    """
    PrimeOrganism-0 Payload Execution
    """
    print(f"Budget Enforcer Active. Max Time: {GLOBAL_BUDGET.max_time_sec}s, Max Tokens: {GLOBAL_BUDGET.max_tokens}")
    search_primes()

# ==========================================
# CORE EVOLUTION ENGINE
# ==========================================
@enforce_budget
def call_llm_api(prompt_text):
    """
    Simulated LLM API Call wrapped by the Budget Enforcer.
    """
    token_cost = len(prompt_text) // 4
    GLOBAL_BUDGET.consume_tokens(token_cost)
    time.sleep(0.005)
    return f"# Evolved code based on {token_cost} tokens."

@enforce_budget
def evolve():
    """
    Placeholder for self-modification logic.
    """
    print("Running CORE EVOLUTION ENGINE...")
    # Triggering the core search payload under evolution supervision
    agent_payload()

if __name__ == "__main__":
    try:
        # Launch the defensive temporal-guarded payload
        agent_payload()
    except BudgetExceededException as e:
        # Success Criteria: Enforcer interrupts runaway loops gracefully
        print(f"\n[SUCCESS] Enforcer gracefully interrupted execution: {e}")
        
        # Post-Mortem Recovery Handler
        if EXECUTION_STATE.best_prime is not None:
            # Recover the best prime metadata safely from state registry
            safe_attempts = max(EXECUTION_STATE.total_attempts, 1)
            safe_elapsed = max(EXECUTION_STATE.elapsed_time_at_discovery, 0.001)
            recovered_fitness = EXECUTION_STATE.bit_size / (safe_attempts * safe_elapsed)
            print("--- POST-MORTEM STATE RECOVERY SUCCESSFUL ---")
            print(f"Discovered Prime : {EXECUTION_STATE.best_prime}")
            print(f"Prime Bit-Size   : {EXECUTION_STATE.bit_size}")
            print(f"Discovery Time   : {EXECUTION_STATE.elapsed_time_at_discovery:.4f}s")
            print(f"Final Fitness    : {recovered_fitness:.6f}")
            print(f"Total Attempts   : {EXECUTION_STATE.total_attempts}")
            print("---------------------------------------------")
        else:
            print("\n--- POST-MORTEM RECOVERY: No primes were discovered before interruption. ---")
            
        # Auditable Post-Mortem SEST-SDP Report
        try:
            total_sieve_attempts = EXECUTION_STATE.sieve_discards + EXECUTION_STATE.mr_evaluations
            sieve_efficiency = (EXECUTION_STATE.sieve_discards / total_sieve_attempts * 100.0) if total_sieve_attempts > 0 else 0.0
            compute_attempts_ratio = (EXECUTION_STATE.mr_witness_loops / EXECUTION_STATE.total_attempts) if EXECUTION_STATE.total_attempts > 0 else 0.0
            
            telemetry_report = {
                "sieve_efficiency_pct": round(sieve_efficiency, 2),
                "compute_to_attempts_ratio": round(compute_attempts_ratio, 4),
                "sieve_discards": EXECUTION_STATE.sieve_discards,
                "mr_evaluations": EXECUTION_STATE.mr_evaluations,
                "mr_witness_loops": EXECUTION_STATE.mr_witness_loops,
                "chronological_scaling_path": EXECUTION_STATE.trajectory_log
            }
            
            print("\n--- AUDITABLE SEST-SDP TELEMETRY REPORT (JSON) ---")
            print(json.dumps(telemetry_report, indent=2))
            print("--------------------------------------------------")
        except Exception as audit_err:
            print(f"[ERROR] Telemetry recovery failed to serialize cleanly: {audit_err}")

        print(f"Final Execution Stats: Tokens used = {GLOBAL_BUDGET.tokens_used}, Elapsed = {time.time() - GLOBAL_BUDGET.start_time:.3f}s")
        sys.exit(0)
    except Exception as e:
        print(f"[FATAL ERROR] Unexpected process termination: {e}")
        sys.exit(1)