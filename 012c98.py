import os
import sys
import time
import random
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
# STATE PRESERVATION & CONFIGURATION
# ==========================================
SEARCH_STATE = {
    "best_bits": 0,
    "total_attempts": 0,
    "best_prime": None,
    "elapsed_time": 0.0,
    "sieve_discards": 0,
    "mr_first_witness_discards": 0,
    "mr_deep_witness_discards": 0,
    "successful_primes": 0
}

# Static lookup of the first 30 primes for cheap trial division
SMALL_PRIMES = (
    2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 
    31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 
    73, 79, 83, 89, 97, 101, 103, 107, 109, 113
)

# ==========================================
# PAYLOAD: PrimeOrganism-0 Search Engine (SP-APSE)
# ==========================================
def is_probable_prime(n, k=5):
    """
    Miller-Rabin primality test with trial division pre-sieve, 
    adaptive rounds, and embedded temporal checks.
    """
    # Static lookup / trial division sieve
    if n <= 113:
        if n in SMALL_PRIMES:
            return True
        else:
            SEARCH_STATE["sieve_discards"] += 1
            return False
    for p in SMALL_PRIMES:
        if n % p == 0:
            SEARCH_STATE["sieve_discards"] += 1
            return False

    # Write n-1 as d * 2^s
    s = 0
    d = n - 1
    while d % 2 == 0:
        s += 1
        d //= 2

    # Witness loop
    for i in range(k):
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
            # Witness confirms composite
            if i == 0:
                SEARCH_STATE["mr_first_witness_discards"] += 1
            else:
                SEARCH_STATE["mr_deep_witness_discards"] += 1
            return False
            
    SEARCH_STATE["successful_primes"] += 1
    return True

def search_primes():
    """
    Core search loop that scales candidate bit-sizes dynamically and
    evaluates fitness with division-by-zero safeguards.
    """
    bit_size = 16
    start_time = time.time()
    
    print("Initiating State-Preserved Adaptive Prime Search Engine (SP-APSE)...")
    while True:
        # Cooperatively enforce budget inside generator loop
        GLOBAL_BUDGET.enforce()
        
        # Generate random odd integer of bit_size
        lower = (1 << (bit_size - 1)) | 1
        upper = (1 << bit_size) - 1
        candidate = random.randint(lower, upper)
        candidate |= 1  # Ensure odd
        
        # Track attempts
        SEARCH_STATE["total_attempts"] += 1
        
        # Dynamic witness rounds
        if bit_size <= 256:
            k = 3
        elif bit_size <= 1024:
            k = 4
        else:
            k = 5
        
        if is_probable_prime(candidate, k=k):
            elapsed_time = time.time() - start_time
            # Division-by-zero protection in fitness calculation
            safe_elapsed = max(elapsed_time, 0.001)
            fitness = bit_size / (SEARCH_STATE["total_attempts"] * safe_elapsed)
            
            # Preserve state across temporal boundaries
            SEARCH_STATE["best_bits"] = bit_size
            SEARCH_STATE["best_prime"] = candidate
            SEARCH_STATE["elapsed_time"] = elapsed_time
            
            print(f"[FOUND] {bit_size}-bit Prime: {candidate}")
            print(f"        Elapsed: {elapsed_time:.4f}s | Fitness: {fitness:.6f}")
            
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
        
        # Compute final actual fitness from preserved state
        best_bits = SEARCH_STATE["best_bits"]
        elapsed = SEARCH_STATE["elapsed_time"] if SEARCH_STATE["elapsed_time"] > 0 else (time.time() - GLOBAL_BUDGET.start_time)
        safe_elapsed = max(elapsed, 0.001)
        total_attempts = max(SEARCH_STATE["total_attempts"], 1)
        final_fitness = best_bits / (total_attempts * safe_elapsed)
        
        # Print a structured evaluation log for evolution clean verification
        print("=" * 45)
        print("   STATE-PRESERVED EVALUATION LOG")
        print("=" * 45)
        print(f"Best Bit Size Achieved: {best_bits} bits")
        print(f"Total Sieve & MR Runs : {SEARCH_STATE['total_attempts']}")
        print(f"Final Actual Fitness  : {final_fitness:.6f}")
        print(f"Best Prime Decoded    : {SEARCH_STATE['best_prime']}")
        print(f"Cumulative Time Active: {time.time() - GLOBAL_BUDGET.start_time:.3f}s")
        print(f"Token Budget Status   : {GLOBAL_BUDGET.tokens_used}/{GLOBAL_BUDGET.max_tokens}")
        print("=" * 45)
        
        # Extrapolate telemetry metrics
        sieve_discards = SEARCH_STATE["sieve_discards"]
        mr_first_discards = SEARCH_STATE["mr_first_witness_discards"]
        mr_deep_discards = SEARCH_STATE["mr_deep_witness_discards"]
        successful_primes = SEARCH_STATE["successful_primes"]
        
        sieve_pct = (sieve_discards / total_attempts) * 100
        mr_first_pct = (mr_first_discards / total_attempts) * 100
        mr_deep_pct = (mr_deep_discards / total_attempts) * 100
        success_pct = (successful_primes / total_attempts) * 100
        
        avg_cpu_per_cand = (time.time() - GLOBAL_BUDGET.start_time) / total_attempts
        
        # Conservation equation check
        conservation_sum = sieve_discards + mr_first_discards + mr_deep_discards + successful_primes
        is_conserved = (conservation_sum == total_attempts)
        
        # Structured SET-BP Diagnostic Profiler Output
        print("=" * 45)
        print("     ALGORITHMIC EFFICIENCY PROFILE (SET-BP)")
        print("=" * 45)
        print(f"Sieve Discard Rate         : {sieve_pct:.2f}% ({sieve_discards})")
        print(f"MR First-Witness Discard   : {mr_first_pct:.2f}% ({mr_first_discards})")
        print(f"MR Deep-Witness Discard    : {mr_deep_pct:.2f}% ({mr_deep_discards})")
        print(f"Prime Success Rate         : {success_pct:.2f}% ({successful_primes})")
        print(f"Avg CPU Time Per Candidate : {avg_cpu_per_cand * 1000:.4f} ms")
        print(f"Conservation Equation     : {conservation_sum} / {total_attempts} ({'PASSED' if is_conserved else 'FAILED'})")
        print("=" * 45)
        
        sys.exit(0)
    except Exception as e:
        print(f"[FATAL ERROR] Unexpected process termination: {e}")
        sys.exit(1)