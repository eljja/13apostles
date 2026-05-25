import random
import time
import math
import sys

# -----------------------------
# Dynamic Environment Patching
# -----------------------------
try:
    sys.set_int_max_str_digits(0)
except (AttributeError, ValueError):
    pass


# -----------------------------
# Global Static Mathematical Constants
# -----------------------------

# Expanded pre-sieve: all 168 primes less than 1000 declared as an immutable tuple
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

# Deterministic Miller-Rabin bases mapping bit-length thresholds to mathematically proven bases
DETERMINISTIC_WITNESSES = {
    32: (2, 7, 61),
    64: (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)
}


# -----------------------------
# 1. Primality test
# -----------------------------

def is_probable_prime(n, rounds=12, deadline=None):
    """
    Miller-Rabin probable primality test with Decoupled Immutable Sieve,
    Deterministic Witness Mapping, and Adaptive Test Loop Refactoring.
    """

    # 1. Input Sanitization: Handle small integers and non-integer types
    if not isinstance(n, int) or n <= 4:
        if isinstance(n, int):
            if n == 2 or n == 3:
                return True
        return False

    # 3. Complexity Cap: Prevent computational denial-of-service
    rounds = min(rounds, 64)

    # 168-element pre-sieve tuple check
    for p in SMALL_PRIME_SIEVE:
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

    # Deterministic Witness Mapping lookup based on bit-length
    bit_len = n.bit_length()
    if bit_len <= 32:
        bases = DETERMINISTIC_WITNESSES[32]
    elif bit_len <= 64:
        bases = DETERMINISTIC_WITNESSES[64]
    else:
        bases = None

    # Adaptive Test Loop Refactoring
    if bases is not None:
        for a in bases:
            if deadline is not None and time.time() > deadline:
                return False
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
    else:
        for _ in range(rounds):
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

    def benchmark_test_time(self, samples=3):
        """
        Empirical Micro-Benchmarking: Perform fast, low-overhead
        primality tests on mock candidates to calculate empirical average time.
        """
        start = time.time()
        deadline = self.birth_time + self.time_limit_sec
        count = 0
        for _ in range(samples):
            if time.time() > deadline:
                break
            cand = self.make_candidate()
            is_probable_prime(cand, deadline=deadline)
            count += 1
        elapsed = time.time() - start
        return elapsed / count if count > 0 else 0.0

    def search_one_generation(self):
        """
        Search for one probable prime in the current bit-size world.
        """

        attempts = 0
        start = time.time()
        
        # 4. Resource-Aware Call: calculate the hard deadline
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
        Exponential growth with defensive physical ceiling.
        """
        self.generation += 1
        MAX_BIT_SIZE = 8192
        if self.bit_size * 2 > MAX_BIT_SIZE:
            self.bit_size = MAX_BIT_SIZE
        else:
            self.bit_size *= 2

    def fitness(self):
        """
        Simple fitness metric.
        """

        elapsed = time.time() - self.birth_time

        if self.best_prime is None:
            return 0.0

        return self.best_bits / max(self.total_attempts * elapsed, 1e-9)

    def safe_serialize_prime(self):
        """
        Non-blocking serialization helper.
        """
        if self.best_prime is None:
            return "No prime found."
        
        if self.best_bits > 3000:
            hex_rep = hex(self.best_prime)
            try:
                s_prime = str(self.best_prime)
                if len(s_prime) > 100:
                    truncated_dec = f"{s_prime[:50]}...[truncated {len(s_prime) - 100} digits]...{s_prime[-50:]}"
                else:
                    truncated_dec = s_prime
            except Exception:
                truncated_dec = "[Decimal conversion failed]"
            
            return (
                f"Bit length: {self.best_bits}\n"
                f"Hex representation: {hex_rep}\n"
                f"Decimal (truncated): {truncated_dec}"
            )
        else:
            return str(self.best_prime)

    def live(self):
        print("Birth of PrimeOrganism-0.2 (PTG-FPST Enabled)")
        print("Goal: find the largest probable prime under limited time")
        print("-" * 80)

        while self.alive():
            # 1. Empirical Micro-Benchmarking
            t_test = self.benchmark_test_time(samples=3)

            # 2. Mathematical Expectation Modeling (Prime Number Theorem)
            a_expected = math.log(2) * self.bit_size
            t_expected = a_expected * t_test

            # 3. Fitness-Preserving Self-Termination (Meta Guard)
            elapsed_time = time.time() - self.birth_time
            t_remaining = self.time_limit_sec - elapsed_time

            if self.best_prime is not None and t_expected > t_remaining:
                print(
                    f"Meta Guard: Early self-termination triggered. "
                    f"Expected time for {self.bit_size}-bit prime is {t_expected:.4f}s, "
                    f"but only {t_remaining:.4f}s remains. Preserving fitness."
                )
                break

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
            print(self.safe_serialize_prime())
        else:
            print("No prime found.")


# -----------------------------
# 3. Birth
# -----------------------------

def main():
    organism = PrimeOrganism(time_limit_sec=5.0)
    organism.live()


if __name__ == "__main__":
    main()