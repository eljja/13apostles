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

LARGE_SIEVE_PRODUCT = reduce(lambda x, y: x * y, PRIMES_UNDER_1000)

GROWTH_FACTOR = 2

# -----------------------------
# 1. Primality test
# -----------------------------

def adaptive_miller_rabin(n, bit_size, deadline, stats=None):
    # Input Guards
    if n < 3: return n == 2
    if n % 2 == 0: return False
    if n <= 4: return True

    rounds = max(3, 12 - (bit_size // 1024))
    if stats is not None:
        stats['mr_tests'] += 1
    d = n - 1
    s = 0
    while d % 2 == 0:
        s += 1
        d //= 2
    
    try:
        # Deterministic Anchor: Use a = 2 as first witness
        witnesses = [2] + [random.randrange(2, n - 2) for _ in range(rounds - 1)]
        
        for a in witnesses:
            if deadline and time.time() > deadline:
                return False
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
    except (OverflowError, MemoryError, ValueError):
        return False

def is_probable_prime(n, bit_size, deadline=None, stats=None):
    return adaptive_miller_rabin(n, bit_size, deadline, stats)

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

        while self.alive():
            candidate = self.make_candidate()
            attempts += 1
            self.total_attempts += 1

            if is_probable_prime(candidate, self.bit_size, deadline=deadline, stats=stats):
                self.best_prime = candidate
                self.best_bits = candidate.bit_length()
                self.success_count += 1
                
                print(f"gen={self.generation:02d} | bits={self.bit_size:4d} | "
                      f"attempts={attempts:5d} | MR={stats['mr_tests']:d} | FOUND")
                return True
        return False

    def grow(self):
        self.generation += 1
        self.bit_size *= GROWTH_FACTOR

    def live(self):
        print("Birth of PrimeOrganism-ISDA (Input-Shielded Deterministic Anchor)")
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