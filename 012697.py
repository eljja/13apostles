import ast
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

# Establish resource limits (5.0s per target budget constraint)
GLOBAL_BUDGET = ResourceBudgetTracker(max_tokens=5000, max_time_sec=5.0)

def enforce_budget(func):
    """Lightweight global wrapper for enforcing resource limits on LLM and self-mod tasks."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        GLOBAL_BUDGET.enforce()
        return func(*args, **kwargs)
    return wrapper

# ==========================================
# FEATURE: Persistent State Registry
# ==========================================
class ExecutionState:
    def __init__(self):
        self.best_prime = None
        self.bit_size = 0
        self.total_attempts = 0
        self.elapsed_time_at_discovery = 0.0

# Global state tracker instance
EXECUTION_STATE = ExecutionState()

# Static tuple of the first 30 primes for cheap composite rejection
SMALL_PRIMES = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113)

# ==========================================
# FEATURE: AST Guardrail and Sandbox Shield
# ==========================================
class SecurityViolation(Exception):
    """Raised when evolved code violates security or resource policies."""
    pass

class ASTGuardrail:
    """
    Static analysis gatekeeper that validates evolved code before execution.
    """
    ALLOWED_MODULES = {'math', 'time', 'random', 'functools', 'collections', 'itertools'}
    BANNED_BUILTINS = {'exec', 'eval', 'compile', 'open', 'getattr', 'setattr'}
    BANNED_ATTRS = {'__globals__', '__dict__', '__subclasses__'}

    @staticmethod
    def validate(source_code):
        try:
            tree = ast.parse(source_code)
        except SyntaxError as e:
            raise SecurityViolation(f"Invalid Python syntax: {e}")

        for node in ast.walk(tree):
            # 1. Enforce Module Import Whitelist
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.split('.')[0] not in ASTGuardrail.ALLOWED_MODULES:
                        raise SecurityViolation(f"Forbidden module import: {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                if node.module and node.module.split('.')[0] not in ASTGuardrail.ALLOWED_MODULES:
                    raise SecurityViolation(f"Forbidden module import: {node.module}")

            # 2. Ban Dynamic/Reflective Execution Builtins
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id in ASTGuardrail.BANNED_BUILTINS:
                    raise SecurityViolation(f"Forbidden builtin call: {node.func.id}")
                
            # 3. Ban Dangerous Attribute Access
            if isinstance(node, ast.Attribute):
                if node.attr in ASTGuardrail.BANNED_ATTRS:
                    raise SecurityViolation(f"Forbidden attribute access: {node.attr}")

            # 4. Resource-Enforcement Compliance (Check loops for GLOBAL_BUDGET.enforce)
            if isinstance(node, (ast.For, ast.While)):
                loop_is_safe = False
                for sub_node in ast.walk(node):
                    if isinstance(sub_node, ast.Call):
                        # Looking for GLOBAL_BUDGET.enforce()
                        func = sub_node.func
                        if (isinstance(func, ast.Attribute) and 
                            func.attr == 'enforce' and 
                            isinstance(func.value, ast.Name) and 
                            func.value.id == 'GLOBAL_BUDGET'):
                            loop_is_safe = True
                            break
                if not loop_is_safe:
                    raise SecurityViolation(f"Unbounded loop detected: {ast.dump(node)[:50]}... must call GLOBAL_BUDGET.enforce()")
        
        return True

# ==========================================
# PAYLOAD: PrimeOrganism-0 Search Engine
# ==========================================
def is_probable_prime(n, k=5):
    """
    Miller-Rabin primality test with adaptive rounds and embedded temporal checks.
    """
    if n <= 4:
        return n in (2, 3)
    if n % 2 == 0:
        return False

    s = 0
    d = n - 1
    while d % 2 == 0:
        s += 1
        d //= 2

    for _ in range(k):
        GLOBAL_BUDGET.enforce()
        a = random.randint(2, n - 2)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(s - 1):
            GLOBAL_BUDGET.enforce()
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True

def search_primes():
    """
    Core search loop that scales candidate bit-sizes dynamically and
    evaluates fitness with division-by-zero safeguards.
    """
    bit_size = 16
    start_time = time.time()
    total_attempts = 0
    
    print("Initiating PrimeOrganism-0 Search Engine...")
    while True:
        GLOBAL_BUDGET.enforce()
        
        lower = (1 << (bit_size - 1)) | 1
        upper = (1 << bit_size) - 1
        candidate = random.randint(lower, upper)
        candidate |= 1 
        
        if any(candidate % p == 0 for p in SMALL_PRIMES if candidate > p):
            continue

        total_attempts += 1
        EXECUTION_STATE.total_attempts = total_attempts
        
        if is_probable_prime(candidate, k=5):
            elapsed_time = time.time() - start_time
            safe_elapsed = max(elapsed_time, 0.001)
            safe_attempts = max(total_attempts, 1)
            fitness = bit_size / (safe_attempts * safe_elapsed)
            
            print(f"[FOUND] {bit_size}-bit Prime: {candidate}")
            print(f"        Elapsed: {elapsed_time:.4f}s | Fitness: {fitness:.6f}")
            
            EXECUTION_STATE.best_prime = candidate
            EXECUTION_STATE.bit_size = bit_size
            EXECUTION_STATE.elapsed_time_at_discovery = elapsed_time
            
            remaining_time = GLOBAL_BUDGET.max_time_sec - (time.time() - GLOBAL_BUDGET.start_time)
            time_threshold = 0.15 * GLOBAL_BUDGET.max_time_sec
            
            if remaining_time < time_threshold:
                print(f"[GUARD] Remaining time ({remaining_time:.3f}s) low. Freezing bit-size at {bit_size} bits.")
            else:
                bit_size *= 2

@enforce_budget
def agent_payload():
    """
    PrimeOrganism-0 Payload Execution
    """
    print(f"Budget Enforcer Active. Max Time: {GLOBAL_BUDGET.max_time_sec}s, Max Tokens: {GLOBAL_BUDGET.max_tokens}")
    search_primes()

# ==========================================
# CORE EVOLUTION ENGINE
# ==========================================
def safe_execute_evolution(source_code):
    """
    Validates code using AST Guardrail before execution.
    """
    print(f"AST Gatekeeper: Validating mutation (length: {len(source_code)} chars)...")
    try:
        if ASTGuardrail.validate(source_code):
            print("AST Gatekeeper: Validation PASSED. Executing mutation...")
            exec(source_code, globals())
    except SecurityViolation as e:
        print(f"AST Gatekeeper: REJECTED - {e}")
    except Exception as e:
        print(f"AST Gatekeeper: Runtime error in mutation - {e}")

@enforce_budget
def call_llm_api(prompt_text):
    """
    Simulated LLM API Call wrapped by the Budget Enforcer.
    """
    token_cost = len(prompt_text) // 4
    GLOBAL_BUDGET.consume_tokens(token_cost)
    time.sleep(0.005)
    return "# Evolutionary candidate code block"

@enforce_budget
def evolve():
    """
    Demonstrates the AST Guardrail logic using synthetic test candidates.
    """
    print("\n--- RUNNING EVOLUTIONARY EXPERIMENT ---")
    
    candidates = {
        "Safe Optimization": "import math\nfor i in range(10):\n    GLOBAL_BUDGET.enforce()\n    x = math.sqrt(i)",
        "Malicious Payload": "import os\nos.system('whoami')",
        "Uncooperative Loop": "while True:\n    pass",
        "Reflection Attack": "getattr(GLOBAL_BUDGET, '__dict__')"
    }

    for name, code in candidates.items():
        print(f"\n[TEST] Evaluating candidate: {name}")
        safe_execute_evolution(code)
    
    print("\n--- RESUMING PRIMARY PAYLOAD ---")
    agent_payload()

if __name__ == "__main__":
    try:
        # Launch evolution sequence which incorporates the AST Guardrail
        evolve()
    except BudgetExceededException as e:
        print(f"\n[SUCCESS] Enforcer gracefully interrupted execution: {e}")
        
        if EXECUTION_STATE.best_prime is not None:
            safe_elapsed = max(EXECUTION_STATE.elapsed_time_at_discovery, 0.001)
            safe_attempts = max(EXECUTION_STATE.total_attempts, 1)
            recovered_fitness = EXECUTION_STATE.bit_size / (safe_attempts * safe_elapsed)
            print("--- POST-MORTEM STATE RECOVERY SUCCESSFUL ---")
            print(f"Discovered Prime : {EXECUTION_STATE.best_prime}")
            print(f"Prime Bit-Size   : {EXECUTION_STATE.bit_size}")
            print(f"Discovery Time   : {EXECUTION_STATE.elapsed_time_at_discovery:.4f}s")
            print(f"Final Fitness    : {recovered_fitness:.6f}")
            print(f"Total Attempts   : {EXECUTION_STATE.total_attempts}")
            print("---------------------------------------------")
        else:
            print("\n--- POST-MORTEM RECOVERY: No primes discovered. ---")
            
        print(f"Final Execution Stats: Tokens used = {GLOBAL_BUDGET.tokens_used}, Elapsed = {time.time() - GLOBAL_BUDGET.start_time:.3f}s")
        sys.exit(0)
    except Exception as e:
        print(f"[FATAL ERROR] Unexpected process termination: {e}")
        sys.exit(1)