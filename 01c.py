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
# MATHEMATICAL UTILITIES
# ==========================================
def is_prime_mr(n, k=5):
    """
    Miller-Rabin Primality Test.
    Returns True if n is probably prime, False if n is definitely composite.
    """
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False

    # Write n-1 as 2^r * d
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2

    for _ in range(k):
        a = random.randint(2, n - 2)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True

def generate_candidate(bits):
    """Generates an odd random integer of exactly the specified bit-width."""
    return random.randrange(2**(bits-1) + 1, 2**bits, 2)

# ==========================================
# PAYLOAD SECTION
# ==========================================
@enforce_budget
def agent_payload():
    """
    PrimeOrganism-0: Unified Domain Integration
    Executes a sequential prime-searching loop that starts at 16-bit candidates,
    doubles the bit size upon finding a prime, and tracks metrics.
    """
    print("Starting PrimeOrganism-0 search engine...")
    bit_size = 16
    total_attempts = 0
    best_bits = 0
    best_prime = None
    payload_start = time.time()

    try:
        while True:
            # Graceful proactive exit checking to avoid hard crashing just before the 2.0s limit
            elapsed = time.time() - GLOBAL_BUDGET.start_time
            if elapsed >= GLOBAL_BUDGET.max_time_sec - 0.05:
                print("Budget limit imminent. Gracefully halting search loop.")
                break

            GLOBAL_BUDGET.enforce()

            candidate = generate_candidate(bit_size)
            total_attempts += 1
            GLOBAL_BUDGET.consume_tokens(1)  # Consume 1 token per primality test attempt

            if is_prime_mr(candidate):
                best_bits = bit_size
                best_prime = candidate
                print(f"Found {bit_size}-bit prime: {candidate}")
                bit_size *= 2  # Double bit-width upon success

    except BudgetExceededException as e:
        print(f"Budget exceeded during search: {e}")

    # Calculate and output fitness
    elapsed_time = max(time.time() - payload_start, 0.001)
    fitness = best_bits / (total_attempts * elapsed_time) if total_attempts > 0 else 0.0

    print("\n--- Payload Execution Summary ---")
    print(f"Best prime found: {best_prime} ({best_bits} bits)")
    print(f"Total attempts: {total_attempts}")
    print(f"Elapsed time: {elapsed_time:.3f}s")
    print(f"Fitness (best_bits / (attempts * time)): {fitness:.6f}")
    print("---------------------------------\n")

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
def synthetic_infinite_loop():
    """
    Experiment Method: Controlled synthetic infinite loop to verify 
    that the self-modification engine cannot bankrupt its environment.
    """
    print("Initiating synthetic runaway loop experiment...")
    dummy_prompt = "Generate extensive self-modification routines. " * 50
    
    loop_counter = 0
    while True:
        evolved = call_llm_api(dummy_prompt)
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
        synthetic_infinite_loop()
    except BudgetExceededException as e:
        print(f"\n[SUCCESS] Enforcer interrupted runaway loop: {e}")
        print(f"Graceful termination completed. Final tokens used: {GLOBAL_BUDGET.tokens_used}")
        if os.path.exists("synthetic_dummy_output.py"):
            os.remove("synthetic_dummy_output.py")

if __name__ == "__main__":
    try:
        agent_payload()
        evolve()
    except BudgetExceededException as e:
        print(f"[INFO] Main thread budget reached: {e}")
        sys.exit(0)