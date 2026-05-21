import random
import time
import math
from functools import reduce

# -----------------------------
# 1. Primality Verification Engine
# -----------------------------

class PrimalityEngine:
    def __init__(self):
        # Encapsulated Constants
        self.sieve_constants = (
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
        self.quality_gate_product = reduce(lambda x, y: x * y, self.sieve_constants[:32])
        self.full_sieve_product = reduce(lambda x, y: x * y, self.sieve_constants)
        self.mr_bases = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31)

    def verify(self, n, bit_size, deadline=None, telemetry=None):
        """
        Unified decision pipeline for primality testing.
        Consolidates Sieve filtering and Miller-Rabin witnessing.
        """
        # Small integer bypass
        if n <= 1000:
            return n in self.sieve_constants

        # Small-prime pre-sieve (Single math.gcd execution)
        if math.gcd(n, self.full_sieve_product) != 1:
            if telemetry is not None:
                telemetry['sieve_rejections'] += 1
            return False

        # Probabilistic Miller-Rabin phase
        if telemetry is not None:
            telemetry['mr_invocations'] += 1
            
        rounds = max(3, 12 - (bit_size // 1024))
        d = n - 1
        s = 0
        while d % 2 == 0:
            s += 1
            d //= 2

        try:
            for i in range(rounds):
                if deadline and time.time() > deadline:
                    return False
                
                a = self.mr_bases[i % len(self.mr_bases)]
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
# 2. Prime Organism
# -----------------------------

class PrimeOrganism:
    def __init__(self, engine, time_limit_sec=5.0):
        self.engine = engine
        self.birth_time = time.time()
        self.time_limit_sec = time_limit_sec
        self.generation = 0
        self.bit_size = 16
        self.best_prime = None
        self.success_count = 0
        self.telemetry = {
            'candidates': 0, 
            'sieve_rejections': 0, 
            'mr_invocations': 0
        }

    def alive(self):
        return time.time() - self.birth_time < self.time_limit_sec

    def make_candidate(self):
        """Generates a raw odd candidate of current bit size."""
        n = random.getrandbits(self.bit_size)
        n |= (1 << (self.bit_size - 1)) | 1
        self.telemetry['candidates'] += 1
        return n

    def search_one_generation(self):
        start = time.time()
        deadline = self.birth_time + self.time_limit_sec
        gen_start_candidates = self.telemetry['candidates']
        gen_start_sieve = self.telemetry['sieve_rejections']

        while self.alive():
            candidate = self.make_candidate()
            
            # Delegate all filtering to the Unified Engine
            if self.engine.verify(candidate, self.bit_size, deadline, self.telemetry):
                elapsed = time.time() - start
                self.best_prime = candidate
                self.success_count += 1
                
                gen_candidates = self.telemetry['candidates'] - gen_start_candidates
                gen_sieve = self.telemetry['sieve_rejections'] - gen_start_sieve
                efficiency = gen_sieve / gen_candidates if gen_candidates > 0 else 0
                
                print(f"gen={self.generation:02d} | bits={self.bit_size:5d} | "
                      f"time={elapsed:7.4f}s | sieve_eff={efficiency:.4f} | FOUND")
                return True
        return False

    def grow(self):
        self.generation += 1
        self.bit_size *= 2

    def live(self):
        print("Birth of PrimeOrganism-UPVE (Unified Primality Verification Engine)")
        while self.alive():
            if not self.search_one_generation(): 
                break
            self.grow()
        print("-" * 80)
        print(f"Life ended. Total candidates: {self.telemetry['candidates']} | "
              f"Successes: {self.success_count}")

# -----------------------------
# 3. Entry Point
# -----------------------------

def main():
    engine = PrimalityEngine()
    organism = PrimeOrganism(engine=engine, time_limit_sec=5.0)
    organism.live()

if __name__ == "__main__":
    main()