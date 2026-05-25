import random
import sys
import time


# Safely configure the runtime environment to prevent fatal ValueError crashes when handling large integers
if hasattr(sys, 'set_int_max_str_digits'):
    try:
        sys.set_int_max_str_digits(0)
    except ValueError:
        pass


# Global module-level immutable tuple for Sieve Memory Optimization
_SMALL_PRIME_SIEVE = (
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

def is_probable_prime(n, rounds=12, deadline=None):
    """
    Miller-Rabin probable primality test with High-Throughput Small Prime Pre-Sieve,
    Deterministic Resource Guardrails, and Input Sanitization.
    
    Implements Hybrid Deterministic-Adaptive Verification Engine (HD-AVE).
    """

    # 1. Input Sanitization: Handle small integers and non-integer types
    if not isinstance(n, int) or n <= 4:
        if isinstance(n, int):
            if n == 2 or n == 3:
                return True
        return False

    # Pre-sieve with global optimized tuple
    for p in _SMALL_PRIME_SIEVE:
        if n == p:
            return True
        if n % p == 0:
            return False

    # n - 1 = d * 2^s
    d = n - 1
    s = 0

    while d % 2 == 0:
        s += 1
        d //= 2

    # Deterministic Path (for n < 2^64)
    if n < 18446744073709551616:
        if n < 4759123141:
            bases = [2, 7, 61]
        else:
            bases = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]

        for a in bases:
            if deadline is not None and time.time() > deadline:
                return False

            # Ensure the witness base is valid
            if a >= n - 1:
                continue

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

    # Adaptive Probabilistic Path (for n >= 2^64)
    else:
        bit_size = n.bit_length()
        if bit_size < 512:
            rounds = 4
        elif bit_size < 1024:
            rounds = 6
        elif bit_size < 2048:
            rounds = 8
        else:
            rounds = 12

        # Complexity Cap: Prevent computational denial-of-service
        rounds = min(rounds, 64)

        for _ in range(rounds):
            # Temporal Circuit Breaker: Abort if budget exceeded
            if deadline is not None and time.time() > deadline:
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


# -----------------------------
# 2. Serialization engine
# -----------------------------

def safe_format_large_int(n, digits=50):
    """
    Safely format a potentially massive integer to decimal representation 
    without triggering Python's O(N^2) decimal conversion overhead.
    """
    bit_len = n.bit_length()
    # log10(2) is approximately 0.30103
    approx_dec_digits = int(bit_len * 0.30103)
    
    if approx_dec_digits <= 100:
        return str(n)
        
    # Extract last digits using fast modulo
    low_val = n % (10 ** digits)
    low_str = str(low_val).zfill(digits)
    
    # Extract first digits using fast division
    shift = approx_dec_digits - digits
    if shift > 0:
        high_val = n // (10 ** shift)
        high_str = str(high_val).zfill(digits)[:digits]
    else:
        high_str = str(n)
        
    return f"{high_str}...{low_str} (approx {approx_dec_digits} digits)"


# -----------------------------
# 3. Prime organism
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
        """
        Life is limited by time.
        Time is the first real resource.
        """
        return time.time() - self.birth_time < self.time_limit_sec

    def make_candidate(self):
        """
        Create a random odd integer with exact bit_size bits.
        """

        n = random.getrandbits(self.bit_size)

        # Force exact bit length.
        n |= 1 << (self.bit_size - 1)

        # Force odd.
        n |= 1

        return n

    def search_one_generation(self):
        """
        Search for one probable prime in the current bit-size world.
        """

        attempts = 0
        start = time.time()
        
        # Resource-Aware Call: calculate the hard deadline
        deadline = self.birth_time + self.time_limit_sec

        while self.alive():
            candidate = self.make_candidate()
            attempts += 1
            self.total_attempts += 1

            if is_probable_prime(candidate, deadline=deadline):
                elapsed = time.time() - start

                self.best_prime = candidate
                self.best_bits = candidate.bit_length()
                self.success_count += 1

                print(
                    f"generation={self.generation:02d} | "
                    f"bits={self.bit_size:5d} | "
                    f"attempts={attempts:5d} | "
                    f"time={elapsed:7.4f}s | "
                    f"FOUND"
                )

                return True

        return False

    def grow(self):
        """
        Exponential growth with Temporal Growth Gating.
        """
        self.generation += 1
        
        remaining = self.time_limit_sec - (time.time() - self.birth_time)
        next_bit_size = self.bit_size * 2
        
        # Gating conditions: less than 0.8s left or next bit size exceeds physical ceiling
        if remaining < 0.8 or next_bit_size > 8192:
            # Cap growth: stay at current maximum safe bit-size
            pass
        else:
            self.bit_size = next_bit_size

    def fitness(self):
        """
        Simple fitness metric.
        """

        elapsed = time.time() - self.birth_time

        if self.best_prime is None:
            return 0.0

        return self.best_bits / max(self.total_attempts * elapsed, 1e-9)

    def live(self):
        print("Birth of PrimeOrganism-0.1 (High-Throughput with HD-AVE)")
        print("Goal: find the largest probable prime under limited time")
        print("-" * 80)

        while self.alive():
            found = self.search_one_generation()

            if not found:
                break

            self.grow()

        print("-" * 80)
        print("Life ended.")
        print(f"elapsed_time     : {time.time() - self.birth_time:.4f}s")
        print(f"generations      : {self.generation}")
        print(f"success_count    : {self.success_count}")
        print(f"total_attempts   : {self.total_attempts}")
        print(f"best_bits        : {self.best_bits}")
        print(f"fitness          : {self.fitness():.8f}")

        if self.best_prime is not None:
            print("best_prime:")
            # Safe Serialization: truncate large decimals to avoid O(N^2) CPU locks and string conversion crashes
            if self.best_bits >= 4096:
                truncated = safe_format_large_int(self.best_prime, digits=50)
                print(f"Decimal (truncated): {truncated}")
                print(f"Hexadecimal (full) : {hex(self.best_prime)}")
            else:
                print(self.best_prime)
        else:
            print("No prime found.")


# -----------------------------
# 4. Birth
# -----------------------------

def main():
    organism = PrimeOrganism(time_limit_sec=5.0)
    organism.live()


if __name__ == "__main__":
    main()