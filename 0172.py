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
    def __init__(self, max_tokens=10000, max_time_sec=1.0):
        self.max_tokens = max_tokens
        self.max_time_sec = max_time_sec
        self.tokens_used = 0
        self.start_time = time.monotonic() # CLOCK-SHIFT IMMUNITY

    def consume_tokens(self, amount):
        # Guard against negative values or overflows
        self.tokens_used += max(0, int(amount))
        self.enforce()

    def enforce(self):
        elapsed = time.monotonic() - self.start_time # CLOCK-SHIFT IMMUNITY
        elapsed = max(0.0, elapsed) # Safeguard against negative elapsed time
        if elapsed > self.max_time_sec:
            raise BudgetExceededException(f"Time limit breached: {elapsed:.3f}s > {self.max_time_sec}s")
        if self.tokens_used > self.max_tokens:
            raise BudgetExceededException(f"Token limit breached: {self.tokens_used} > {self.max_tokens}")

# Establish hardcoded resource limits for the session (Tight 1.0s limit to verify cooperative interruption)
GLOBAL_BUDGET = ResourceBudgetTracker(max_tokens=5000, max_time_sec=1.0)

def enforce_budget(func):
    """Lightweight global wrapper for enforcing resource limits on tasks."""
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
# DEFENSIVE PRIMALITY ENGINE (PrimeOrganism-0)
# ==========================================
@enforce_budget
def run_prime_organism_engine():
    """
    Implements the PrimeOrganism-0 search engine with deep-loop budget enforcement,
    dynamic Miller-Rabin selection, and early-exit trial divisions.
    """
    print("Initiating PrimeOrganism-0 Primality Search Engine...")
    bit_size = 16
    attempts = 0
    largest_prime = None
    largest_prime_bits = 0
    
    start_run = time.monotonic()
    
    try:
        while True:
            # Cooperative check in generation loop
            GLOBAL_BUDGET.enforce()
            
            # Dynamic selection of MR rounds (k) based on target bit size
            k = 3 if bit_size <= 512 else 5
            
            # Generate candidate odd number of 'bit_size' bits
            min_val = (1 << (bit_size - 1)) + 1
            max_val = (1 << bit_size) - 1
            
            # Draw random odd candidate
            candidate = random.randrange(min_val, max_val + 1, 2)
            attempts = max(0, attempts + 1) # Guard against counter overflows
            
            is_prime = True
            
            # Early-exit trial division for primes under 100
            small_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]
            if candidate < 2:
                is_prime = False
            else:
                for p in small_primes:
                    if candidate == p:
                        break
                    if candidate % p == 0:
                        is_prime = False
                        break
                
                if is_prime and candidate >= 101:
                    # Miller-Rabin Primality Test
                    # Factor candidate - 1 to 2^s * d
                    d = candidate - 1
                    s = 0
                    while d % 2 == 0:
                        d //= 2
                        s += 1
                        GLOBAL_BUDGET.enforce() # Cooperative deep-loop budget interruption
                    
                    # Witness loop
                    for _ in range(k):
                        GLOBAL_BUDGET.enforce() # Cooperative witness-loop budget interruption
                        a = random.randint(2, candidate - 2)
                        x = pow(a, d, candidate)
                        if x == 1 or x == candidate - 1:
                            continue
                        for _ in range(s - 1):
                            GLOBAL_BUDGET.enforce() # Cooperative inner exponentiation loop interruption
                            x = pow(x, 2, candidate)
                            if x == candidate - 1:
                                break
                        else:
                            is_prime = False
                            break
            
            if is_prime:
                largest_prime = candidate
                largest_prime_bits = bit_size
                print(f"[FOUND] {bit_size}-bit prime found: {candidate} (attempts: {attempts})")
                
                # Format discovery safely for storage
                payload_content = f"prime = {candidate}\nbits = {bit_size}\nattempts = {attempts}\n"
                safe_write("discovered_prime.txt", payload_content)
                
                # Double target bit sizes upon success
                bit_size *= 2
                
    except BudgetExceededException as e:
        # Calculate metrics using zero-division guards and clean conversions
        elapsed_time = max(time.monotonic() - start_run, 0.000001)
        fitness = (largest_prime_bits * attempts) / elapsed_time
        
        print(f"\n[SUCCESS] Enforcer interrupted PrimeOrganism-0: {e}")
        print(f"Graceful termination completed.")
        print(f"Final Performance Metrics:")
        print(f"  - Max Bit Size Discovered: {largest_prime_bits}")
        print(f"  - Total Candidates Evaluated: {attempts}")
        print(f"  - Safe Elapsed Time: {elapsed_time:.6f}s")
        print(f"  - Final Fitness Score: {fitness:.4f}")
        
        # Re-raise to let parent orchestrator execute cleanups
        raise e

# ==========================================
# PAYLOAD SECTION
# ==========================================
@enforce_budget
def agent_payload():
    """
    13 Disciples - Generation 1 (Hardened Production Release)
    Executes core tasks while strictly adhering to resource budgets.
    """
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
    
    try:
        # 1. Security Test: Programmatically attempt out-of-bounds write
        print("\n[SECURITY TEST] Testing path-traversal resilience...")
        try:
            safe_write("../unauthorized_payload.py", "malicious_code = True")
            print("[FAILURE] Security Test failed! Unauthorized write allowed.")
        except PermissionError as e:
            print(f"[SUCCESS] Security Test blocked out-of-bounds write: {e}")
            
        # 2. Run PrimeOrganism-0 Primality Engine instead of placeholder loops
        run_prime_organism_engine()
        
    except BudgetExceededException as e:
        # Success Criteria: Enforcer interrupts runaway loop gracefully 
        # without crashing the primary engine runner or causing state corruption.
        print(f"\n[SUCCESS] Main Loop Gracefully Closed: {e}")
        print(f"Graceful termination completed. Final tokens used: {GLOBAL_BUDGET.tokens_used}")
    finally:
        # Exception-Resilient Cleanup of workspace contents
        print("Executing cleanup pipeline...")
        for temp_file in ["discovered_prime.txt", "synthetic_dummy_output.py"]:
            try:
                target_path = validate_and_resolve_path(temp_file)
                if os.path.exists(target_path):
                    os.remove(target_path)
                    print(f"[SUCCESS] Cleaned up temporary file: {target_path}")
            except Exception as cleanup_err:
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