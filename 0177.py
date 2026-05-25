import os
import sys
import time
import subprocess
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

# Establish hardcoded resource limits for the session (5.0s per candidate proposal description)
GLOBAL_BUDGET = ResourceBudgetTracker(max_tokens=10000, max_time_sec=5.0)

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
# SUBPROCESS SANDBOX RUNNER WITH HARD TIMEOUT
# ==========================================
@enforce_budget
def run_payload_in_sandbox(code_content, filename="sandbox_payload.py", timeout_sec=1.5):
    """
    Executes the candidate code in an isolated subprocess with a hard OS-level timeout.
    Safely captures and sanitizes output, preventing parent thread hangs or pollution.
    """
    target_path = safe_write(filename, code_content)
    start_time = time.time()
    
    # Use process group isolation under Unix to prevent child process leaking
    kwargs = {}
    if os.name == 'posix':
        kwargs['preexec_fn'] = os.setsid

    proc = subprocess.Popen(
        [sys.executable, target_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        **kwargs
    )
    
    try:
        stdout, stderr = proc.communicate(timeout=timeout_sec)
        duration = time.time() - start_time
        return {
            "success": proc.returncode == 0,
            "returncode": proc.returncode,
            "stdout": stdout,
            "stderr": stderr,
            "duration": duration,
            "timeout_triggered": False
        }
    except subprocess.TimeoutExpired:
        # Hard OS-level termination
        if os.name == 'posix':
            import signal
            try:
                # Forcefully kill the entire subprocess group
                os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
            except ProcessLookupError:
                pass
        else:
            proc.kill()
            
        # Reap standard outputs post-termination
        stdout, stderr = proc.communicate()
        duration = time.time() - start_time
        return {
            "success": False,
            "returncode": -1,
            "stdout": stdout,
            "stderr": stderr,
            "duration": duration,
            "timeout_triggered": True
        }

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
def runaway_sandbox_experiment():
    """
    Experiment Method: Runs a deliberate, non-cooperative infinite loop
    inside the subprocess sandbox to verify OS-level timeout enforcement.
    """
    print("\n[SANDBOX TEST] Initiating non-cooperative runaway loop experiment...")
    runaway_code = (
        "import time\n"
        "print('Child process started. Entering non-cooperative infinite loop...')\n"
        "while True:\n"
        "    pass\n"
    )
    
    # Run the non-cooperative script in the sandbox with a 1.5 second hard timeout
    test_timeout = 1.5
    result = run_payload_in_sandbox(runaway_code, "runaway_payload.py", timeout_sec=test_timeout)
    
    if result["timeout_triggered"]:
        print(f"[SUCCESS] Sandbox intercepted and terminated the runaway loop!")
        print(f"Captured Stdout prior to termination:\n---\n{result['stdout'].strip()}\n---")
        print(f"Execution terminated forcibly after {result['duration']:.3f} seconds.")
    else:
        print(f"[FAILURE] Runaway loop was not terminated by timeout! Exit code: {result['returncode']}")
        if result['stderr']:
            print(f"Error output: {result['stderr']}")

@enforce_budget
def cooperative_sandbox_experiment():
    """
    Runs a cooperative evolution payload in the sandbox and extracts performance
    metrics via structured standard output parsing.
    """
    print("\n[SANDBOX TEST] Initiating cooperative payload execution and metric parsing...")
    cooperative_code = (
        "import json\n"
        "print('Running evolved algorithm...')\n"
        "metrics = {'best_bits': [1, 0, 1, 1, 0], 'total_attempts': 42}\n"
        "print('METRICS_JSON:' + json.dumps(metrics))\n"
    )
    
    result = run_payload_in_sandbox(cooperative_code, "cooperative_payload.py", timeout_sec=2.0)
    if result["success"]:
        print("[SUCCESS] Sandbox execution completed successfully.")
        # Extract metrics safely from standard output
        metrics = None
        for line in result["stdout"].splitlines():
            if line.startswith("METRICS_JSON:"):
                import json
                try:
                    metrics = json.loads(line[len("METRICS_JSON:"):])
                except json.JSONDecodeError:
                    pass
        print(f"Parsed metrics from sandbox: {metrics}")
    else:
        print(f"[FAILURE] Sandbox execution failed. Error: {result['stderr']}")

@enforce_budget
def evolve():
    """
    Core self-modification logic with resilient cleanup and security validation.
    """
    print("Running CORE EVOLUTION ENGINE with Subprocess Sandboxing...")
    
    try:
        # 1. Security Test: Programmatically attempt out-of-bounds write
        print("\n[SECURITY TEST] Testing path-traversal resilience...")
        try:
            safe_write("../unauthorized_payload.py", "malicious_code = True")
            print("[FAILURE] Security Test failed! Unauthorized write allowed.")
        except PermissionError as e:
            print(f"[SUCCESS] Security Test blocked out-of-bounds write: {e}")
            
        # 2. Execute runaway loop experiment inside sandbox (OS-level timeout guard)
        runaway_sandbox_experiment()
        
        # 3. Execute cooperative performance parsing experiment
        cooperative_sandbox_experiment()
        
    except BudgetExceededException as e:
        print(f"\n[FATAL] Parent process budget exceeded: {e}")
    finally:
        # Exception-Resilient Cleanup of workspace contents
        print("\nExecuting cleanup pipeline...")
        temp_files = ["runaway_payload.py", "cooperative_payload.py", "sandbox_payload.py"]
        for filename in temp_files:
            try:
                target_path = validate_and_resolve_path(filename)
                if os.path.exists(target_path):
                    os.remove(target_path)
                    print(f"[SUCCESS] Cleaned up temporary file: {target_path}")
            except Exception as cleanup_err:
                print(f"[ERROR] Clean up sequence failed for {filename}: {cleanup_err}")

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