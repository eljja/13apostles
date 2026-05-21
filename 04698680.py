import random
import time
import sys

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

def adaptive_miller_rabin(n, bit_size, deadline, stats=None):
    if stats is not None:
        stats['mr_tests'] += 1
    d = n - 1
    s = 0
    while d % 2 == 0:
        s += 1
        d //= 2
    
    try:
        if pow(2, d, n) == 1 or pow(2, d, n) == n - 1:
            pass
        else:
            x = pow(2, d, n)
            for _ in range(s - 1):
                x = pow(x, 2, n)
                if x == n - 1: break
            else: return False
    except (OverflowError, MemoryError, ValueError): return False

    rounds = max(3, 12 - (bit_size // 1024))
    try:
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
    except (OverflowError, MemoryError, ValueError): return False

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

    def alive(self):
        return time.time() - self.birth_time < self.time_limit_sec

    def get_candidate_stream(self, window_size=2048):
        base = random.getrandbits(self.bit_size) | (1 << (self.bit_size - 1)) | 1
        bitset = bytearray([1]) * window_size
        
        for p in SMALL_PRIME_SIEVE:
            if p == 2: continue
            start = (-(base // 2)) % p
            for i in range(start, window_size, p):
                bitset[i] = 0
        
        for i in range(window_size):
            if bitset[i]:
                yield base + (i * 2)

    def search_one_generation(self):
        gen_start_attempts = self.telemetry['attempts']
        gen_start_mr = self.telemetry['mr_tests']
        deadline = self.birth_time + self.time_limit_sec

        while self.alive():
            for candidate in self.get_candidate_stream():
                self.telemetry['attempts'] += 1
                if adaptive_miller_rabin(candidate, self.bit_size, deadline, self.telemetry):
                    self.best_prime = candidate
                    self.best_bits = candidate.bit_length()
                    self.success_count += 1
                    print(f"gen={self.generation:02d} | bits={self.bit_size:4d} | status=FOUND   | "
                          f"attempts={self.telemetry['attempts']-gen_start_attempts:5d} | MR={self.telemetry['mr_tests']-gen_start_mr:d}")
                    return True
                if not self.alive(): break
        return False

    def grow(self):
        self.generation += 1
        self.bit_size *= GROWTH_FACTOR

    def live(self):
        while self.alive():
            if not self.search_one_generation(): break
            self.grow()
        print(f"Summary | Successes: {self.success_count} | Best Bits: {self.best_bits} | Attempts: {self.telemetry['attempts']} | MR: {self.telemetry['mr_tests']}")

if __name__ == "__main__":
    PrimeOrganism().live()