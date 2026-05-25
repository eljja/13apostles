import os
import sys
import time
import random
import math
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

# Global state tracker instance
EXECUTION_STATE = ExecutionState()

# ==========================================
# STATIC IMMUTABLE MASTER PRIMES & DERIVATIVES
# ==========================================
MASTER_PRIMES = (
    2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97,
    101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193,
    197, 199, 211, 223, 227, 229, 233, 239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293, 307,
    311, 313, 317, 331, 337, 347, 349, 353, 359, 367
)

SMALL_PRIME_SET = frozenset(MASTER_PRIMES)

# Product of all odd primes in MASTER_PRIMES
GCD_FILTER_PRODUCT = 1
for p in MASTER_PRIMES:
    if p != 2:
        GCD_FILTER_PRODUCT *= p

# ==========================================
# PAYLOAD: PrimeOrganism-0 Search Engine
# ==========================================
def is_probable_prime(n, k=5):
    """
    Miller-Rabin primality test with adaptive rounds, C-native pre-filtering, and embedded temporal checks.
    """
    # Deterministic Range Guard
    if n <= 367:
        return n in SMALL_PRIME_SET
    
    # Pre-filtering: Even numbers and C-native GCD pre-filter
    if n % 2 == 0:
        return False
    if math.gcd(n, GCD_FILTER_PRODUCT) != 1:
        return False

    # Write n-1 as d * 2^s
    s = 0
    d = n - 1
    while d % 2 == 0:
        s += 1
        d //= 2

    # Witness loop
    for _ in range(k):
        # Cooperatively enforce budget inside witness evaluation
        GLOBAL_BUDGET.enforce()
        a = random.randint(2, n - 2)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(s - 1):
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
            else:
                # Double the target bit-size upon successful discovery
                bit_size *= 2

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
            
        print(f"Final Execution Stats: Tokens used = {GLOBAL_BUDGET.tokens_used}, Elapsed = {time.time() - GLOBAL_BUDGET.start_time:.3f}s")
        sys.exit(0)
    except Exception as e:
        print(f"[FATAL ERROR] Unexpected process termination: {e}")
        sys.exit(1)