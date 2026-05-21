# 0.py
# PrimeOrganism-0
#
# Goal:
#   Find the largest probable prime using limited time and limited computation.
#
# Meaning:
#   This is not a user-task assistant.
#   This is a minimal autonomous organism living in the world of integers.
#
# World:
#   Large integer space
#
# Organism action:
#   Generate prime candidates
#
# Perception:
#   Test whether a candidate is probably prime
#
# Fitness:
#   Larger prime found with fewer attempts and less time


import random
import time


# -----------------------------
# 1. Primality test
# -----------------------------

def is_probable_prime(n, rounds=12):
    """
    Miller-Rabin probable primality test.

    For very large numbers, deterministic proof is expensive.
    This function gives a fast probabilistic judgment:
        True  -> probably prime
        False -> definitely composite
    """

    if n < 2:
        return False

    small_primes = [
        2, 3, 5, 7, 11, 13, 17, 19, 23, 29,
        31, 37, 41, 43, 47
    ]

    for p in small_primes:
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

    for _ in range(rounds):
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

        Exact bit length condition:
            top bit = 1

        Odd condition:
            bottom bit = 1
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

        while self.alive():
            candidate = self.make_candidate()
            attempts += 1
            self.total_attempts += 1

            if is_probable_prime(candidate):
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
        Exponential growth.

        The organism does not seek the next prime.
        It seeks a prime in a much larger number world.
        """

        self.generation += 1
        self.bit_size *= 2

    def fitness(self):
        """
        Simple fitness.

        Bigger prime is better.
        Fewer attempts are better.
        Less time is better.

        This is intentionally simple for 0.py.
        """

        elapsed = time.time() - self.birth_time

        if self.best_prime is None:
            return 0.0

        return self.best_bits / max(self.total_attempts * elapsed, 1e-9)

    def live(self):
        print("Birth of PrimeOrganism-0")
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
