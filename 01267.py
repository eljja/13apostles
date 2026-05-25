import os
import sys
import time
import random
import ast
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

# ==========================================
# AST-BASED SECURITY SANDBOX GUARDRAIL
# ==========================================
class SecurityASTVisitor(ast.NodeVisitor):
    def __init__(self):
        self.safe = True
        self.violations = []
        # Mathematical, temporal, and safe structural library whitelist
        self.allowed_imports = {'math', 'time', 'random', 'sys', 'typing', 'functools', 'collections'}

    def visit_Import(self, node):
        for alias in node.names:
            root_module = alias.name.split('.')[0]
            if root_module not in self.allowed_imports:
                self.safe = False
                self.violations.append(f"Unauthorized import: {alias.name}")
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module:
            root_module = node.module.split('.')[0]
            if root_module not in self.allowed_imports:
                self.safe = False
                self.violations.append(f"Unauthorized from-import: {node.module}")
        self.generic_visit(node)

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            if node.func.id in {'eval', 'exec', 'compile', 'open', 'getattr'}:
                self.safe = False
                self.violations.append(f"Forbidden function call: {node.func.id}")
        self.generic_visit(node)

    def visit_Attribute(self, node):
        if node.attr in {'__globals__', '__subclasses__'} or node.attr.startswith('__'):
            self.safe = False
            self.violations.append(f"Forbidden dunder attribute access: {node.attr}")
        self.generic_visit(node)

    def visit_For(self, node):
        if not self._has_budget_enforce(node):
            self.safe = False
            self.violations.append("For loop missing mandatory GLOBAL_BUDGET.enforce() call")
        self.generic_visit(node)

    def visit_While(self, node):
        if not self._has_budget_enforce(node):
            self.safe = False
            self.violations.append("While loop missing mandatory GLOBAL_BUDGET.enforce() call")
        self.generic_visit(node)

    def _has_budget_enforce(self, loop_node):
        for child in ast.walk(loop_node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Attribute):
                    if isinstance(child.func.value, ast.Name) and child.func.value.id == 'GLOBAL_BUDGET':
                        if child.func.attr == 'enforce':
                            return True
        return False

def validate_code_safety(code_str):
    """
    Statically analyzes code structure to ensure compatibility with isolation guardrails.
    """
    try:
        tree = ast.parse(code_str)
        visitor = SecurityASTVisitor()
        visitor.visit(tree)
        return visitor.safe, visitor.violations
    except SyntaxError as e:
        return False, [f"Syntax Error: {e}"]

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
        
        total_attempts += 1
        EXECUTION_STATE.total_attempts = total_attempts
        
        if is_probable_prime(candidate, k=5):
            elapsed_time = time.time() - start_time
            safe_elapsed = max(elapsed_time, 0.001)
            fitness = bit_size / safe_elapsed
            
            print(f"[FOUND] {bit_size}-bit Prime: {candidate}")
            print(f"        Elapsed: {elapsed_time:.4f}s | Fitness (bits/sec): {fitness:.2f}")
            
            EXECUTION_STATE.best_prime = candidate
            EXECUTION_STATE.bit_size = bit_size
            EXECUTION_STATE.elapsed_time_at_discovery = elapsed_time
            
            remaining_time = GLOBAL_BUDGET.max_time_sec - (time.time() - GLOBAL_BUDGET.start_time)
            time_threshold = 0.15 * GLOBAL_BUDGET.max_time_sec
            
            if remaining_time < time_threshold:
                print(f"[GUARD] Remaining time ({remaining_time:.3f}s) < threshold ({time_threshold:.3f}s). Freezing bit-size scaling at {bit_size} bits.")
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
@enforce_budget
def call_llm_api(prompt_text):
    """
    Simulated LLM API Call wrapped by the Budget Enforcer.
    """
    token_cost = len(prompt_text) // 4
    GLOBAL_BUDGET.consume_tokens(token_cost)
    time.sleep(0.005)
    return f"# Evolved code based on {token_cost} tokens."

@enforce_budget
def evolve():
    """
    Evolution engine equipped with static AST validation and runtime execution guards.
    Runs verification suite prior to payload execution to protect host runtime.
    """
    print("Initiating Evolution Guardrail Self-Test...")
    
    # Validation Test Cases covering standard safety limits
    test_cases = {
        "Valid Mathematical Candidate": """
def safe_math_evolution():
    import math
    for i in range(10):
        GLOBAL_BUDGET.enforce()
        temp = math.factorial(i % 5)
""",
        "Malicious Dynamic Execution Attempt": """
eval("print('System compromise')")
""",
        "Malicious System Import Attempt": """
import os
os.system("echo compromised")
""",
        "Malicious Dunder Reflection Attack": """
object.__subclasses__()
""",
        "Uncooperative Infinite Loop Candidate": """
while True:
    pass
"""
    }

    for name, code in test_cases.items():
        is_safe, violations = validate_code_safety(code)
        print(f"  Testing Payload: '{name}'")
        if is_safe:
            print("    [APPROVED] Code passed security standards.")
        else:
            print("    [BLOCKED] Code violated safety guardrails.")
            for violation in violations:
                print(f"      - {violation}")

    print("\nEvolution Guardrail Verification Complete. Transitioning to search payload...")
    agent_payload()

if __name__ == "__main__":
    try:
        # Launch evolutionary system wrapper
        evolve()
    except BudgetExceededException as e:
        print(f"\n[SUCCESS] Enforcer gracefully interrupted execution: {e}")
        
        # Post-Mortem Recovery Handler
        if EXECUTION_STATE.best_prime is not None:
            safe_elapsed = max(EXECUTION_STATE.elapsed_time_at_discovery, 0.001)
            recovered_fitness = EXECUTION_STATE.bit_size / safe_elapsed
            print("--- POST-MORTEM STATE RECOVERY SUCCESSFUL ---")
            print(f"Discovered Prime : {EXECUTION_STATE.best_prime}")
            print(f"Prime Bit-Size   : {EXECUTION_STATE.bit_size}")
            print(f"Discovery Time   : {EXECUTION_STATE.elapsed_time_at_discovery:.4f}s")
            print(f"Final Fitness    : {recovered_fitness:.2f} bits/sec")
            print(f"Total Attempts   : {EXECUTION_STATE.total_attempts}")
            print("---------------------------------------------")
        else:
            print("\n--- POST-MORTEM RECOVERY: No primes were discovered before interruption. ---")
            
        print(f"Final Execution Stats: Tokens used = {GLOBAL_BUDGET.tokens_used}, Elapsed = {time.time() - GLOBAL_BUDGET.start_time:.3f}s")
        sys.exit(0)
    except Exception as e:
        print(f"[FATAL ERROR] Unexpected process termination: {e}")
        sys.exit(1)