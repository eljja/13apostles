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

def sieve_check(n):
    # Check all 168 primes up to 997
    for p in SMALL_PRIME_SIEVE:
        if n == p: return True
        if n % p == 0: return False
    return True

def adaptive_miller_rabin(n, bit_size, deadline):
    if n < 4:
        return n in (2, 3)

    d = n - 1
    s = 0
    while d % 2 == 0:
        s += 1
        d //= 2

    def is_composite(a):
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            return False
        for _ in range(s - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                return False
        return True

    try:
        # Deterministic Multi-Witness Gatekeeping (a=2, a=3)
        if is_composite(2) or is_composite(3):
            return False

        # Adaptive Round Cap: max(2, 6 - (bit_size // 2048))
        rounds = max(2, 6 - (bit_size // 2048))
        for _ in range(rounds - 2): # -2 because 2 and 3 already tested
            if deadline and time.time() > deadline:
                return False
            a = random.randrange(4, n - 2)
            if is_composite(a):
                return False
        return True
    except (OverflowError, MemoryError):
        return False

def is_probable_prime(n, bit_size, deadline=None):
    return sieve_check(n) and adaptive_miller_rabin(n, bit_size, deadline)

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
        self.last_gen_duration = 0.01  # Initial seed value for TCGG heuristic

    def alive(self):
        return time.time() - self.birth_time < self.time_limit_sec

    def make_candidate(self):
        while True:
            n = random.getrandbits(self.bit_size)
            n |= 1 << (self.bit_size - 1)
            n |= 1
            
            # Expanded Sieve Filter (168 primes)
            passed = True
            for p in SMALL_PRIME_SIEVE:
                if n % p == 0:
                    passed = False
                    break
            if passed:
                return n

    def search_one_generation(self):
        attempts = 0
        start = time.time()
        deadline = self.birth_time + self.time_limit_sec

        while self.alive():
            candidate = self.make_candidate()
            attempts += 1
            self.total_attempts += 1

            if is_probable_prime(candidate, self.bit_size, deadline=deadline):
                now = time.time()
                elapsed = now - start
                self.last_gen_duration = max(0.0001, elapsed)
                self.best_prime = candidate
                self.best_bits = candidate.bit_length()
                self.success_count += 1
                print(f"generation={self.generation:02d} | bits={self.bit_size:5d} | "
                      f"attempts={attempts:5d} | time={elapsed:7.4f}s | FOUND")
                return True
        return False

    def grow(self):
        self.generation += 1
        # Implementation of the Adaptive Temporal-Cubic Growth Governor (TCGG)
        remaining_time = max(0.0, self.time_limit_sec - (time.time() - self.birth_time))
        
        # next_bits = current_bits + max(16, int(current_bits * min(1.0, (remaining_time / (last_gen_duration * 1.5))**(1/3))))
        denom = self.last_gen_duration * 1.5
        scaling_ratio = min(1.0, (remaining_time / denom) ** (1/3))
        
        bit_increment = max(16, int(self.bit_size * scaling_ratio))
        self.bit_size += bit_increment

    def live(self):
        print("Birth of PrimeOrganism-TCGG (Adaptive Temporal-Cubic Growth Governor)")
        while self.alive():
            if not self.search_one_generation(): break
            self.grow()
        print("-" * 80)
        print(f"Life ended. Elapsed: {time.time() - self.birth_time:.4f}s | Final Bits: {self.best_bits} | Successes: {self.success_count}")

def main():
    organism = PrimeOrganism(time_limit_sec=5.0)
    organism.live()

if __name__ == "__main__":
    main()