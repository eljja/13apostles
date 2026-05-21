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
# 1. Validator Factory
# -----------------------------

def build_validator(bit_size, deadline):
    """
    Returns a closure that captures the necessary primality test parameters
    to minimize redundant calculations in the hot loop.
    """
    rounds = max(3, 12 - (bit_size // 1024))

    def validator(n):
        if n < 4:
            return n in (2, 3)

        d, s = n - 1, 0
        while d % 2 == 0:
            d //= 2
            s += 1

        def is_composite(a):
            x = pow(a, d, n)
            if x == 1 or x == n - 1:
                return False
            for _ in range(s - 1):
                x = pow(x, 2, n)
                if x == n - 1:
                    return False
            return True

        # Accuracy Hardening for <= 32-bit
        if bit_size <= 32:
            for a in (2, 7, 61):
                if n == a: return True
                if is_composite(a): return False
            return True

        # Deterministic Fast-Reject
        if is_composite(2):
            return False

        # Probabilistic checks
        for _ in range(rounds - 1):
            if deadline and time.time() > deadline:
                return False
            a = random.randrange(3, n - 2)
            if is_composite(a):
                return False
        return True

    return validator

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
        self.total_attempts = 0
        self.success_count = 0

    def alive(self):
        return time.time() - self.birth_time < self.time_limit_sec

    def _candidate_stream(self, bit_size, deadline):
        """
        Generator yielding candidates that have passed the consolidated 
        trial-division sieve.
        """
        while time.time() < deadline:
            # Generate candidate
            n = random.getrandbits(bit_size)
            n |= 1 << (bit_size - 1)
            n |= 1
            
            # Consolidated Sieve
            passed_sieve = True
            for p in SMALL_PRIME_SIEVE:
                if n % p == 0:
                    if n > p: 
                        passed_sieve = False
                    break
            
            if passed_sieve:
                yield n

    def search_one_generation(self):
        deadline = self.birth_time + self.time_limit_sec
        validate, start, gen_attempts = build_validator(self.bit_size, deadline), time.time(), 0
        
        for candidate in self._candidate_stream(self.bit_size, deadline):
            gen_attempts += 1
            self.total_attempts += 1
            if validate(candidate):
                self.best_prime, self.best_bits, self.success_count = candidate, candidate.bit_length(), self.success_count + 1
                print(f"generation={self.generation:02d} | bits={self.bit_size:5d} | "
                      f"attempts={gen_attempts:5d} | time={time.time() - start:7.4f}s | FOUND")
                return True
        return False

    def grow(self):
        self.generation += 1
        self.bit_size *= GROWTH_FACTOR

    def live(self):
        print("Birth of PrimeOrganism-2 (Functional Context-Aware Pipeline)")
        while self.alive():
            if not self.search_one_generation(): 
                break
            self.grow()
        print("-" * 80)
        print(f"Life ended. Elapsed: {time.time() - self.birth_time:.4f}s | Successes: {self.success_count}")

def main():
    organism = PrimeOrganism(time_limit_sec=5.0)
    organism.live()

if __name__ == "__main__":
    main()