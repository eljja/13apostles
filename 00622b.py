import random
import sys
import time


# -----------------------------
# Global Static Sieve Tuple
# -----------------------------

SMALL_PRIMES = (
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
# Heuristic Strategy & Guardrails
# -----------------------------

class PrimalityStrategy:
    """
    Centralized configuration registry for primality testing heuristics.
    Adheres to SRP by separating algorithmic execution from heuristic parameters.
    """
    @staticmethod
    def get_rounds(bit_size: int) -> int:
        if bit_size < 256:
            return 3
        elif bit_size < 1024:
            return 5
        else:
            return 8

    @staticmethod
    def estimate_cost_seconds(bit_size: int) -> float:
        """Empirical estimate: testing a B-bit integer takes approx (B/1024)^3 * 0.05 seconds."""
        return ((bit_size / 1024.0) ** 3) * 0.05


# -----------------------------
# 1. Primality test
# -----------------------------

def is_probable_prime(n, rounds=None, deadline=None):
    """
    Miller-Rabin probable primality test with High-Throughput Small Prime Pre-Sieve.
    Now includes Input Sanitization, Temporal Guarding, Dynamic Strategy Round Scaling, 
    and Robust Exception Shielding.
    """
    try:
        # Input Sanitization: Explicit handling for small integers to prevent randrange error
        if n < 5:
            return n in (2, 3)

        for p in SMALL_PRIMES:
            if n == p:
                return True
            if n % p == 0:
                return False

        # Resolve rounds dynamically from strategy class if not specified
        if rounds is None:
            rounds = PrimalityStrategy.get_rounds(n.bit_length())

        # n - 1 = d * 2^s
        d = n - 1
        s = 0

        while d % 2 == 0:
            s += 1
            d //= 2

        for _ in range(rounds):
            # Temporal Guarding: Active Resource Monitoring
            if deadline and time.time() > deadline:
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
    except (ArithmeticError, ValueError, MemoryError, Exception) as e:
        print(f"[-] Exception shielded during candidate testing: {type(e).__name__}: {e}", file=sys.stderr)
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
        Now executes within an Execution Exception Shield with Decoupled Temporal Predictor.
        """

        attempts = 0
        start = time.time()
        
        # Calculate the hard deadline for primality tests
        deadline = self.birth_time + self.time_limit_sec

        while self.alive():
            try:
                # Check remaining time before candidate generation and testing
                remaining_time = deadline - time.time()
                
                # Fetch estimation from strategy class to eliminate inline magic formulas
                estimated_seconds = PrimalityStrategy.estimate_cost_seconds(self.bit_size)
                if remaining_time < estimated_seconds * 1.5:
                    break

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
            except (ArithmeticError, ValueError, MemoryError, Exception) as e:
                print(f"[-] Exception shielded during generation search: {type(e).__name__}: {e}", file=sys.stderr)
                return False

        return False

    def grow(self):
        """
        Exponential growth.
        """

        self.generation += 1
        self.bit_size *= 2

    def fitness(self):
        """
        Simple fitness metric.
        """

        elapsed = time.time() - self.birth_time

        if self.best_prime is None:
            return 0.0

        return self.best_bits / max(self.total_attempts * elapsed, 1e-9)

    def live(self):
        print("Birth of PrimeOrganism-0.3 (Decoupled Strategy-Driven & Guarded)")
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
            # Safe Serialization Shield (CVE-2020-10735 Mitigation):
            # Print hexadecimal representation if bit size is greater than 10,000 (safely below ~4,300 decimal digits).
            if self.best_bits > 10000:
                print(hex(self.best_prime))
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