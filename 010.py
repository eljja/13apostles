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
# PRIME ENGINE UTILITIES (PrimeOrganism-0)
# ==========================================

# First 168 primes (all primes under 1000)
SMALL_PRIMES = (
    2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 
    103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 
    211, 223, 227, 229, 233, 239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293, 307, 311, 313, 317, 
    331, 337, 347, 349, 353, 359, 367, 373, 379, 383, 389, 397, 401, 409, 419, 421, 431, 433, 439, 443, 
    449, 457, 461, 463, 467, 479, 487, 491, 499, 503, 509, 521, 523, 541, 547, 557, 563, 569, 571, 577, 
    587, 593, 599, 601, 607, 613, 617, 619, 631, 641, 643, 647, 653, 659, 661, 673, 677, 683, 691, 701, 
    709, 719, 727, 733, 739, 743, 751, 757, 761, 769, 773, 787, 797, 809, 811, 821, 823, 827, 829, 839, 
    853, 857, 859, 863, 877, 881, 883, 887, 907, 911, 919, 929, 937, 941, 947, 953, 967, 971, 977, 983, 
    991, 997
)

@enforce_budget
def is_prime_candidate(n):
    """
    Highly optimized primality test.
    1. Pre-filter with 168 small primes.
    2. Adaptive Miller-Rabin rounds based on bit-length.
    """
    if n < 2: return False
    # Sieve Pre-filtering
    for p in SMALL_PRIMES:
        if n % p == 0:
            return n == p
    
    # Adaptive Miller-Rabin Rounds
    bit_len = n.bit_length()
    if bit_len <= 256:
        k = 2
    elif bit_len <= 1024:
        k = 3
    else:
        k = 4
    
    # Miller-Rabin Algorithm
    d = n - 1
    r = 0
    while d % 2 == 0:
        d //= 2
        r += 1
    
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

# ==========================================
# PAYLOAD SECTION
# ==========================================
@enforce_budget
def agent_payload():
    """
    PrimeOrganism-0 Discovery Engine
    Implements Dynamic Exponential Bit-Growth and Adaptive Scaling.
    """
    print(f"PrimeOrganism-0 Engine Active. Budget: {GLOBAL_BUDGET.max_time_sec}s")
    
    current_bits = 16
    best_bits = 0
    attempts = 0
    primes_found = 0
    
    start_time = time.time()
    
    try:
        while True:
            attempts += 1
            # Generate random candidate (odd)
            candidate = random.getrandbits(current_bits) | 1 | (1 << (current_bits - 1))
            
            if is_prime_candidate(candidate):
                primes_found += 1
                best_bits = max(best_bits, current_bits)
                
                # Dynamic Exponential Bit-Growth
                elapsed = time.time() - start_time
                remaining_ratio = (GLOBAL_BUDGET.max_time_sec - elapsed) / GLOBAL_BUDGET.max_time_sec
                
                # Consume tokens for each discovery to monitor budget
                GLOBAL_BUDGET.consume_tokens(10)
                
                if remaining_ratio > 0.30:
                    # Healthy budget: Double bit-size
                    current_bits *= 2
                    # Cap to avoid extreme latency in a single MR test if bits get too large
                    if current_bits > 8192:
                        current_bits = 8192
                
                print(f"Prime Found: {current_bits} bits | Total Found: {primes_found} | Elapsed: {elapsed:.3f}s")

            # Check budget every 100 attempts for efficiency
            if attempts % 100 == 0:
                GLOBAL_BUDGET.enforce()
                
    except BudgetExceededException as e:
        elapsed_final = time.time() - start_time
        print(f"\n[TERMINATION] {e}")
        
        # Success Criteria Calculation
        if attempts > 0 and elapsed_final > 0:
            throughput = attempts / elapsed_final
            fitness = best_bits / (attempts * elapsed_final)
            print(f"--- Performance Report ---")
            print(f"Max Bit Size: {best_bits}")
            print(f"Total Attempts: {attempts}")
            print(f"Throughput: {throughput:.2f} attempts/sec")
            print(f"Fitness Score: {fitness:.6f}")
            
            if best_bits >= 1024:
                print("Criterion 1 Met: Found >= 1024-bit prime.")
            if throughput > 5000:
                print("Criterion 2 Met: Throughput > 5000 attempts/sec.")
        
        return best_bits

# ==========================================
# CORE EVOLUTION ENGINE
# ==========================================
@enforce_budget
def evolve():
    """
    Triggers the discovery engine and handles lifecycle.
    """
    print("Running CORE EVOLUTION ENGINE...")
    try:
        agent_payload()
    except Exception as e:
        if not isinstance(e, BudgetExceededException):
            print(f"Unexpected Error: {e}")
        else:
            print("Evolution cycle completed by budget constraint.")

if __name__ == "__main__":
    try:
        evolve()
    except BudgetExceededException as e:
        print(f"[FATAL] Budget logic interrupted main execution: {e}")
        sys.exit(0)
    except KeyboardInterrupt:
        sys.exit(0)