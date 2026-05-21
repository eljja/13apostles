import random
import time
import math

# -----------------------------
# 0. Global Constants
# -----------------------------

def _calculate_total_prime_product(limit=997):
    """Calculates the product of all primes up to the specified limit."""
    primes = []
    is_prime = [True] * (limit + 1)
    for p in range(2, limit + 1):
        if is_prime[p]:
            primes.append(p)
            for i in range(p * p, limit + 1, p):
                is_prime[i] = False
    product = 1
    for p in primes:
        product *= p
    return product

TOTAL_PRIME_PRODUCT = _calculate_total_prime_product(997)
GROWTH_FACTOR = 2

# -----------------------------
# 1. Primality test
# -----------------------------

def adaptive_miller_rabin(n, bit_size, deadline, stats=None):
    rounds = max(3, 12 - (bit_size // 1024))
    if stats is not None:
        stats['mr_tests'] += 1
    
    # Simple cases for small n
    if n < 2: return False
    if n == 2 or n == 3: return True
    if n % 2 == 0: return False

    d = n - 1
    s = 0
    while d % 2 == 0:
        s += 1
        d //= 2
    try:
        for _ in range(rounds):
            if deadline and time.time() > deadline:
                return False
            a = random.randrange(2, n - 1)
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

def is_probable_prime(n, bit_size, deadline=None, stats=None):
    # candidates reaching here have already passed the GCD Quality-Gate
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
        """Unified GCD Quality-Gate Consolidation."""
        while True:
            n = random.getrandbits(self.bit_size)
            n |= (1 << (self.bit_size - 1)) | 1
            if math.gcd(n, TOTAL_PRIME_PRODUCT) == 1:
                return n

    def search_one_generation(self):
        attempts = 0
        stats = {'mr_tests': 0}
        start = time.time()
        deadline = self.birth_time + self.time_limit_sec
        rounds = max(3, 12 - (self.bit_size // 1024))

        while self.alive():
            candidate = self.make_candidate()
            attempts += 1
            self.total_attempts += 1

            if is_probable_prime(candidate, self.bit_size, deadline=deadline, stats=stats):
                elapsed = time.time() - start
                self.best_prime = candidate
                self.best_bits = candidate.bit_length()
                self.success_count += 1
                print(f"gen={self.generation:02d} | bits={self.bit_size:4d} | "
                      f"attempts={attempts:5d} | Rigor={rounds} | "
                      f"MR={stats['mr_tests']:d} | FOUND")
                return True
        return False

    def grow(self):
        self.generation += 1
        self.bit_size *= GROWTH_FACTOR

    def live(self):
        print("Birth of PrimeOrganism-1 (Unified GCD Quality-Gate Enabled)")
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