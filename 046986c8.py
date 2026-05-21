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

def sieve_check(n):
    return all(n % p != 0 for p in SMALL_PRIME_SIEVE if n > p)

def adaptive_miller_rabin(n, bit_size, deadline):
    d = n - 1
    s = 0
    while d % 2 == 0:
        s += 1
        d //= 2
    
    if pow(2, d, n) != 1 and pow(2, d, n) != n - 1:
        x = pow(2, d, n)
        for _ in range(s - 1):
            x = pow(x, 2, n)
            if x == n - 1: break
        else: return False

    rounds = max(3, 12 - (bit_size // 1024))
    for _ in range(rounds - 1):
        if time.time() > deadline: return False
        a = random.randrange(2, n - 2) if n > 4 else 2
        x = pow(a, d, n)
        if x == 1 or x == n - 1: continue
        for _ in range(s - 1):
            x = pow(x, 2, n)
            if x == n - 1: break
        else: return False
    return True

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
        self.telemetry = {'sieve_rejections': 0, 'mr_tests': 0, 'vetted_attempts': 0}

    def _vetted_candidate_stream(self, deadline):
        while time.time() < deadline:
            n = random.getrandbits(self.bit_size) | (1 << (self.bit_size - 1)) | 1
            if not sieve_check(n):
                self.telemetry['sieve_rejections'] += 1
                continue
            self.telemetry['vetted_attempts'] += 1
            yield n

    def search_one_generation(self):
        deadline = self.birth_time + self.time_limit_sec
        gen_vetted = 0
        for candidate in self._vetted_candidate_stream(deadline):
            gen_vetted += 1
            self.telemetry['mr_tests'] += 1
            if adaptive_miller_rabin(candidate, self.bit_size, deadline):
                self.best_prime, self.best_bits, self.success_count = candidate, candidate.bit_length(), self.success_count + 1
                print(f"gen={self.generation:02d} | bits={self.bit_size:4d} | vetted={gen_vetted:5d} | status=FOUND")
                return True
        print(f"gen={self.generation:02d} | bits={self.bit_size:4d} | vetted={gen_vetted:5d} | status=TIMEOUT")
        return False

    def grow(self):
        self.generation += 1
        time_remaining = self.time_limit_sec - (time.time() - self.birth_time)
        self.bit_size = int(self.bit_size * (1.1 + (0.9 * max(0.0, time_remaining) / self.time_limit_sec)))

    def live(self):
        print("Birth of PrimeOrganism-1 (UTVCP Enabled)")
        while time.time() - self.birth_time < self.time_limit_sec:
            if not self.search_one_generation(): break
            self.grow()
        print("-" * 80)
        print(f"Life ended. Successes: {self.success_count} | Vetted: {self.telemetry['vetted_attempts']} | Best Bits: {self.best_bits}")

if __name__ == "__main__":
    PrimeOrganism(time_limit_sec=5.0).live()