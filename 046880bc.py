import random
import time
import sys
import math
from functools import reduce

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

SIEVE_PRODUCT = reduce(lambda x, y: x * y, SIEVE_DATA_CONSTANTS)

# -----------------------------
# 2. Logic Decoupling
# -----------------------------

def pass_sieve_gate(n):
    return math.gcd(n, SIEVE_PRODUCT) == 1

def verify_miller_rabin(n, rounds, deadline):
    d = n - 1
    s = 0
    while d % 2 == 0:
        s += 1
        d //= 2
    
    # Lazy Witness Evaluation
    for i in range(rounds):
        a = 2 if i == 0 else random.randrange(3, n - 2)
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

def is_probable_prime(n, bit_size, deadline, telemetry):
    if n <= 1000:
        return n in SIEVE_DATA_CONSTANTS
    if not pass_sieve_gate(n):
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
        self.best_prime = None
        self.total_candidates_generated = 0
        self.telemetry = {'gate_rejections': 0, 'mr_tests': 0}
        self.success_count = 0
        self.last_gen_duration = 0.001

    def alive(self):
        return time.time() - self.birth_time < self.time_limit_sec

    def make_candidate(self):
        while self.alive():
            self.total_candidates_generated += 1
            n = random.getrandbits(self.bit_size)
            n |= (1 << (self.bit_size - 1)) | 1
            
            if pass_sieve_gate(n):
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
                self.last_gen_duration = max(0.001, time.time() - start)
                self.best_prime = candidate
                self.success_count += 1
                ratio = self.telemetry['gate_rejections'] / max(1, self.total_candidates_generated)
                print(f"gen={self.generation:02d} | bits={self.bit_size:5d} | "
                      f"time={self.last_gen_duration:7.4f}s | SieveRatio={ratio:.3f} | FOUND")
                return True
        return False

    def grow(self):
        self.generation += 1
        
        # Cubic-Complexity Adaptive Growth (CCAG) implementation
        remaining_time = self.time_limit_sec - (time.time() - self.birth_time)
        safety_factor = 0.5
        
        # target_bits = current_bits * ( (remaining_time * safety_factor) / last_gen_duration )^(1/3)
        raw_multiplier = ((max(0, remaining_time) * safety_factor) / self.last_gen_duration) ** (1/3)
        
        # Enforce floor of 1.2x and ceiling of 2.0x
        clamped_multiplier = max(1.2, min(2.0, raw_multiplier))
        
        self.bit_size = int(self.bit_size * clamped_multiplier)

    def live(self):
        print("Birth of PrimeOrganism-4 (Cubic-Complexity Adaptive Growth)")
        while self.alive():
            if not self.search_one_generation(): break
            self.grow()
        print("-" * 80)
        print(f"Life ended. Elapsed: {time.time() - self.birth_time:.4f}s | Successes: {self.success_count} | Final Bit Size: {self.bit_size}")

def main():
    organism = PrimeOrganism(time_limit_sec=5.0)
    organism.live()

if __name__ == "__main__":
    main()