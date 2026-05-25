import random
import time
import sys


# -----------------------------
# 0. Global Constant Pooling (Data Relocation & Read-Only Integrity)
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

SMALL_PRIMES_SET = frozenset(SMALL_PRIMES)


# -----------------------------
# 1. Primality test (Decoupled Data Contracts)
# -----------------------------

def is_probable_prime(n, rounds=12, deadline=None):
    """
    Miller-Rabin probable primality test.
    Optimized via Decoupled Clean Data Contracts: expects a pre-sieved candidate, 
    performing an O(1) set lookup and immediately launching the Miller-Rabin test.
    """

    # Input Sanitization
    if n < 5:
        return n in (2, 3)

    # Fast-path exact-match lookup
    if n in SMALL_PRIMES_SET:
        return True

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


# -----------------------------
# 2. Prime organism
# -----------------------------

class PrimeOrganism:
    # Strict maximum bit-size cap to prevent exponential memory/CPU runaways
    MAX_SAFE_BIT_SIZE = 16384

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
        Data Filtering at Source (Sieved Generation):
        Create a random odd integer with exact bit_size bits that is guaranteed 
        to be either an exact match or coprime to all primes under 1000.
        """
        while True:
            n = random.getrandbits(self.bit_size)

            # Force exact bit length.
            n |= 1 << (self.bit_size - 1)

            # Force odd.
            n |= 1

            if n in SMALL_PRIMES_SET:
                return n

            # Trial division pre-sieve at source
            is_coprime = True
            for p in SMALL_PRIMES:
                if n % p == 0:
                    is_coprime = False
                    break

            if is_coprime:
                return n

    def search_one_generation(self):
        """
        Search for one probable prime in the current bit-size world.
        Guarded against memory exhaustion, arithmetic errors, and execution anomalies.
        """

        attempts = 0
        start = time.time()
        
        # Calculate the hard deadline for primality tests
        deadline = self.birth_time + self.time_limit_sec

        try:
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
        except (ArithmeticError, MemoryError, OverflowError, Exception) as e:
            print(f"[SHIELD] Generation search interrupted gracefully. Error: {type(e).__name__}: {e}", file=sys.stderr)
            return False

        return False

    def grow(self):
        """
        Exponential growth bounded by the safe maximum bit size limit.
        """

        self.generation += 1
        self.bit_size = min(self.bit_size * 2, self.MAX_SAFE_BIT_SIZE)

    def fitness(self):
        """
        Simple fitness metric.
        """

        elapsed = time.time() - self.birth_time

        if self.best_prime is None:
            return 0.0

        return self.best_bits / max(self.total_attempts * elapsed, 1e-9)

    def live(self):
        print("Birth of PrimeOrganism-0.3 (Sieved Candidate Generation & Decoupled Data Contracts)")
        print("Goal: find the largest probable prime under limited time")
        print("-" * 80)

        try:
            while self.alive():
                found = self.search_one_generation()

                if not found:
                    break

                self.grow()
        except (ArithmeticError, MemoryError, OverflowError, Exception) as e:
            print(f"[SHIELD] Life loop intercepted gracefully. Error: {type(e).__name__}: {e}", file=sys.stderr)

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
            if self.best_bits > 10000:
                print(f"Hexadecimal (Safe Serialization, {self.best_bits} bits):")
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