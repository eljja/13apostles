import random
import time
import sys
import math
from functools import reduce

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

def adaptive_miller_rabin(n, bit_size, deadline, organism):
    rounds = max(3, 12 - (bit_size // 1024))
    organism.gen_mr_tests += 1
    organism.total_mr_tests += 1
    d = n - 1
    s = 0
    while d % 2 == 0:
        s += 1
        d //= 2
    try:
        for _ in range(rounds):
            if deadline and time.time() > deadline:
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

class PrimeOrganism:
    def __init__(self, time_limit_sec=5.0):
        self.birth_time = time.time()
        self.time_limit_sec = time_limit_sec
        self.generation = 0
        self.bit_size = 16
        self.best_prime = None
        self.best_bits = 0
        self.total_attempts = 0
        self.total_mr_tests = 0
        self.success_count = 0
        self.gen_start_time = 0
        self.gen_attempts = 0
        self.gen_mr_tests = 0
        self.gen_durations = []

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
        self.gen_attempts = 0
        self.gen_mr_tests = 0
        self.gen_start_time = time.time()
        deadline = self.birth_time + self.time_limit_sec
        rounds = max(3, 12 - (self.bit_size // 1024))

        while self.alive():
            candidate = self.make_candidate()
            self.gen_attempts += 1
            self.total_attempts += 1

            if adaptive_miller_rabin(candidate, self.bit_size, deadline, self):
                self.best_prime = candidate
                self.best_bits = candidate.bit_length()
                self.success_count += 1
                duration = time.time() - self.gen_start_time
                self.gen_durations.append(duration)
                print(f"gen={self.generation:02d} | bits={self.bit_size:4d} | attempts={self.gen_attempts:5d} | "
                      f"Rigor={rounds} | MR={self.gen_mr_tests:d} | FOUND")
                return True
        
        duration = time.time() - self.gen_start_time
        self.gen_durations.append(duration)
        print(f"[TIMEOUT] gen={self.generation:02d} | bits={self.bit_size:4d} | attempts={self.gen_attempts:5d} | MR={self.gen_mr_tests:d}")
        return False

    def report(self):
        total_time = time.time() - self.birth_time
        throughput = self.total_attempts / total_time if total_time > 0 else 0
        density = self.total_attempts / self.total_mr_tests if self.total_mr_tests > 0 else 0
        final_gen_pct = (self.gen_durations[-1] / total_time * 100) if self.gen_durations else 0
        
        print("-" * 80)
        print("POST-MORTEM REPORT")
        print(f"Throughput: {throughput:.2f} candidates/sec")
        print(f"Validation Density (Attempts/MR): {density:.2f}")
        print(f"Resource Allocation (Final Gen %): {final_gen_pct:.2f}%")
        print("-" * 80)

    def grow(self):
        self.generation += 1
        self.bit_size *= GROWTH_FACTOR

    def live(self):
        print("Birth of PrimeOrganism-1 (C-Level GCD Sieve Enabled)")
        while self.alive():
            if not self.search_one_generation(): break
            self.grow()
        self.report()

def main():
    organism = PrimeOrganism(time_limit_sec=5.0)
    organism.live()

if __name__ == "__main__":
    main()