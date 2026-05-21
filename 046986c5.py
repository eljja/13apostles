import random
import time
import sys

# -----------------------------
# 0. Global Constants
# -----------------------------

SMALL_PRIME_SIEVE = (
    2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71,
    73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151,
    157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229, 233,
    239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293, 307, 311, 313, 317,
    331, 337, 347, 349, 353, 359, 367, 373, 379, 383, 389, 397, 401, 409, 419,
    421, 431, 433, 439, 443, 449, 457, 461, 463, 467, 479, 487, 491, 499, 503,
    509, 521, 523, 541, 547, 557, 563, 569, 571, 577, 587, 593, 599, 601, 607,
    613, 617, 619, 631, 641, 643, 647, 653, 659, 661, 673, 677, 683, 691, 701,
    709, 719, 727, 733, 739, 743, 751, 757, 761, 769, 773, 787, 797, 809, 811,
    821, 823, 827, 829, 839, 853, 857, 859, 863, 877, 881, 883, 887, 907, 911,
    919, 929, 937, 941, 947, 953, 967, 971, 977, 983, 991, 997
)

# -----------------------------
# 1. Pure Primality Test Functions
# -----------------------------

def sieve_check(n):
    """Pure function: Returns True if n passes small prime division check."""
    if n <= 1000:
        return n in SMALL_PRIME_SIEVE
    for p in SMALL_PRIME_SIEVE:
        if n % p == 0:
            return False
    return True

def adaptive_miller_rabin(n, rounds):
    """
    Pure function: Miller-Rabin test. 
    Returns (is_prime, rounds_executed).
    """
    d = n - 1
    s = 0
    while d % 2 == 0:
        s += 1
        d //= 2
    
    # Deterministic base 2 check
    x = pow(2, d, n)
    if x == 1 or x == n - 1:
        passed = True
    else:
        passed = False
        for _ in range(s - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                passed = True
                break
    
    if not passed:
        return False, 1

    # Random witness checks for remaining rounds
    for i in range(1, rounds):
        a = random.randrange(2, n - 2) if n > 4 else 2
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        passed = False
        for _ in range(s - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                passed = True
                break
        if not passed:
            return False, i + 1
            
    return True, rounds

def is_probable_prime(n, rounds):
    """
    Pure function entry point for primality testing.
    Returns (is_prime, mr_rounds_run).
    """
    if n < 2: return False, 0
    if n == 2 or n == 3: return True, 0
    if n % 2 == 0: return False, 0
    
    if not sieve_check(n):
        return False, 0
    
    return adaptive_miller_rabin(n, rounds)

# -----------------------------
# 2. Prime organism
# -----------------------------

class PrimeOrganism:
    def __init__(self, time_limit_sec=5.0):
        self.birth_time = time.time()
        self.time_limit_sec = time_limit_sec
        self.generation = 0
        self.bit_size = 16
        self.best_prime = None
        self.best_bits = 0
        self.total_attempts = 0
        self.success_count = 0

    def alive(self):
        return time.time() - self.birth_time < self.time_limit_sec

    def make_candidate(self):
        n = random.getrandbits(self.bit_size)
        n |= 1 << (self.bit_size - 1)
        n |= 1
        return n

    def search_one_generation(self):
        # Parameter Pre-calculation
        rounds = max(3, 12 - (self.bit_size // 1024))
        # Adaptive Batch Size Calculation
        batch_size = max(1, min(64, 2048 // max(1, self.bit_size)))
        
        gen_attempts = 0
        gen_sieve_hits = 0
        gen_mr_tests = 0
        start_time = time.time()

        while self.alive():
            # Batch Dispatcher
            batch_found = None
            local_attempts = 0
            local_sieve_hits = 0
            local_mr_tests = 0
            
            for _ in range(batch_size):
                candidate = self.make_candidate()
                local_attempts += 1
                
                # Pure Function Validation
                is_p, mr_cnt = is_probable_prime(candidate, rounds)
                
                local_mr_tests += mr_cnt
                if mr_cnt == 0:
                    local_sieve_hits += 1
                
                if is_p:
                    batch_found = candidate
                    break
            
            # Telemetry Aggregation (flushing batch results to generation/instance state)
            gen_attempts += local_attempts
            gen_sieve_hits += local_sieve_hits
            gen_mr_tests += local_mr_tests
            self.total_attempts += local_attempts

            if batch_found:
                self.best_prime = batch_found
                self.best_bits = batch_found.bit_length()
                self.success_count += 1
                sieve_eff = (gen_sieve_hits / gen_attempts) * 100
                print(f"gen={self.generation:02d} | bits={self.bit_size:4d} | "
                      f"attempts={gen_attempts:5d} | Rigor={rounds} | "
                      f"Sieve Eff={sieve_eff:5.2f}% | MR={gen_mr_tests:d} | FOUND")
                return True
                
        return False

    def grow(self):
        self.generation += 1
        time_remaining = self.time_limit_sec - (time.time() - self.birth_time)
        growth_multiplier = 1.1 + (0.9 * (max(0.0, time_remaining) / self.time_limit_sec))
        self.bit_size = int(self.bit_size * growth_multiplier)

    def live(self):
        print("Birth of PrimeOrganism-PFV-BD (Pure Functions & Batch Dispatch)")
        while self.alive():
            if not self.search_one_generation(): 
                break
            self.grow()
        print("-" * 80)
        print(f"Life ended. Elapsed: {time.time() - self.birth_time:.4f}s | Successes: {self.success_count} | Best Bits: {self.best_bits}")

def main():
    organism = PrimeOrganism(time_limit_sec=5.0)
    organism.live()

if __name__ == "__main__":
    main()