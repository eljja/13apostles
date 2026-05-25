import os
import sys
import time
import random
import json
import math
from functools import wraps

# ==========================================
# FEATURE: Global Execution and Token Budget
# ==========================================
class BudgetExceededException(Exception):
    """Raised when execution time or token limits are breached."""
    pass

class ResourceBudgetTracker:
    def __init__(self, max_tokens=10000, max_time_sec=2.0):
        self.max_tokens = max_tokens
        self.max_time_sec = max_time_sec
        self.tokens_used = 0
        self.start_time = time.monotonic()

    def consume_tokens(self, amount):
        self.tokens_used += amount
        self.enforce()

    def enforce(self):
        elapsed = time.monotonic() - self.start_time
        if elapsed > self.max_time_sec:
            raise BudgetExceededException(f"Time limit breached: {elapsed:.3f}s > {self.max_time_sec}s")
        if self.tokens_used > self.max_tokens:
            raise BudgetExceededException(f"Token limit breached: {self.tokens_used} > {self.max_tokens}")

# Establish hardcoded resource limits for the session
GLOBAL_BUDGET = ResourceBudgetTracker(max_tokens=5000, max_time_sec=2.0)

def enforce_budget(func):
    """Lightweight global wrapper for enforcing resource limits."""
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
    """
    os.makedirs(workspace_dir, exist_ok=True)
    workspace_abs = os.path.abspath(workspace_dir)
    target_abs = os.path.abspath(os.path.join(workspace_abs, filename))
    
    try:
        common = os.path.commonpath([workspace_abs, target_abs])
        if common != workspace_abs:
            raise PermissionError(f"Security Violation: Path traversal detected: {filename}")
    except ValueError:
        raise PermissionError(f"Security Violation: Invalid path target: {filename}")
        
    return target_abs

def safe_write(filename, content):
    """Writes content to a file safely nested within the authorized workspace."""
    target_path = validate_and_resolve_path(filename)
    with open(target_path, "w") as f:
        f.write(content)
    return target_path

# ==========================================
# TELEMETRY SANITIZATION UTILITY
# ==========================================
def sanitize_telemetry_string(s, max_len=1024):
    """
    Sanitizes string telemetry by stripping control characters and capping length.
    """
    if not isinstance(s, str):
        s = str(s)
    # Strip control characters (keep only printable ASCII characters and basic whitespace)
    cleaned = "".join(c for c in s if 32 <= ord(c) <= 126 or c in ("\n", "\r", "\t"))
    return cleaned[:max_len]

# ==========================================
# STATIC VALUE INITIALIZATION
# ==========================================
def _compute_prime_product():
    """Generates the product of all prime numbers between 7 and 1000."""
    primes = []
    for candidate in range(7, 1000):
        is_p = True
        for factor in range(2, int(candidate**0.5) + 1):
            if candidate % factor == 0:
                is_p = False
                break
        if is_p:
            primes.append(candidate)
    prod = 1
    for p in primes:
        prod *= p
    return prod

PRIME_PRODUCT = _compute_prime_product()

# ==========================================
# MATHEMATICAL ENGINE: WGR-CGS Optimized
# ==========================================
def is_probable_prime(n, k=5):
    """
    Miller-Rabin primality test with adaptive budget enforcement and C-optimized GCD sieve.
    """
    if n <= 1: return False
    if n in (2, 3, 5): return True
    if n % 2 == 0 or n % 3 == 0 or n % 5 == 0: return False

    # C-Optimized GCD Sieve
    if math.gcd(n, PRIME_PRODUCT) > 1:
        return False

    # Miller-Rabin witness loop
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2
    
    for _ in range(k):
        # Cooperative Budget Verification
        GLOBAL_BUDGET.enforce()
        
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
def prime_organism_engine():
    """
    Core search engine that scales bit-length of prime candidates 
    until budget exhaustion, using Modulo-30 residue-class wheel generation.
    """
    best_bits = 0
    total_attempts = 0
    current_bits = 16
    found_primes = []

    print(f"Starting WGR-CGS Prime Search. Budget: {GLOBAL_BUDGET.max_time_sec}s")

    try:
        while True:
            GLOBAL_BUDGET.enforce()
            
            # Defensive Bit-Size Ceiling: Clamp candidate request to 4096 bits
            current_bits = min(current_bits, 4096)
            
            # Modulo-30 Residue-Class Wheel Generator
            m_min = (2**(current_bits - 1) + 29) // 30
            m_max = (2**current_bits - 1 - 29) // 30
            
            if m_max < m_min:
                # Fallback for very small bit lengths (mathematically unreachable since current_bits >= 16)
                candidate = random.getrandbits(current_bits)
                candidate |= (1 << (current_bits - 1)) | 1
            else:
                candidate = 30 * random.randint(m_min, m_max) + random.choice((1, 7, 11, 13, 17, 19, 23, 29))
            
            total_attempts += 1
            
            # Adaptive k scaling
            k_rounds = 3 if current_bits < 512 else 5
            
            if is_probable_prime(candidate, k=k_rounds):
                best_bits = current_bits
                found_primes.append(str(candidate))
                print(f"Found {best_bits}-bit prime. Incrementing complexity...")
                # Double bit size iteratively
                current_bits *= 2
            
            # Small token consumption to simulate logic complexity
            GLOBAL_BUDGET.consume_tokens(1)

    except BudgetExceededException as e:
        elapsed_time = time.monotonic() - GLOBAL_BUDGET.start_time
        # Mitigate division by zero/near-zero
        denom = max(elapsed_time, 0.001)
        fitness = (best_bits ** 2) / denom
        
        # Structured Telemetry Sanitization
        sanitized_reason = sanitize_telemetry_string(str(e))
        sanitized_timestamp = sanitize_telemetry_string(time.ctime())
        
        report = {
            "best_bits": best_bits,
            "total_attempts": total_attempts,
            "fitness": round(fitness, 4),
            "termination_reason": sanitized_reason,
            "timestamp": sanitized_timestamp
        }
        
        # Harmonized Security: Finalized structured report
        report_path = safe_write("prime_discovery_report.json", json.dumps(report, indent=4))
        print(f"\n[TERMINATION] Budget reached. Report saved to: {report_path}")
        print(f"Final Stats -> Bits: {best_bits} | Attempts: {total_attempts} | Fitness: {report['fitness']}")
        raise

# ==========================================
# CORE EVOLUTION RUNNER
# ==========================================
def evolve():
    """
    Orchestrates the primality search within the hardened sandbox.
    """
    print("Running Meta-Balanced Transition...")
    
    try:
        # 1. Security Test: Maintain path-traversal resilience check
        print("[SECURITY TEST] Verifying sandbox isolation...")
        try:
            safe_write("../unauthorized.txt", "fail")
        except PermissionError:
            print("[SUCCESS] Sandbox integrity verified.")

        # 2. Execute Prime Search Engine
        prime_organism_engine()
        
    except BudgetExceededException:
        # Expected graceful exit
        pass
    finally:
        # Clean post-run directory state (keeping only the report)
        print("Executing post-run cleanup...")
        pass

if __name__ == "__main__":
    try:
        evolve()
    except Exception as fatal:
        print(f"System Failure: {fatal}")
        sys.exit(1)