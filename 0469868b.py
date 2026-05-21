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
# 1. Prime organism
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
        self.telemetry = {
            'sieve_hits': 0,
            'mr_tests': 0,
            'attempts': 0
        }

    def alive(self):
        return time.time() - self.birth_time < self.time_limit_sec

    def _sieve_check(self, n):
        is_prime = n in SMALL_PRIME_SIEVE if n <= 1000 else all(n % p != 0 for p in SMALL_PRIME_SIEVE)
        if not is_prime:
            self.telemetry['sieve_hits'] += 1
        return is_prime

    def _adaptive_miller_rabin(self, n, bit_size, deadline):
        self.telemetry['mr_tests'] += 1
        d, s = n - 1, 0
        while d % 2 == 0:
            s += 1
            d //= 2
        
        try:
            # Deterministic Witness: 2
            x = pow(2, d, n)
            if x != 1 and x != n - 1:
                for _ in range(s - 1):
                    x = pow(x, 2, n)
                    if x == n - 1: break
                else: return False

            # Randomized Witnesses
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
        except (OverflowError, MemoryError, ValueError):
            return False

    def _is_probable_prime(self, n, bit_size, deadline):
        # Already sieve-vetted by the generator
        return self._adaptive_miller_rabin(n, bit_size, deadline)

    def _vetted_candidates(self, bit_size, deadline):
        while time.time() < deadline:
            self.telemetry['attempts'] += 1
            candidate = random.getrandbits(bit_size) | (1 << (bit_size - 1)) | 1
            if self._sieve_check(candidate):
                yield candidate

    def _print_generation_summary(self, status, start_stats):
        att, sie, mr = start_stats
        gen_att = self.telemetry['attempts'] - att
        gen_sie = self.telemetry['sieve_hits'] - sie
        gen_mr = self.telemetry['mr_tests'] - mr
        s_eff = (gen_sie / gen_att) * 100 if gen_att > 0 else 0
        rigor = max(3, 12 - (self.bit_size // 1024))
        print(f"gen={self.generation:02d} | bits={self.bit_size:4d} | status={status:7s} | "
              f"attempts={gen_att:5d} | Rigor={rigor} | Sieve Eff={s_eff:5.2f}% | MR={gen_mr:d}")

    def search_one_generation(self):
        deadline = self.birth_time + self.time_limit_sec
        snapshot = (self.telemetry['attempts'], self.telemetry['sieve_hits'], self.telemetry['mr_tests'])
        for candidate in self._vetted_candidates(self.bit_size, deadline):
            if self._is_probable_prime(candidate, self.bit_size, deadline):
                self.best_prime, self.best_bits = candidate, candidate.bit_length()
                self.success_count += 1
                self._print_generation_summary("FOUND", snapshot)
                return True
        self._print_generation_summary("TIMEOUT", snapshot)
        return False

    def grow(self):
        self.generation += 1
        self.bit_size *= GROWTH_FACTOR

    def live(self):
        print("Birth of PrimeOrganism (Decoupled Validator-Generator Pipeline)")
        while self.alive():
            if not self.search_one_generation(): break
            self.grow()
        
        total_time = time.time() - self.birth_time
        print("-" * 80)
        print(f"Life Summary | Elapsed: {total_time:.4f}s | Successes: {self.success_count} | Best Bits: {self.best_bits}")
        print(f"Lifecycle Efficiency Signature: Attempts={self.telemetry['attempts']} | "
              f"Sieve Rejections={self.telemetry['sieve_hits']} | MR Tests={self.telemetry['mr_tests']}")

def main():
    organism = PrimeOrganism(time_limit_sec=5.0)
    organism.live()

if __name__ == "__main__":
    main()