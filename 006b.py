import random
import time

# -----------------------------
# 1. Primality Validator
# -----------------------------

class PrimalityValidator:
    """
    Stateless engine for primality verification.
    Encapsulates the mathematical logic and constant pool for pre-sieving.
    """
    
    # Constant Pool: All 168 primes less than 1000.
    # Defined as an immutable class-level tuple to avoid re-allocation in the hot path.
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

    def is_probable_prime(self, n, rounds=12, deadline=None):
        """
        Miller-Rabin probable primality test with Pre-Sieve.
        Uses the shared constant pool for maximum throughput.
        """
        if n < 5:
            return n in (2, 3)

        # Pre-sieve using the constant pool
        for p in self.SMALL_PRIMES:
            if n == p:
                return True
            if n % p == 0:
                return False

        # Miller-Rabin test: n - 1 = d * 2^s
        d = n - 1
        s = 0
        while d % 2 == 0:
            s += 1
            d //= 2

        for _ in range(rounds):
            # Temporal Guarding
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
# 2. Prime Organism
# -----------------------------

class PrimeOrganism:
    def __init__(self, validator, time_limit_sec=5.0):
        """
        Dependency Injection: The organism is injected with a primality validator instance,
        decoupling search logic from mathematical verification implementation.
        """
        self.validator = validator
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

    def make_candidate(self):
        n = random.getrandbits(self.bit_size)
        n |= 1 << (self.bit_size - 1) # Force bit length
        n |= 1                        # Force odd
        return n

    def search_one_generation(self):
        attempts = 0
        start = time.time()
        deadline = self.birth_time + self.time_limit_sec

        while self.alive():
            candidate = self.make_candidate()
            attempts += 1
            self.total_attempts += 1

            # Use the injected validator
            if self.validator.is_probable_prime(candidate, deadline=deadline):
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
        self.generation += 1
        self.bit_size *= 2

    def fitness(self):
        elapsed = time.time() - self.birth_time
        if self.best_prime is None:
            return 0.0
        return self.best_bits / max(self.total_attempts * elapsed, 1e-9)

    def live(self):
        print("Birth of PrimeOrganism-0.2 (Decoupled Validator Architecture)")
        print("Goal: maximize throughput by eliminating redundant allocations")
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
            print(self.best_prime)
        else:
            print("No prime found.")


# -----------------------------
# 3. Birth
# -----------------------------

def main():
    # Instantiate the decoupled validator once per lifecycle
    validator = PrimalityValidator()
    
    # Inject validator into the organism
    organism = PrimeOrganism(validator=validator, time_limit_sec=5.0)
    organism.live()


if __name__ == "__main__":
    main()