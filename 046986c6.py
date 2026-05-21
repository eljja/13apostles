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

# -----------------------------
# 1. Primality test
# -----------------------------

def adaptive_miller_rabin(n, bit_size, deadline):
    d = n - 1
    s = 0
    while d % 2 == 0:
        s += 1
        d //= 2
    
    # Deterministic Anchor: a = 2
    if pow(2, d, n) == 1 or pow(2, d, n) == n - 1:
        pass
    else:
        x = pow(2, d, n)
        for _ in range(s - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False

    rounds = max(3, 12 - (bit_size // 1024))
    try:
        for _ in range(rounds - 1):
            if deadline and time.time() > deadline:
                return False
            a = random.randrange(2, n - 2) if n > 4 else 2
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
    except (OverflowError, MemoryError, ValueError):
        return False

def is_probable_prime(n, bit_size, deadline=None):
    # Guard Clauses
    if n < 2: return False
    if n == 2 or n == 3: return True
    # n is guaranteed to be odd and not divisible by small primes by make_candidate
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
        self.total_attempts = 0 # Now tracks MR stage attempts
        self.success_count = 0
        self.MAX_REJECTIONS = 2000

    def alive(self):
        return time.time() - self.birth_time < self.time_limit_sec

    def make_candidate(self):
        """
        GSGI implementation: Internal loop filters trivial composites
        using SMALL_PRIME_SIEVE before returning a candidate.
        """
        for _ in range(self.MAX_REJECTIONS):
            n = random.getrandbits(self.bit_size)
            if self.bit_size > 0:
                n |= 1 << (self.bit_size - 1)
            n |= 1
            
            # Internal Sieve Check
            if n <= 1000:
                if n in SMALL_PRIME_SIEVE:
                    return n
                continue
            
            is_clean = True
            for p in SMALL_PRIME_SIEVE:
                if n % p == 0:
                    is_clean = False
                    break
            if is_clean:
                return n
        return None

    def search_one_generation(self):
        attempts = 0
        start = time.time()
        deadline = self.birth_time + self.time_limit_sec
        rounds = max(3, 12 - (self.bit_size // 1024))

        while self.alive():
            candidate = self.make_candidate()
            
            # Graceful Generation Termination via Dead-Man's Switch
            if candidate is None:
                return False

            # Metric Guarding: Only count candidates that reached high-value MR stage
            attempts += 1
            self.total_attempts += 1

            if is_probable_prime(candidate, self.bit_size, deadline=deadline):
                elapsed = time.time() - start
                self.best_prime = candidate
                self.best_bits = candidate.bit_length()
                self.success_count += 1
                print(f"gen={self.generation:02d} | bits={self.bit_size:4d} | "
                      f"MR_tests={attempts:5d} | Rigor={rounds} | FOUND")
                return True
        return False

    def grow(self):
        self.generation += 1
        # Implement Predictive Bit-Length Scaling (PBLS)
        time_remaining = self.time_limit_sec - (time.time() - self.birth_time)
        growth_multiplier = 1.1 + (0.9 * (max(0.0, time_remaining) / self.time_limit_sec))
        self.bit_size = int(self.bit_size * growth_multiplier)

    def live(self):
        print("Birth of PrimeOrganism-2 (GSGI Enabled)")
        while self.alive():
            if not self.search_one_generation(): break
            self.grow()
        print("-" * 80)
        print(f"Life ended. Elapsed: {time.time() - self.birth_time:.4f}s | Successes: {self.success_count} | Best Bits: {self.best_bits} | High-Value MR Tests: {self.total_attempts}")

def main():
    organism = PrimeOrganism(time_limit_sec=5.0)
    organism.live()

if __name__ == "__main__":
    main()