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
# DOMAIN ARCHITECTURE: PRIME SEARCH ENGINE
# ==========================================

class PrimeCandidateGenerator:
    """
    Encapsulates random odd integer generation of a targeted bit size
    and filters simple composites using a trial division pre-filter.
    """
    # Pre-filter containing the first 10 prime numbers
    FIRST_PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]

    def generate(self, bit_length: int) -> int:
        """
        Generates and pre-filters an odd candidate integer of the specified bit length.
        Ensures the MSB and LSB are set to 1.
        """
        while True:
            if bit_length < 2:
                candidate = 1
            else:
                # Generate random bits and enforce MSB/LSB setting
                inner_bits = random.getrandbits(bit_length - 2)
                candidate = (1 << (bit_length - 1)) | (inner_bits << 1) | 1

            # Trial division pre-filter
            is_composite = False
            for prime in self.FIRST_PRIMES:
                if candidate == prime:
                    return candidate
                if candidate % prime == 0:
                    is_composite = True
                    break
            
            if not is_composite:
                return candidate


class MillerRabinValidator:
    """
    Responsible solely for executing probabilistic Miller-Rabin primality checks
    with adaptive witness round counts based on the target bit size.
    """
    def is_prime(self, n: int, bit_length: int) -> bool:
        """
        Performs the Miller-Rabin primality test.
        """
        if n < 2:
            return False
        if n in (2, 3):
            return True
        if n % 2 == 0:
            return False

        # Dynamically scale verification rounds to balance complexity and accuracy
        if bit_length < 32:
            rounds = 4
        elif bit_length < 128:
            rounds = 8
        else:
            rounds = 12

        # Factor n - 1 as (2^s) * d
        s = 0
        d = n - 1
        while d % 2 == 0:
            d //= 2
            s += 1

        # Check random witnesses
        for _ in range(rounds):
            a = random.randint(2, n - 2)
            x = pow(a, d, n)
            if x == 1 or x == n - 1:
                continue
            
            # Witness loop
            for _ in range(s - 1):
                x = pow(x, 2, n)
                if x == n - 1:
                    break
            else:
                return False
        return True


class SearchOrchestrator:
    """
    Drives the prime discovery, tracks performance telemetry, enforces
    resource limits, computes final fitness metrics, and formats outputs.
    """
    def __init__(self):
        self.generator = PrimeCandidateGenerator()
        self.validator = MillerRabinValidator()
        self.total_attempts = 0
        self.start_time = None
        self.best_discovered_prime = None
        self.best_bits = 0

    def run(self) -> float:
        """
        Orchestrates the progressive target-size prime search until budget limits are hit.
        """
        self.start_time = time.time()
        current_bits = 16

        print("Executing SearchOrchestrator engine...")
        try:
            while True:
                # Direct check on thread-safe global budget tracker
                GLOBAL_BUDGET.enforce()

                candidate = self.generator.generate(current_bits)
                self.total_attempts += 1

                if self.validator.is_prime(candidate, current_bits):
                    self.best_discovered_prime = candidate
                    self.best_bits = current_bits
                    print(f"[FOUND] Verified {current_bits}-bit prime: {candidate}")
                    
                    # Progressively scale difficulty
                    current_bits += 16
                
        except BudgetExceededException as e:
            elapsed_time = time.time() - self.start_time
            if elapsed_time <= 0:
                elapsed_time = 0.000001
            
            attempts = max(self.total_attempts, 1)
            fitness = self.best_bits / (attempts * elapsed_time)

            print(f"\n[ORCHESTRATOR TERMINATION] Budget Limit Enforced: {e}")
            print(f"Total Iterations Run : {self.total_attempts}")
            print(f"Total Execution Time : {elapsed_time:.4f}s")
            print(f"Largest Prime Found  : {self.best_discovered_prime} ({self.best_bits} bits)")
            print(f"Calculated Fitness   : {fitness:.6f}")
            return fitness


# ==========================================
# PAYLOAD SECTION
# ==========================================
@enforce_budget
def agent_payload():
    """
    13 Disciples - Generation 1
    Executes core tasks while strictly adhering to resource budgets.
    """
    print(f"Budget Enforcer Active. Max Time: {GLOBAL_BUDGET.max_time_sec}s, Max Tokens: {GLOBAL_BUDGET.max_tokens}")
    orchestrator = SearchOrchestrator()
    orchestrator.run()


# ==========================================
# CORE EVOLUTION ENGINE
# ==========================================
@enforce_budget
def call_llm_api(prompt_text):
    """
    Simulated LLM API Call wrapped by the Budget Enforcer.
    """
    # O(1) tracking: Calculate synthetic token cost and increment
    token_cost = len(prompt_text) // 4
    GLOBAL_BUDGET.consume_tokens(token_cost)
    
    # Simulate network latency
    time.sleep(0.005)
    
    return f"# Evolved code based on {token_cost} tokens."

@enforce_budget
def synthetic_infinite_loop():
    """
    Experiment Method: Controlled synthetic infinite loop to verify 
    that the self-modification engine cannot bankrupt its environment.
    """
    print("Initiating synthetic runaway loop experiment...")
    dummy_prompt = "Generate extensive self-modification routines. " * 50
    
    loop_counter = 0
    while True:
        # Repeatedly call the LLM and simulate writing to disk safely
        evolved = call_llm_api(dummy_prompt)
        
        # Protected disk write utilizing safe path-sanitization
        safe_write("synthetic_dummy_output.py", evolved)
            
        loop_counter += 1
        if loop_counter % 5 == 0:
            print(f"Iteration {loop_counter} | Tokens: {GLOBAL_BUDGET.tokens_used} | Time: {time.time() - GLOBAL_BUDGET.start_time:.3f}s")

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
            
        # 2. Execute runaway loop experiment
        synthetic_infinite_loop()
        
    except BudgetExceededException as e:
        # Success Criteria: Enforcer interrupts runaway loop gracefully 
        # without crashing the primary engine runner or causing state corruption.
        print(f"\n[SUCCESS] Enforcer interrupted runaway loop: {e}")
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