import random
import time
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

QUALITY_GATE_PRODUCT = reduce(lambda x, y: x * y, SIEVE_DATA_CONSTANTS[:32])
FULL_SIEVE_PRODUCT = reduce(lambda x, y: x * y, SIEVE_DATA_CONSTANTS)

# -----------------------------
# 2. Primality test
# -----------------------------

def is_probable_prime(n, bit_size, deadline=None, telemetry=None):
    if n <= 1000:
        is_prime = n in SIEVE_DATA_CONSTANTS
        if not is_prime and telemetry is not None:
            telemetry['sieve_rej'] += 1
        return is_prime
    
    if math.gcd(n, FULL_SIEVE_PRODUCT) != 1:
        if telemetry is not None:
            telemetry['sieve_rej'] += 1
        return False

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
        # Tier 1: Deterministic base-2 Miller-Rabin test
        if not check_witness(2):
            if telemetry is not None:
                telemetry['t1_mr_rej'] += 1
            return False

        # Tier 2: Light-weight check with fixed witnesses {3, 5}
        for base in (3, 5):
            if not check_witness(base):
                if telemetry is not None:
                    telemetry['t2_mr_rej'] += 1
                return False

        # Tier 3: Remaining randomized Miller-Rabin rounds
        for _ in range(rounds):
            if deadline and time.time() > deadline:
                if telemetry is not None:
                    telemetry['timeout_rej'] += 1
                return False

            a = random.randrange(7, n - 2)
            if not check_witness(a):
                if telemetry is not None:
                    telemetry['tr_mr_rej'] += 1
                return False
                
        return True
    except (OverflowError, MemoryError, ValueError):
        if telemetry is not None:
            telemetry['timeout_rej'] += 1
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
        self.telemetry = {
            'sieve_rej': 0,
            't1_mr_rej': 0,
            't2_mr_rej': 0,
            'tr_mr_rej': 0,
            'timeout_rej': 0
        }

    def alive(self):
        return time.time() - self.birth_time < self.time_limit_sec

    def make_candidate(self):
        while self.alive():
            n = random.getrandbits(self.bit_size)
            n |= (1 << (self.bit_size - 1)) | 1
            
            if math.gcd(n, QUALITY_GATE_PRODUCT) == 1:
                return n
        return None

    def search_one_generation(self):
        attempts = 0
        start = time.time()
        deadline = self.birth_time + self.time_limit_sec

        while self.alive():
            candidate = self.make_candidate()
            if candidate is None:
                break
                
            attempts += 1
            self.total_attempts += 1

            if is_probable_prime(candidate, self.bit_size, deadline=deadline, telemetry=self.telemetry):
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
        self.bit_size *= 2

    def live(self):
        print("Birth of PrimeOrganism-2 (Logic-Path Telemetry & Fitness Instrumentation)")
        while self.alive():
            if not self.search_one_generation(): break
            self.grow()
        
        elapsed_total = time.time() - self.birth_time
        fitness = self.best_bits / (self.total_attempts * elapsed_total) if self.total_attempts > 0 and elapsed_total > 0 else 0
        
        print("-" * 80)
        print(f"Life ended. Elapsed: {elapsed_total:.4f}s | Successes: {self.success_count}")
        print(f"Final Fitness Score: {fitness:.8e}")
        print("Rejection Profile:")
        for reason, count in self.telemetry.items():
            percentage = (count / self.total_attempts * 100) if self.total_attempts > 0 else 0
            print(f"  {reason:12}: {count:8d} ({percentage:6.2f}%)")

def main():
    organism = PrimeOrganism(time_limit_sec=5.0)
    organism.live()

if __name__ == "__main__":
    main()