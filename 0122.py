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
# STATE-PRESERVING INTERRUPTION REGISTRY (SPIR)
# ==========================================
class OrganismStateRegistry:
    def __init__(self):
        self.best_prime = None
        self.best_bits = 0
        self.total_attempts = 0
        self.start_time = time.time()

STATE_REGISTRY = OrganismStateRegistry()

# ==========================================
# PAYLOAD: PrimeOrganism-0 Search Engine
# ==========================================
def is_probable_prime(n, k=5):
    """
    Miller-Rabin primality test with adaptive rounds and embedded temporal checks.
    """
    # Explicit boundary guards
    if n <= 4:
        return n in (2, 3)
    if n % 2 == 0:
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
    STATE_REGISTRY.start_time = time.time()
    STATE_REGISTRY.best_bits = 0
    STATE_REGISTRY.best_prime = None
    STATE_REGISTRY.total_attempts = 0
    
    print("Initiating PrimeOrganism-0 Search Engine...")
    while True:
        # Cooperatively enforce budget inside generator loop
        GLOBAL_BUDGET.enforce()
        
        # Generate random odd integer of bit_size
        lower = (1 << (bit_size - 1)) | 1
        upper = (1 << bit_size) - 1
        candidate = random.randint(lower, upper)
        candidate |= 1  # Ensure odd
        
        # Track total evaluation attempts atomically
        STATE_REGISTRY.total_attempts += 1
        
        if is_probable_prime(candidate, k=5):
            elapsed_time = time.time() - STATE_REGISTRY.start_time
            # Division-by-zero protection in fitness calculation
            safe_elapsed = max(elapsed_time, 0.001)
            fitness = bit_size / safe_elapsed
            
            # Record state atomically
            STATE_REGISTRY.best_prime = candidate
            STATE_REGISTRY.best_bits = bit_size
            
            print(f"[FOUND] {bit_size}-bit Prime: {candidate}")
            print(f"        Elapsed: {elapsed_time:.4f}s | Fitness (bits/sec): {fitness:.2f}")
            
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
        
        # Process and output the post-mortem telemetry log using State-Preserving Interruption Registry (SPIR)
        elapsed_time = time.time() - STATE_REGISTRY.start_time
        safe_elapsed = max(elapsed_time, 0.001)
        best_bits = STATE_REGISTRY.best_bits
        best_prime = STATE_REGISTRY.best_prime
        total_attempts = STATE_REGISTRY.total_attempts
        fitness = best_bits / safe_elapsed if best_bits > 0 else 0.0
        
        print("==========================================")
        print("POST-MORTEM TELEMETRY LOG")
        print("==========================================")
        print(f"Status: INTERRUPTED (Budget Exceeded)")
        print(f"Total Attempted Candidates: {total_attempts}")
        print(f"Highest Verified Prime:     {best_prime if best_prime is not None else 'None'}")
        print(f"Highest Bit-Size Discovered: {best_bits}-bit")
        print(f"Final Fitness (bits/sec):   {fitness:.4f}")
        print(f"Budget Tracker Tokens Used: {GLOBAL_BUDGET.tokens_used}")
        print(f"Actual Elapsed Search Time: {elapsed_time:.4f}s")
        print("==========================================")
        sys.exit(0)
    except Exception as e:
        print(f"[FATAL ERROR] Unexpected process termination: {e}")
        sys.exit(1)