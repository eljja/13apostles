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

# -----------------------------
# 2. Primality test
# -----------------------------

def is_probable_prime(n, bit_size, stats, deadline=None):
    """
    Miller-Rabin Primality Test with explicit telemetry for Rejection Profiling.
    """
    if n <= 1000:
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
        # Witness 2 Fail: The most efficient first-pass filter for composites
        if not check_witness(2):
            stats['witness_2_fail'] += 1
            return False
            
        # Witness Static Fail: Catching composites with low-prime bases
        for base in (3, 5):
            if not check_witness(base):
                stats['witness_static_fail'] += 1
                return False
        
        # Witness Random Fail: High-confidence rounds
        for _ in range(rounds):
            if deadline and time.time() > deadline:
                stats['deadline_exit'] += 1
                return False
            a = random.randrange(7, n - 2)
            if not check_witness(a):
                stats['witness_random_fail'] += 1
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
        self.sieve_window_size = 2048
        # ILPP-OT Telemetry
        self.stats = {
            'sieve_filtered': 0,
            'witness_2_fail': 0,
            'witness_static_fail': 0,
            'witness_random_fail': 0,
            'deadline_exit': 0
        }

    def alive(self):
        return time.time() - self.birth_time < self.time_limit_sec

    def get_candidate_stream(self):
        """
        Streaming Segmented Sieve using modular arithmetic offsets.
        Logic: To find if S + 2k is divisible by prime p, we solve:
               S + 2k ≡ 0 (mod p)
               2k ≡ -S (mod p)
               k ≡ (-S) * modular_inverse(2, p) (mod p)
        """
        while self.alive():
            # Ensure S is odd and has the correct bit length
            S = random.getrandbits(self.bit_size) | (1 << (self.bit_size - 1)) | 1
            sieve = bytearray([1]) * self.sieve_window_size
            
            for p in SIEVE_DATA_CONSTANTS:
                if p == 2: continue # S is already odd, no need to sieve for 2
                
                # Calculate the starting offset k in the window [S, S + 2*window_size]
                # k represents the step index for (S + 2k)
                # pow(2, -1, p) calculates the modular multiplicative inverse of 2 mod p
                start_k = ((-S) * pow(2, -1, p)) % p
                for k in range(start_k, self.sieve_window_size, p):
                    sieve[k] = 0
            
            # Record sieve efficiency
            passed_count = sum(sieve)
            self.stats['sieve_filtered'] += (self.sieve_window_size - passed_count)
            
            for k, is_prime in enumerate(sieve):
                if is_prime:
                    yield S + 2 * k

    def search_one_generation(self):
        attempts = 0
        start = time.time()
        deadline = self.birth_time + self.time_limit_sec
        stream = self.get_candidate_stream()

        while self.alive():
            try:
                candidate = next(stream)
            except StopIteration:
                break
                
            attempts += 1
            self.total_attempts += 1

            if is_probable_prime(candidate, self.bit_size, self.stats, deadline=deadline):
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
        print("Birth of PrimeOrganism-ILPP-OT (Instrumented Logic-Path Profiling)")
        while self.alive():
            if not self.search_one_generation(): break
            self.grow()
        
        # End of life reporting
        elapsed_total = time.time() - self.birth_time
        fitness = self.best_bits / (self.total_attempts * elapsed_total) if self.total_attempts > 0 else 0
        
        total_rejections = sum(self.stats.values())
        
        print("-" * 80)
        print(f"Life ended. Elapsed: {elapsed_total:.4f}s | Successes: {self.success_count}")
        print(f"Fitness Score: {fitness:.8f} (bits / attempt-sec)")
        print(f"Rejection Profile (Total: {total_rejections}):")
        for key, val in self.stats.items():
            pct = (val / total_rejections * 100) if total_rejections > 0 else 0
            print(f"  {key:20}: {val:10} ({pct:6.2f}%)")

def main():
    organism = PrimeOrganism(time_limit_sec=5.0)
    organism.live()

if __name__ == "__main__":
    main()