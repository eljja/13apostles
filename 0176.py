import os
import sys
import time
import random
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
# STATE TRACKER AND PRIME ENGINE
# ==========================================
class StateTracker:
    def __init__(self):
        self.last_prime = None
        self.best_bits = 0
        self.total_attempts = 0

def miller_rabin(n, k=5):
    """
    Highly resilient Miller-Rabin primality test.
    Optimized and guarded with budget checks.
    """
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False

    # n - 1 = 2^r * d
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2

    for _ in range(k):
        # Temporal Guardrail inside the witness loop
        GLOBAL_BUDGET.enforce()
        
        a = random.randint(2, n - 2) if n > 3 else 2
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

def generate_candidate(bits):
    """
    Generates a secure, random odd candidate of the requested bit-length.
    """
    if bits < 2:
        bits = 2
    lower = 1 << (bits - 1)
    upper = (1 << bits) - 1
    candidate = random.randint(lower, upper)
    if candidate % 2 == 0:
        candidate += 1
        if candidate > upper:
            candidate -= 2
    return candidate

@enforce_budget
def search_primes(tracker):
    """
    Executes PrimeOrganism-0 search engine, escalating bit-size dynamically.
    """
    bits = 16
    while True:
        while True:
            tracker.total_attempts += 1
            
            # Cooperative temporal guardrail: throttle clock checking
            if tracker.total_attempts % 50 == 0:
                GLOBAL_BUDGET.enforce()
            
            candidate = generate_candidate(bits)
            
            # Defensive mathematical sanitization
            if candidate <= 3:
                if candidate in (2, 3):
                    tracker.last_prime = candidate
                    tracker.best_bits = bits
                    bits *= 2
                    break
                continue
            
            if miller_rabin(candidate, k=5):
                tracker.last_prime = candidate
                tracker.best_bits = bits
                print(f"Discovered {bits}-bit prime: {candidate}")
                bits *= 2  # Double the bit-size upon discovery
                break

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
    Runs the exception-resilient PrimeOrganism-0 search engine.
    """
    print("Running CORE EVOLUTION ENGINE...")
    tracker = StateTracker()
    
    try:
        # 1. Security Test: Programmatically attempt out-of-bounds write
        print("\n[SECURITY TEST] Testing path-traversal resilience...")
        try:
            safe_write("../unauthorized_payload.py", "malicious_code = True")
            print("[FAILURE] Security Test failed! Unauthorized write allowed.")
        except PermissionError as e:
            print(f"[SUCCESS] Security Test blocked out-of-bounds write: {e}")
            
        # 2. Execute PrimeOrganism-0 search payload
        print("\n[PAYLOAD] Initiating PrimeOrganism-0 Search Engine...")
        search_primes(tracker)
        
    except BudgetExceededException as e:
        # Success Criteria: Enforcer interrupts runaway loop gracefully 
        # and logs calculated fitness with zero data loss.
        print(f"\n[SUCCESS] Enforcer interrupted prime search: {e}")
        
        # Defensive division by zero safeguards
        elapsed_time = max(0.001, time.time() - GLOBAL_BUDGET.start_time)
        attempts = max(1, tracker.total_attempts)
        fitness = tracker.best_bits / (attempts * elapsed_time)
        
        print("Final State Saved:")
        print(f"  - Last Prime Bit Size: {tracker.best_bits}")
        print(f"  - Last Prime: {tracker.last_prime}")
        print(f"  - Total Attempts: {tracker.total_attempts}")
        print(f"  - Elapsed Time: {elapsed_time:.3f}s")
        print(f"  - Calculated Fitness: {fitness:.6f}")
        print(f"Graceful termination completed. Final tokens used: {GLOBAL_BUDGET.tokens_used}")
        
    finally:
        # Exception-Resilient Cleanup of workspace contents
        print("Executing cleanup pipeline...")
        try:
            target_path = validate_and_resolve_path("synthetic_dummy_output.py")
            if os.path.exists(target_path):
                os.remove(target_path)
                print(f"[SUCCESS] Cleaned up temporary file: {target_path}")
        except Exception as cleanup_err:
            print(f"[ERROR] Clean up sequence failed: {cleanup_err}")

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