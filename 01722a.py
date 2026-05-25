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
    def __init__(self, max_tokens=10000, max_time_sec=1.0):
        self.max_tokens = max_tokens
        self.max_time_sec = max_time_sec
        self.tokens_used = 0
        self.start_time = time.monotonic()

    def consume_tokens(self, amount):
        self.tokens_used += max(0, int(amount))
        self.enforce()

    def enforce(self):
        elapsed = time.monotonic() - self.start_time
        elapsed = max(0.0, elapsed)
        if elapsed > self.max_time_sec:
            raise BudgetExceededException(f"Time limit breached: {elapsed:.3f}s > {self.max_time_sec}s")
        if self.tokens_used > self.max_tokens:
            raise BudgetExceededException(f"Token limit breached: {self.tokens_used} > {self.max_tokens}")

GLOBAL_BUDGET = ResourceBudgetTracker(max_tokens=10000, max_time_sec=1.0)

def enforce_budget(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        GLOBAL_BUDGET.enforce()
        return func(*args, **kwargs)
    return wrapper

# ==========================================
# STATIC SIEVE DATA (168 primes under 1000)
# ==========================================
PRIMES_UNDER_1000 = (
    2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97,
    101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199,
    211, 223, 227, 229, 233, 239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293, 307, 311, 313, 317, 331,
    337, 347, 349, 353, 359, 367, 373, 379, 383, 389, 397, 401, 409, 419, 421, 431, 433, 439, 443, 449, 457,
    461, 463, 467, 479, 487, 491, 499, 503, 509, 521, 523, 541, 547, 557, 563, 569, 571, 577, 587, 593, 599,
    601, 607, 613, 617, 619, 631, 641, 643, 647, 653, 659, 661, 673, 677, 683, 691, 701, 709, 719, 727, 733,
    739, 743, 751, 757, 761, 769, 773, 787, 797, 809, 811, 821, 823, 827, 829, 839, 853, 857, 859, 863, 877,
    881, 883, 887, 907, 911, 919, 929, 937, 941, 947, 953, 967, 971, 977, 983, 991, 997
)

# ==========================================
# SANITIZED WORKSPACE UTILITY
# ==========================================
SAFE_WORKSPACE = os.path.abspath("safe_workspace")

def validate_and_resolve_path(filename, workspace_dir=SAFE_WORKSPACE):
    os.makedirs(workspace_dir, exist_ok=True)
    workspace_abs = os.path.abspath(workspace_dir)
    target_abs = os.path.abspath(os.path.join(workspace_abs, filename))
    if os.path.commonpath([workspace_abs, target_abs]) != workspace_abs:
        raise PermissionError(f"Security Violation: {filename}")
    return target_abs

def safe_write_json(filename, data):
    target_path = validate_and_resolve_path(filename)
    with open(target_path, "w") as f:
        json.dump(data, f, indent=4)
    return target_path

# ==========================================
# DEFENSIVE PRIMALITY ENGINE
# ==========================================
@enforce_budget
def run_prime_organism_engine():
    bit_size = 16
    attempts = 0
    best_candidate_data = {}
    max_safe_bits = 4096
    start_run = time.monotonic()
    
    try:
        while True:
            GLOBAL_BUDGET.enforce()
            k = 3 if bit_size <= 512 else 5
            min_val = (1 << (bit_size - 1)) + 1
            max_val = (1 << bit_size) - 1
            candidate = random.randrange(min_val, max_val + 1, 2)
            attempts += 1
            
            # Sieve filtering
            is_prime = True
            for p in PRIMES_UNDER_1000:
                if candidate == p: break
                if candidate % p == 0:
                    is_prime = False
                    break
            else:
                # Miller-Rabin
                d = candidate - 1
                s = 0
                while d % 2 == 0:
                    d //= 2
                    s += 1
                for _ in range(k):
                    a = random.randint(2, candidate - 2)
                    x = pow(a, d, candidate)
                    if x == 1 or x == candidate - 1: continue
                    for _ in range(s - 1):
                        x = pow(x, 2, candidate)
                        if x == candidate - 1: break
                    else:
                        is_prime = False
                        break
            
            if is_prime:
                elapsed = time.monotonic() - start_run
                best_candidate_data = {
                    "prime_raw": candidate,
                    "prime_str": str(candidate),
                    "bits": bit_size,
                    "total_attempts": attempts,
                    "elapsed_time": round(elapsed, 6),
                    "fitness": round(bit_size / (max(1, attempts) * max(elapsed, 1e-6)), 6)
                }
                if bit_size * 2 <= max_safe_bits:
                    bit_size *= 2
                
    except BudgetExceededException as e:
        if best_candidate_data:
            safe_write_json("discovered_prime.json", best_candidate_data)
        raise e

# ==========================================
# CORE EVOLUTION ENGINE
# ==========================================
@enforce_budget
def evolve():
    try:
        run_prime_organism_engine()
    except BudgetExceededException:
        pass
    finally:
        pass

if __name__ == "__main__":
    evolve()