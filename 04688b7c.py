import random
import time
import sys
import math

# -----------------------------
# 1. Global Sieve Data
# -----------------------------

SIEVE_DATA_CONSTANTS = (
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

SIEVE_PRODUCT = 1
for p in SIEVE_DATA_CONSTANTS:
    SIEVE_PRODUCT *= p

# -----------------------------
# 2. Logic Decoupling
# -----------------------------

def verify_low_level_sieve(n):
    return math.gcd(n, SIEVE_PRODUCT) == 1

def verify_miller_rabin(n, rounds, deadline):
    d = n - 1
    s = 0
    while d % 2 == 0:
        s += 1
        d //= 2
    for i in range(rounds):
        if deadline and time.time() > deadline:
            return False
        
        if i == 0:
            a = 2
        else:
            a = random.randrange(3, n - 2)
            
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

def is_probable_prime(n, bit_size, deadline, telemetry):
    if n <= 1000:
        return n in SIEVE_DATA_CONSTANTS
    if not verify_low_level_sieve(n):
        return False
    telemetry['mr_tests'] += 1
    rounds = max(3, 12 - (bit_size // 1024))
    return verify_miller_rabin(n, rounds, deadline)

# -----------------------------
# 3. Prime organism
# -----------------------------

class PrimeOrganism:
    def __init__(self, time_limit_sec=5.0):
        self.birth_time = time.time()
        self.time_limit_sec = time_limit_sec
        self.generation = 0
        self.bit_size = 16
        
        # Feedback-Driven Elastic Bit-Scaling (FEBS) State
        self.last_bit_size = 0
        self.last_discovery_time = self.birth_time
        
        self.best_prime = None
        self.total_candidates_generated = 0
        self.telemetry = {'gate_rejections': 0, 'mr_tests': 0}
        self.success_count = 0

    def alive(self):
        return time.time() - self.birth_time < self.time_limit_sec

    def make_candidate(self):
        while self.alive():
            self.total_candidates_generated += 1
            n = random.getrandbits(self.bit_size)
            n |= (1 << (self.bit_size - 1)) | 1
            
            if math.gcd(n, SIEVE_PRODUCT) == 1:
                return n
            else:
                self.telemetry['gate_rejections'] += 1
        return None

    def search_one_generation(self):
        start = time.time()
        deadline = self.birth_time + self.time_limit_sec
        while self.alive():
            candidate = self.make_candidate()
            if candidate is None: break
            
            if is_probable_prime(candidate, self.bit_size, deadline, self.telemetry):
                elapsed = time.time() - start
                self.best_prime = candidate
                self.success_count += 1
                ratio = self.telemetry['gate_rejections'] / max(1, self.total_candidates_generated)
                print(f"gen={self.generation:02d} | bits={self.bit_size:5d} | "
                      f"time={elapsed:7.4f}s | SieveRatio={ratio:.3f} | FOUND")
                return True
        return False

    def grow(self):
        now = time.time()
        # FEBS Logic: Calculate velocity based on time spent and bit-growth in the last gen
        time_spent = now - self.last_discovery_time
        bits_diff = self.bit_size - self.last_bit_size
        remaining_time = (self.birth_time + self.time_limit_sec) - now
        
        if bits_diff > 0 and time_spent > 0:
            # Computational Cost per Bit (C)
            c = time_spent / bits_diff
            
            # Project achievable growth targeting the 5.0s finish line
            # Using 0.8 damping factor to account for non-linear complexity (O(k^3))
            projected_growth = (remaining_time / c) * 0.8
            
            # Constraints: Cap at 2.0x multiplier, Minimum +1 bit
            multiplier_cap = float(self.bit_size)
            clamped_growth = max(1.0, min(multiplier_cap, projected_growth))
            next_bit_size = int(self.bit_size + clamped_growth)
        else:
            # Fallback for first generation or near-zero discovery time
            next_bit_size = self.bit_size * 2
            
        # Evolution of state
        self.last_bit_size = self.bit_size
        self.bit_size = next_bit_size
        self.last_discovery_time = now
        self.generation += 1

    def live(self):
        print("Birth of PrimeOrganism-FEBS (Feedback-Driven Elastic Bit-Scaling)")
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