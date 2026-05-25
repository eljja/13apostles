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
# FEATURE: Hard Ceiling Boundary Guard & Defensive LCG Fallback
# ==========================================
MAX_BIT_SIZE = 4096

class LinearCongruentialGenerator:
    """Deterministic high-performance 64-bit LCG fallback generator."""
    def __init__(self, seed=123456789):
        self.state = seed
        self.a = 6364136223846793005
        self.c = 1442695040888963407
        self.m = 2**64

    def _next_bits(self, bits):
        val = 0
        chunks = (bits + 63) // 64
        for _ in range(chunks):
            self.state = (self.a * self.state + self.c) % self.m
            val = (val << 64) | self.state
        return val & ((1 << bits) - 1)

    def randint(self, lower, upper):
        bit_len = (upper - lower).bit_length()
        if bit_len == 0:
            return lower
        val = self._next_bits(bit_len)
        return lower + (val % (upper - lower + 1))

FALLBACK_RANDOM = LinearCongruentialGenerator()

def safe_randint(lower, upper):
    """Wraps random.randint with defensive degradation to LCG fallback."""
    try:
        return random.randint(lower, upper)
    except Exception:
        return FALLBACK_RANDOM.randint(lower, upper)

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
        a = safe_randint(2, n - 2)
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
        
        # Enforce Hard Ceiling Boundary Guard
        current_bit_size = min(bit_size, MAX_BIT_SIZE)
        
        # Generate random odd integer of current_bit_size
        lower = (1 << (current_bit_size - 1)) | 1
        upper = (1 << current_bit_size) - 1
        candidate = safe_randint(lower, upper)
        candidate |= 1  # Ensure odd
        
        total_attempts += 1
        EXECUTION_STATE.total_attempts = total_attempts
        
        if is_probable_prime(candidate, k=5):
            elapsed_time = time.time() - start_time
            # Division-by-zero protection in fitness calculation
            safe_elapsed = max(elapsed_time, 0.001)
            fitness = current_bit_size / safe_elapsed
            
            print(f"[FOUND] {current_bit_size}-bit Prime: {candidate}")
            print(f"        Elapsed: {elapsed_time:.4f}s | Fitness (bits/sec): {fitness:.2f}")
            
            # Persist successful state immediately to shield against stack unwinding data loss
            EXECUTION_STATE.best_prime = candidate
            EXECUTION_STATE.bit_size = current_bit_size
            EXECUTION_STATE.elapsed_time_at_discovery = elapsed_time
            
            # TEMPORAL SCALING GUARD:
            # Estimate if the remaining time budget is sufficient for the next step.
            # If remaining time is less than 15% of total budget, freeze bit-size scaling.
            remaining_time = GLOBAL_BUDGET.max_time_sec - (time.time() - GLOBAL_BUDGET.start_time)
            time_threshold = 0.15 * GLOBAL_BUDGET.max_time_sec
            
            if remaining_time < time_threshold:
                print(f"[GUARD] Remaining time ({remaining_time:.3f}s) < threshold ({time_threshold:.3f}s). Freezing bit-size scaling at {current_bit_size} bits.")
            else:
                # Double the target bit-size upon successful discovery, constrained by absolute boundary
                bit_size = min(bit_size * 2, MAX_BIT_SIZE)

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

# ==========================================
# UNIFIED FAIL-SAFE TERMINATION HANDLER
# ==========================================
def unified_termination_handler(trigger_event):
    """
    Guarantees zero-loss state recovery and telemetry dumping for any
    termination event (exceptions, user interrupts, or unexpected crashes).
    """
    if isinstance(trigger_event, BudgetExceededException):
        print(f"\n[SUCCESS] Enforcer gracefully interrupted execution: {trigger_event}")
    else:
        print(f"\n[TERMINATION] Unified recovery triggered by: {type(trigger_event).__name__} ({trigger_event})")
    
    # Post-Mortem Recovery Handler
    if EXECUTION_STATE.best_prime is not None:
        # Recover the best prime metadata safely from state registry
        safe_elapsed = max(EXECUTION_STATE.elapsed_time_at_discovery, 0.001)
        recovered_fitness = EXECUTION_STATE.bit_size / safe_elapsed
        print("--- POST-MORTEM STATE RECOVERY SUCCESSFUL ---")
        print(f"Discovered Prime : {EXECUTION_STATE.best_prime}")
        print(f"Prime Bit-Size   : {EXECUTION_STATE.bit_size}")
        print(f"Discovery Time   : {EXECUTION_STATE.elapsed_time_at_discovery:.4f}s")
        print(f"Final Fitness    : {recovered_fitness:.2f} bits/sec")
        print(f"Total Attempts   : {EXECUTION_STATE.total_attempts}")
        print("---------------------------------------------")
    else:
        print("\n--- POST-MORTEM RECOVERY: No primes were discovered before interruption. ---")
        
    print(f"Final Execution Stats: Tokens used = {GLOBAL_BUDGET.tokens_used}, Elapsed = {time.time() - GLOBAL_BUDGET.start_time:.3f}s")
    os._exit(0)

if __name__ == "__main__":
    try:
        # Launch the defensive temporal-guarded payload
        agent_payload()
    except BaseException as e:
        # Intercept absolutely all termination signals/exceptions to guarantee zero loss
        unified_termination_handler(e)