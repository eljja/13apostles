import random
# Use time and sys for boundary controls and logging
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

FILTER_PRIMES = SMALL_PRIME_SIEVE[:40]
GROWTH_FACTOR = 2
MIN_MR_ROUNDS = 3
MAX_BIT_SIZE = 16384  # Deterministic Resource Boundary

# -----------------------------
# 1. Primality test logic
# -----------------------------

def get_rigor(bit_size):
    """Calculates Miller-Rabin rounds based on bit-size for balanced certainty/cost."""
    if bit_size <= 32: return 3
    return max(MIN_MR_ROUNDS, 12 - (bit_size // 1024))

def adaptive_miller_rabin(n, bit_size, deadline):
    if n < 4: return n in (2, 3)
    d = n - 1
    s = 0
    while d % 2 == 0:
        s += 1
        d //= 2

    def is_composite(a):
        x = pow(a, d, n)
        if x == 1 or x == n - 1: return False
        for _ in range(s - 1):
            x = pow(x, 2, n)
            if x == n - 1: return False
        return True

    try:
        if bit_size <= 32:
            for a in (2, 7, 61):
                if n == a: return True
                if is_composite(a): return False
            return True

        if is_composite(2): return False
        rounds = get_rigor(bit_size)
        for _ in range(rounds - 1):
            if deadline and time.time() > deadline: return False
            a = random.randrange(3, n - 2)
            if is_composite(a): return False
        return True
    except (OverflowError, MemoryError):
        return False

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
        
        # Telemetry
        self.total_generated = 0
        self.sieve_rejected = 0
        self.mr_tests_performed = 0
        self.total_mr_rounds = 0
        self.success_count = 0

    def alive(self):
        return time.time() - self.birth_time < self.time_limit_sec

    def make_candidate(self):
        # Loop Iteration Cap: Prevents infinite search if prime density is low
        for _ in range(50000):
            self.total_generated += 1
            n = random.getrandbits(self.bit_size)
            n |= 1 << (self.bit_size - 1)
            n |= 1
            
            passed = True
            for p in FILTER_PRIMES:
                if n % p == 0:
                    passed = False
                    self.sieve_rejected += 1
                    break
            if passed: return n
        return None

    def search_one_generation(self):
        deadline = self.birth_time + self.time_limit_sec
        attempts_this_gen = 0
        
        while self.alive():
            candidate = self.make_candidate()
            
            # Safety-Aware Orchestration: Terminate if no candidate produced within cap
            if candidate is None:
                return False

            attempts_this_gen += 1
            self.mr_tests_performed += 1
            self.total_mr_rounds += get_rigor(self.bit_size)

            if adaptive_miller_rabin(candidate, self.bit_size, deadline=deadline):
                self.best_prime = candidate
                self.best_bits = candidate.bit_length()
                self.success_count += 1
                
                sieve_eff = ((self.total_generated - self.sieve_rejected) / self.total_generated) * 100
                print(f"Gen={self.generation:02d} | Bits={self.bit_size:5d} | "
                      f"Rigor={get_rigor(self.bit_size)} | SieveEff={sieve_eff:5.2f}% | "
                      f"Attempts={attempts_this_gen:5d} | FOUND")
                return True
        return False

    def grow(self):
        self.generation += 1
        # Growth Ceiling: Clamping the bit-depth for hardware safety
        self.bit_size = min(self.bit_size * GROWTH_FACTOR, MAX_BIT_SIZE)

    def live(self):
        print("Birth of PrimeOrganism (Safety Guardrails Enabled)")
        while self.alive():
            if not self.search_one_generation(): break
            self.grow()
        
        yield_val = (self.success_count / self.total_generated * 1000) if self.total_generated > 0 else 0
        print("-" * 80)
        print(f"Lifecycle Summary:")
        print(f"Total Work (MR Rounds): {self.total_mr_rounds}")
        print(f"Discovery Yield: {yield_val:.2f} primes/1k candidates")
        print(f"Total Successes: {self.success_count}")
        if self.best_prime:
            print(f"Largest Found: {self.best_bits} bits")

def main():
    # Integer String Limit: Prevents ValueError on printing massive numbers
    if hasattr(sys, 'set_int_max_str_digits'):
        sys.set_int_max_str_digits(10000)
        
    organism = PrimeOrganism(time_limit_sec=5.0)
    organism.live()

if __name__ == "__main__":
    main()