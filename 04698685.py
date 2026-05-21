import random
import time
import sys

# -----------------------------
# 0. Global Constants
# -----------------------------

SMALL_PRIME_SIEVE = (
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

GROWTH_FACTOR = 2

# -----------------------------
# 1. Pure Primality Validation
# -----------------------------

def sieve_check(n):
    if n <= 1000:
        return n in SMALL_PRIME_SIEVE
    return all(n % p != 0 for p in SMALL_PRIME_SIEVE)

def adaptive_miller_rabin(n, bit_size, deadline):
    d = n - 1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1
    
    try:
        if pow(2, d, n) != 1 and pow(2, d, n) != n - 1:
            x = pow(2, d, n)
            for _ in range(s - 1):
                x = pow(x, 2, n)
                if x == n - 1: break
            else: return False
            
        rounds = max(3, 12 - (bit_size // 1024))
        for _ in range(rounds - 1):
            if deadline and time.time() > deadline: return False
            a = random.randrange(2, n - 2) if n > 4 else 2
            x = pow(a, d, n)
            if x == 1 or x == n - 1: continue
            passed = False
            for _ in range(s - 1):
                x = pow(x, 2, n)
                if x == n - 1:
                    passed = True
                    break
            if not passed: return False
        return True
    except (OverflowError, MemoryError, ValueError):
        return False

def is_probable_prime(n, bit_size, deadline):
    if n < 2: return False
    if n in (2, 3): return True
    if n % 2 == 0: return False
    if not sieve_check(n): return False
    return adaptive_miller_rabin(n, bit_size, deadline)

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
        self.success_count = 0
        self.telemetry = {'sieve_hits': 0, 'mr_tests': 0, 'attempts': 0}

    def _candidate_stream(self, bit_size, deadline):
        while time.time() < deadline:
            n = random.getrandbits(bit_size) | (1 << (bit_size - 1)) | 1
            yield n

    def search_one_generation(self):
        start_state = self.telemetry.copy()
        deadline = self.birth_time + self.time_limit_sec
        
        for candidate in self._candidate_stream(self.bit_size, deadline):
            self.telemetry['attempts'] += 1
            if not sieve_check(candidate):
                self.telemetry['sieve_hits'] += 1
                continue
            
            self.telemetry['mr_tests'] += 1
            if adaptive_miller_rabin(candidate, self.bit_size, deadline):
                self.best_prime, self.best_bits, self.success_count = candidate, candidate.bit_length(), self.success_count + 1
                self._report("FOUND", start_state)
                return True
        
        self._report("TIMEOUT", start_state)
        return False

    def _report(self, status, start_state):
        da = self.telemetry['attempts'] - start_state['attempts']
        print(f"gen={self.generation:02d} | bits={self.bit_size:4d} | status={status:7s} | "
              f"attempts={da:5d} | Sieve Eff={((self.telemetry['sieve_hits'] - start_state['sieve_hits'])/da)*100:5.2f}% | "
              f"MR={self.telemetry['mr_tests'] - start_state['mr_tests']:d}")

    def grow(self):
        self.generation += 1
        self.bit_size *= GROWTH_FACTOR

    def live(self):
        print("Birth of PrimeOrganism-1 (ARPD Pattern)")
        while time.time() - self.birth_time < self.time_limit_sec:
            if not self.search_one_generation(): break
            self.grow()
        print("-" * 80)
        print(f"Summary | Successes: {self.success_count} | Best Bits: {self.best_bits}")

def main():
    PrimeOrganism(5.0).live()

if __name__ == "__main__":
    main()