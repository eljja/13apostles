import random
import time
import math
from functools import reduce

# -----------------------------
# 1. Global Sieve Data
# -----------------------------

SIEVE_DATA_CONSTANTS = (
    2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71,
    73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127
)

QUALITY_GATE_PRODUCT = reduce(lambda x, y: x * y, SIEVE_DATA_CONSTANTS)

# Precompute coprime wheel for deterministic skipping
# We map residues modulo QUALITY_GATE_PRODUCT to the next integer coprime to it
COPRIME_WHEEL = {}
def build_wheel():
    for r in range(QUALITY_GATE_PRODUCT):
        if math.gcd(r, QUALITY_GATE_PRODUCT) == 1:
            COPRIME_WHEEL[r] = 0
        else:
            # Find distance to next coprime
            skip = 1
            while math.gcd(r + skip, QUALITY_GATE_PRODUCT) != 1:
                skip += 1
            COPRIME_WHEEL[r] = skip

build_wheel()

# -----------------------------
# 2. Primality test
# -----------------------------

def is_probable_prime(n, bit_size, deadline=None):
    if n <= 127:
        return n in SIEVE_DATA_CONSTANTS
    
    rounds = max(2, min(8, bit_size // 512))

    d = n - 1
    s = 0
    while d % 2 == 0:
        s += 1
        d //= 2

    def check_witness(a):
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            return True
        for _ in range(s - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                return True
        return False

    try:
        if not check_witness(2):
            return False
        for base in (3, 5):
            if not check_witness(base):
                return False
        for _ in range(rounds):
            if deadline and time.time() > deadline:
                return False
            a = random.randrange(7, n - 2)
            if not check_witness(a):
                return False
        return True
    except (OverflowError, MemoryError, ValueError):
        return False

# -----------------------------
# 3. Prime organism
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
        n |= (1 << (self.bit_size - 1)) | 1
        
        # Max stride limit to ensure global search-space coverage
        for _ in range(100):
            r = n % QUALITY_GATE_PRODUCT
            skip = COPRIME_WHEEL[r]
            if skip == 0:
                return n
            n += skip
        return None

    def search_one_generation(self):
        attempts = 0
        start = time.time()
        deadline = self.birth_time + self.time_limit_sec

        while self.alive():
            candidate = self.make_candidate()
            if candidate is None:
                continue
                
            attempts += 1
            self.total_attempts += 1

            if is_probable_prime(candidate, self.bit_size, deadline=deadline):
                elapsed = time.time() - start
                self.best_prime = candidate
                self.best_bits = candidate.bit_length()
                self.success_count += 1
                print(f"generation={self.generation:02d} | bits={self.bit_size:5d} | "
                      f"attempts={attempts:5d} | time={elapsed:7.4f}s | FOUND")
                return True
        return False

    def grow(self):
        self.generation += 1
        remaining_ratio = (self.time_limit_sec - (time.time() - self.birth_time)) / self.time_limit_sec
        growth_factor = 1.1 + (0.9 * max(0, remaining_ratio))
        self.bit_size = max(self.bit_size + 1, int(self.bit_size * growth_factor))

    def live(self):
        print("Birth of PrimeOrganism-FDRSN (Failure-Directed Residue Skip-Navigation)")
        while self.alive():
            if not self.search_one_generation(): break
            self.grow()
        print("-" * 80)
        print(f"Life ended. Elapsed: {time.time() - self.birth_time:.4f}s | Successes: {self.success_count} | Best Bits: {self.best_bits}")

def main():
    organism = PrimeOrganism(time_limit_sec=5.0)
    organism.live()

if __name__ == "__main__":
    main()