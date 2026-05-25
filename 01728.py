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
    def __init__(self, max_tokens=10000, max_time_sec=1.0):
        self.max_tokens = max_tokens
        self.max_time_sec = max_time_sec
        self.tokens_used = 0
        self.start_time = time.monotonic() 

    def consume_tokens(self, amount):
        self.tokens_used += max(0, int(amount))
        self.enforce()

    def enforce(self):
        elapsed = time.monotonic() - self.start_time
        elapsed = max(0.0, elapsed)
        if elapsed > self.max_time_sec:
            raise BudgetExceededException(f"Time limit breached: {elapsed:.3f}s > {self.max_time_sec}s")
        if self.tokens_used > self.max_tokens:
            raise BudgetExceededException(f"Token limit breached: {self.tokens_used} > {self.max_tokens}")

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
    os.makedirs(workspace_dir, exist_ok=True)
    workspace_abs = os.path.abspath(workspace_dir)
    target_abs = os.path.abspath(os.path.join(workspace_abs, filename))
    try:
        common = os.path.commonpath([workspace_abs, target_abs])
        if common != workspace_abs:
            raise PermissionError(f"Security Violation: Path traversal detected. Access denied to target: {filename}")
    except ValueError:
        raise PermissionError(f"Security Violation: Invalid or malicious path target: {filename}")
    return target_abs

def safe_write(filename, content):
    target_path = validate_and_resolve_path(filename)
    with open(target_path, "w") as f:
        f.write(content)
    return target_path

# ==========================================
# SELF-PROFILING SIEVE-FILTERED ENGINE (UDEP)
# ==========================================
class AuditProfile:
    def __init__(self):
        self.candidates_evaluated = 0
        self.sieve_rejections = 0
        self.mr_evaluations = 0
        self.mr_rejections = 0
        self.witness_distribution = {}

    def to_json(self):
        # Convert integer keys to strings for JSON compliance
        dist_str_keys = {str(k): v for k, v in self.witness_distribution.items()}
        data = {
            "candidates_evaluated": self.candidates_evaluated,
            "sieve_rejections": self.sieve_rejections,
            "mr_evaluations": self.mr_evaluations,
            "mr_rejections": self.mr_rejections,
            "witness_distribution": dist_str_keys
        }
        return json.dumps(data, indent=4)

SIEVE_PRIMES = (
    2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 
    73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 
    157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229, 233, 
    239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293, 307, 311, 313, 317, 
    331, 337, 347, 349, 353, 359, 367, 373, 379, 383, 389, 397, 401, 409, 419, 
    421, 431, 433, 439, 443, 449, 457, 461, 463, 467, 479, 487, 491, 499, 503, 
    509, 521, 523, 541
)

@enforce_budget
def run_prime_organism_engine():
    """
    Implements the SPSPE with UDEP telemetry and a 100-prime sieve pre-filter.
    """
    print("Initiating SPSPE (Self-Profiling Sieve-Filtered Primality Engine)...")
    bit_size = 16
    largest_prime = None
    largest_prime_bits = 0
    audit = AuditProfile()
    start_run = time.monotonic()
    
    try:
        while True:
            GLOBAL_BUDGET.enforce()
            
            k = 3 if bit_size <= 512 else 5
            min_val = (1 << (bit_size - 1)) + 1
            max_val = (1 << bit_size) - 1
            
            candidate = random.randrange(min_val, max_val + 1, 2)
            audit.candidates_evaluated += 1
            
            is_prime = True
            
            # Extended Sieve Pre-Filter
            for p in SIEVE_PRIMES:
                if p >= candidate:
                    break
                if candidate % p == 0:
                    is_prime = False
                    audit.sieve_rejections += 1
                    break
            
            if is_prime:
                audit.mr_evaluations += 1
                # Miller-Rabin Primality Test
                d = candidate - 1
                s = 0
                while d % 2 == 0:
                    d //= 2
                    s += 1
                    GLOBAL_BUDGET.enforce()
                
                for _ in range(k):
                    GLOBAL_BUDGET.enforce()
                    a = random.randint(2, candidate - 2)
                    x = pow(a, d, candidate)
                    if x == 1 or x == candidate - 1:
                        continue
                    
                    composite_found = True
                    for _ in range(s - 1):
                        GLOBAL_BUDGET.enforce()
                        x = pow(x, 2, candidate)
                        if x == candidate - 1:
                            composite_found = False
                            break
                    
                    if composite_found:
                        audit.mr_rejections += 1
                        audit.witness_distribution[a] = audit.witness_distribution.get(a, 0) + 1
                        is_prime = False
                        break
            
            if is_prime:
                largest_prime = candidate
                largest_prime_bits = bit_size
                print(f"[FOUND] {bit_size}-bit prime found (attempts: {audit.candidates_evaluated})")
                
                payload_content = f"prime = {candidate}\nbits = {bit_size}\nattempts = {audit.candidates_evaluated}\n"
                safe_write("discovered_prime.txt", payload_content)
                
                bit_size *= 2
                
    except BudgetExceededException as e:
        elapsed_time = max(time.monotonic() - start_run, 0.000001)
        fitness = (largest_prime_bits * audit.candidates_evaluated) / elapsed_time
        profile_json = audit.to_json()
        
        # Structured Non-Blocking Serialization
        print(f"\n[SUCCESS] Enforcer interrupted SPSPE: {e}")
        print(f"Audit Profile (UDEP):\n{profile_json}")
        safe_write("audit_profile.json", profile_json)
        
        print(f"Final Performance Metrics:")
        print(f"  - Max Bit Size Discovered: {largest_prime_bits}")
        print(f"  - Total Candidates Evaluated: {audit.candidates_evaluated}")
        rejection_rate = (audit.sieve_rejections / audit.candidates_evaluated * 100) if audit.candidates_evaluated > 0 else 0
        print(f"  - Sieve Rejection Rate: {rejection_rate:.2f}%")
        print(f"  - Final Fitness Score: {fitness:.4f}")
        
        raise e

# ==========================================
# PAYLOAD AND EVOLUTION
# ==========================================
@enforce_budget
def agent_payload():
    print(f"Budget Enforcer Active. Max Time: {GLOBAL_BUDGET.max_time_sec}s, Max Tokens: {GLOBAL_BUDGET.max_tokens}")

@enforce_budget
def evolve():
    print("Running CORE EVOLUTION ENGINE...")
    try:
        print("\n[SECURITY TEST] Testing path-traversal resilience...")
        try:
            safe_write("../unauthorized_payload.py", "malicious_code = True")
            print("[FAILURE] Security Test failed!")
        except PermissionError as e:
            print(f"[SUCCESS] Security Test blocked out-of-bounds write: {e}")
            
        run_prime_organism_engine()
        
    except BudgetExceededException as e:
        print(f"\n[SUCCESS] Main Loop Gracefully Closed: {e}")
    finally:
        print("Executing cleanup pipeline...")
        for temp_file in ["discovered_prime.txt", "audit_profile.json"]:
            try:
                target_path = validate_and_resolve_path(temp_file)
                if os.path.exists(target_path):
                    os.remove(target_path)
                    print(f"[SUCCESS] Cleaned up: {temp_file}")
            except Exception:
                pass
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
    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(1)
    sys.exit(0)