import random
import time
import sys
import math
from functools import reduce

# -----------------------------
# 0. Global Constants
# -----------------------------

# Primes up to 1000
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

# Consolidated pre-calculated constant: product of all primes < 1000
LARGE_SIEVE_PRODUCT = reduce(lambda x, y: x * y, PRIMES_UNDER_1000)

GROWTH_FACTOR = 2

# -----------------------------
# 1. Validation Service
# -----------------------------

class MillerRabinValidator:
    """
    Encapsulates the primality testing logic, state management, 
    and rigor configuration (SRP & DRY).
    """
    def __init__(self, bit_size, deadline, stats):
        self.bit_size = bit_size
        self.deadline = deadline
        self.stats = stats
        # Centralized rigor calculation (DRY)
        self.rounds = max(3, 12 - (bit_size // 1024))

    def is_prime(self, n):
        """
        Executes the Miller-Rabin test on n with encapsulated context.
        """
        self.stats['mr_tests'] += 1
        d = n - 1
        s = 0
        while d % 2 == 0:
            s += 1
            d //= 2
        
        try:
            for _ in range(self.rounds):
                # Contextual deadline check
                if self.deadline and time.time() > self.deadline:
                    return False
                
                a = random.randrange(2, n - 2)
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
                    return False
            return True
        except (OverflowError, MemoryError):
            return False

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
        # Candidate generation with fast C-level GCD filtering
        while True:
            n = random.getrandbits(self.bit_size)
            n |= 1 << (self.bit_size - 1)
            n |= 1
            if math.gcd(n, LARGE_SIEVE_PRODUCT) == 1:
                return n

    def search_one_generation(self):
        attempts = 0
        stats = {'mr_tests': 0}
        start = time.time()
        deadline = self.birth_time + self.time_limit_sec
        
        # Instantiate the Validation Service for this generation's context
        validator = MillerRabinValidator(self.bit_size, deadline, stats)

        while self.alive():
            candidate = self.make_candidate()
            attempts += 1
            self.total_attempts += 1

            # Interact with high-level abstraction (Simplified Interface)
            if validator.is_prime(candidate):
                self.best_prime = candidate
                self.best_bits = candidate.bit_length()
                self.success_count += 1
                
                print(f"gen={self.generation:02d} | bits={self.bit_size:4d} | "
                      f"attempts={attempts:5d} | Rigor={validator.rounds} | "
                      f"GCD Sieve=PASS | MR={stats['mr_tests']:d} | FOUND")
                return True
        return False

    def grow(self):
        self.generation += 1
        self.bit_size *= GROWTH_FACTOR

    def live(self):
        print("Birth of PrimeOrganism-1 (Validation Service Encapsulation Enabled)")
        while self.alive():
            if not self.search_one_generation(): break
            self.grow()
        print("-" * 80)
        print(f"Life ended. Elapsed: {time.time() - self.birth_time:.4f}s | Successes: {self.success_count}")

def main():
    organism = PrimeOrganism(time_limit_sec=5.0)
    organism.live()

if __name__ == "__main__":
    main()