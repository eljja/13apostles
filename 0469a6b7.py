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
    # Organism's bit_size floor (16-bit) ensures n >= 32768
    rounds = max(3, 12 - (bit_size // 1024))
    d = n - 1
    s = 0
    while d % 2 == 0:
        s += 1
        d //= 2
    
    try:
        # Deterministic Fast-Path: a=2 is mandatory first witness
        for i in range(rounds):
            if deadline and time.time() > deadline:
                return False
            
            if i == 0:
                a = 2
            else:
                a = random.randrange(3, n - 2)
            
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

    def make_candidate(self, deadline):
        """Generates a candidate and filters it against the full 168-prime sieve."""
        while time.time() < deadline:
            n = random.getrandbits(self.bit_size)
            n |= (1 << (self.bit_size - 1)) | 1
            
            passed_sieve = True
            for p in SMALL_PRIME_SIEVE:
                if n % p == 0:
                    if n == p: continue # Unlikely given bit_size floor
                    passed_sieve = False
                    break
            
            if passed_sieve:
                return n
        return None

    def search_one_generation(self, deadline):
        attempts = 0
        start = time.time()

        while self.alive():
            candidate = self.make_candidate(deadline)
            if candidate is None:
                break
            
            attempts += 1
            self.total_attempts += 1

            if adaptive_miller_rabin(candidate, self.bit_size, deadline):
                now = time.time()
                duration = now - start
                self.best_prime = candidate
                self.best_bits = candidate.bit_length()
                self.success_count += 1
                print(f"generation={self.generation:02d} | bits={self.bit_size:5d} | "
                      f"attempts={attempts:5d} | time={duration:7.4f}s | FOUND")
                # Return duration of the successful search
                return duration
        return None

    def grow(self, last_gen_duration):
        self.generation += 1
        
        # Guard against zero duration and negative remaining time
        safe_duration = max(1e-7, last_gen_duration)
        remaining_time = max(0, self.time_limit_sec - (time.time() - self.birth_time))
        
        # Predictive Growth Scaling based on O(bits^3) complexity
        # ratio = ((remaining_time * target_fraction) / last_gen_duration)**(1/3)
        ratio = ((remaining_time * 0.4) / safe_duration)**(1/3)
        
        # Safety Clamping: Ensure growth is between 1.1x and 2.0x
        clamped_ratio = max(1.1, min(2.0, ratio))
        self.bit_size = int(self.bit_size * clamped_ratio)

    def live(self):
        print("Birth of PrimeOrganism-3 (Deterministic Witness & Predictive Scaling)")
        deadline = self.birth_time + self.time_limit_sec
        while self.alive():
            gen_duration = self.search_one_generation(deadline)
            if gen_duration is None: 
                break
            self.grow(gen_duration)
        print("-" * 80)
        print(f"Life ended. Elapsed: {time.time() - self.birth_time:.4f}s | Successes: {self.success_count} | Max Bits: {self.best_bits}")

def main():
    organism = PrimeOrganism(time_limit_sec=5.0)
    organism.live()

if __name__ == "__main__":
    main()