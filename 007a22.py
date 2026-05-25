import random
import time


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
            if deadline is not None and time.perf_counter() > deadline:
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
            if deadline is not None and time.perf_counter() > deadline:
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
        self.birth_time = time.perf_counter()
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
        return time.perf_counter() - self.birth_time < self.time_limit_sec

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
        start = time.perf_counter()
        
        # 4. Resource-Aware Call: calculate the hard deadline
        deadline = self.birth_time + self.time_limit_sec

        while self.alive():
            candidate = self.make_candidate()
            attempts += 1
            self.total_attempts += 1

            if is_probable_prime(candidate, deadline=deadline):
                elapsed = time.perf_counter() - start

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
        Exponential growth with a Defensive Growth Cap.
        """
        MAX_BIT_SIZE = 16384
        self.generation += 1
        self.bit_size = min(self.bit_size * 2, MAX_BIT_SIZE)

    def fitness(self):
        """
        Simple fitness metric.
        """

        elapsed = time.perf_counter() - self.birth_time

        if self.best_prime is None:
            return 0.0

        return self.best_bits / max(self.total_attempts * elapsed, 1e-9)

    def live(self):
        print("Birth of PrimeOrganism-0.1 (High-Throughput)")
        print("Goal: find the largest probable prime under limited time")
        print("-" * 80)

        while self.alive():
            found = self.search_one_generation()

            if not found:
                break

            self.grow()

        print("-" * 80)
        print("Life ended.")
        print(f"elapsed_time     : {time.perf_counter() - self.birth_time:.4f}s")
        print(f"generations      : {self.generation}")
        print(f"success_count    : {self.success_count}")
        print(f"total_attempts   : {self.total_attempts}")
        print(f"best_bits        : {self.best_bits}")
        print(f"fitness          : {self.fitness():.8f}")

        if self.best_prime is not None:
            print("best_prime:")
            if self.best_bits > 4096:
                # Safe serialization formatter for large primes
                approx_digits = int(self.best_bits * 0.30103)
                shift = approx_digits - 30
                if shift > 0:
                    top_part = self.best_prime // (10 ** shift)
                    top_str = str(top_part)[:30]
                else:
                    top_str = str(self.best_prime)
                
                bottom_part = self.best_prime % (10 ** 30)
                bottom_str = f"{bottom_part:030d}"
                
                print(f"[Truncated Decimal | {self.best_bits} bits]: {top_str}...{bottom_str}")
                print(f"[Hexadecimal]: {hex(self.best_prime)}")
            else:
                print(self.best_prime)
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