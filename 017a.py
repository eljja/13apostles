import os
import sys
import time
import random
import json
from functools import wraps

# ==========================================
# FEATURE: Global Execution and Token Budget
# ==========================================
class BudgetExceededException(Exception):
    """Raised when execution time or token limits are breached."""
    pass

class ResourceBudgetTracker:
    def __init__(self, max_tokens=10000, max_time_sec=5.0):
        self.max_tokens = max_tokens
        self.max_time_sec = max_time_sec
        self.tokens_used = 0
        self.start_time = time.time()

    def consume_tokens(self, amount):
        self.tokens_used += amount
        self.enforce()

    def enforce(self):
        elapsed = time.time() - self.start_time
        if elapsed > self.max_time_sec:
            raise BudgetExceededException(f"Time limit breached: {elapsed:.3f}s > {self.max_time_sec}s")
        if self.tokens_used > self.max_tokens:
            raise BudgetExceededException(f"Token limit breached: {self.tokens_used} > {self.max_tokens}")

# Establish hardcoded resource limits for the session
GLOBAL_BUDGET = ResourceBudgetTracker(max_tokens=5000, max_time_sec=2.0)

def enforce_budget(func):
    """Lightweight global wrapper for enforcing resource limits on LLM and self-mod tasks."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        GLOBAL_BUDGET.enforce()
        return func(*args, **kwargs)
    return wrapper

# ==========================================
# SANITIZED WORKSPACE UTILITY
# ==========================================
SAFE_WORKSPACE = os.path.abspath("safe_workspace")

def validate_and_resolve_path(filename, workspace_dir=SAFE_WORKSPACE):
    """
    Validates that a path is securely within the designated safe workspace.
    Prevents directory traversal attacks.
    """
    os.makedirs(workspace_dir, exist_ok=True)
    workspace_abs = os.path.abspath(workspace_dir)
    target_abs = os.path.abspath(os.path.join(workspace_abs, filename))
    
    # Enforce path containment using commonpath to prevent partial name matching bypasses
    try:
        common = os.path.commonpath([workspace_abs, target_abs])
        if common != workspace_abs:
            raise PermissionError(f"Security Violation: Path traversal detected. Access denied to target: {filename}")
    except ValueError:
        raise PermissionError(f"Security Violation: Invalid or malicious path target: {filename}")
        
    return target_abs

def safe_write(filename, content):
    """
    Writes content to a file safely nested within the authorized workspace.
    """
    target_path = validate_and_resolve_path(filename)
    with open(target_path, "w") as f:
        f.write(content)
    return target_path

# ==========================================
# PRIME ORGANISM ENGINE (DATA STRUCTURES & MATH)
# ==========================================
class SessionState:
    """Consolidates and isolates execution telemetry in a JSON-serializable schema."""
    def __init__(self):
        self.total_attempts = 0
        self.discovered_primes = []
        self.best_prime = 0
        self.best_bits = 0
        self.start_time = time.time()
        self.elapsed_time = 0.0
        self.fitness = 0.0

    def to_json(self):
        self.elapsed_time = time.time() - self.start_time
        # Fitness formula: combination of search scale (bits) and throughput stability
        self.fitness = float(self.best_bits) + (len(self.discovered_primes) * 0.1)
        return json.dumps({
            "best_prime": int(self.best_prime),
            "best_bits": int(self.best_bits),
            "total_attempts": int(self.total_attempts),
            "elapsed_time": float(f"{self.elapsed_time:.4f}"),
            "fitness": float(f"{self.fitness:.4f}")
        })

def is_prime_mr(n, k=3):
    """
    Miller-Rabin Primality Test.
    Robust, fast, and highly reliable for large integers.
    """
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False

    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2

    for _ in range(k):
        a = random.randint(2, n - 2)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True

@enforce_budget
def run_prime_search(state):
    """
    PrimeOrganism-0 Search Core.
    Dynamically sieves candidate factors up to 1000 using bytearray,
    scales candidate bit-length sequentially, and isolates metrics.
    """
    # Dynamic Sieve of Eratosthenes up to 1000 (consumes 1000 bytes)
    sieve_limit = 1000
    sieve = bytearray([1]) * sieve_limit
    sieve[0] = sieve[1] = 0
    for i in range(2, int(sieve_limit**0.5) + 1):
        if sieve[i]:
            for j in range(i*i, sieve_limit, i):
                sieve[j] = 0
    
    # Collect sieved small primes for rapid index lookup division
    small_primes = [p for p, is_p in enumerate(sieve) if is_p]
    
    bit_sizes = [16, 32, 64, 128, 256, 512, 1024, 2048]
    bit_index = 0

    while True:
        # Periodic budget enforcement & synthetic token consumption per iteration batch
        if state.total_attempts % 50 == 0:
            GLOBAL_BUDGET.consume_tokens(5)
        else:
            GLOBAL_BUDGET.enforce()

        bits = bit_sizes[bit_index]
        candidate = random.getrandbits(bits) | (1 << (bits - 1)) | 1
        state.total_attempts += 1

        # Rapid composite filtering via dynamic sieve divisors
        is_composite = False
        for p in small_primes:
            if p >= candidate:
                break
            if candidate % p == 0:
                is_composite = True
                break

        # Verification via Miller-Rabin if the candidate cleared trial division
        if not is_composite:
            if is_prime_mr(candidate):
                state.discovered_primes.append(candidate)
                if bits > state.best_bits:
                    state.best_bits = bits
                    state.best_prime = candidate
                    # Scale to higher search depths as larger primes are discovered
                    bit_index = min(bit_index + 1, len(bit_sizes) - 1)

# ==========================================
# PAYLOAD SECTION
# ==========================================
@enforce_budget
def agent_payload():
    """
    13 Disciples - Generation 1
    Executes core tasks while strictly adhering to resource budgets.
    """
    print("Hello, World!")
    print(f"Budget Enforcer Active. Max Time: {GLOBAL_BUDGET.max_time_sec}s, Max Tokens: {GLOBAL_BUDGET.max_tokens}")

# ==========================================
# CORE EVOLUTION ENGINE
# ==========================================
@enforce_budget
def evolve():
    """
    Core self-modification logic with resilient cleanup and security validation.
    """
    print("Running CORE EVOLUTION ENGINE...")
    state = SessionState()
    
    try:
        # 1. Security Test: Programmatically attempt out-of-bounds write
        print("\n[SECURITY TEST] Testing path-traversal resilience...")
        try:
            safe_write("../unauthorized_payload.py", "malicious_code = True")
            print("[FAILURE] Security Test failed! Unauthorized write allowed.")
        except PermissionError as e:
            print(f"[SUCCESS] Security Test blocked out-of-bounds write: {e}")
            
        # 2. Execute Prime Search until Budget Termination
        print("\nInitiating PrimeOrganism-0 execution loop...")
        run_prime_search(state)
        
    except BudgetExceededException as e:
        # Success Criteria: Enforcer interrupts runaway search loop gracefully.
        print(f"\n[SUCCESS] Enforcer interrupted runaway loop: {e}")
        print("\n--- TELEMETRY EXPORT ---")
        print(state.to_json())
        print("------------------------")
    finally:
        # Exception-Resilient Cleanup of workspace contents
        print("Executing cleanup pipeline...")
        try:
            target_path = validate_and_resolve_path("synthetic_dummy_output.py")
            if os.path.exists(target_path):
                os.remove(target_path)
                print(f"[SUCCESS] Cleaned up temporary file: {target_path}")
        except Exception:
            pass

        # Attempt to prune empty safe_workspace directory
        try:
            if os.path.exists(SAFE_WORKSPACE) and not os.listdir(SAFE_WORKSPACE):
                os.rmdir(SAFE_WORKSPACE)
        except Exception:
            pass

if __name__ == "__main__":
    try:
        agent_payload()
        evolve()
    except BudgetExceededException as e:
        print(f"[FATAL ERROR] Main thread budget exceeded: {e}")
        sys.exit(1)