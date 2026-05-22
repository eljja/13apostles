import os
import sys
import json
import re
import subprocess
import py_compile
import logging
import time
from llm_client import LLMClient
from tree_parser import get_organism_basenames, find_root_seeds

# ─── Configuration Constants ────────────────────────────────────────────────
MAX_CANDIDATES = 20          # Maximum number of candidate proposals per generation
DEFAULT_NUM_CHILDREN = 1     # Default number of children to spawn
MAX_CHILDREN = 5             # Maximum number of children per evolution cycle
JSON_PARSE_MAX_RETRIES = 2   # Retries for JSON parsing from LLM voting responses
JSON_RETRY_DELAY = 1.0       # Base delay (seconds) between JSON parse retries
BASE20_CHARS = "0123456789abcdefghij"  # Character set for candidate IDs

# ─── Logging ─────────────────────────────────────────────────────────────────
class ReverseFileHandler(logging.Handler):
    """
    Custom logging handler that prepends new logs to the top of the file
    so that the newest logs are always visible at the very top.
    """
    def __init__(self, filename, encoding="utf-8"):
        super().__init__()
        self.filename = filename
        self.encoding = encoding

    def emit(self, record):
        try:
            msg = self.format(record) + "\n"
            existing_content = ""
            if os.path.exists(self.filename):
                try:
                    with open(self.filename, "r", encoding=self.encoding, errors="ignore") as f:
                        existing_content = f.read()
                except Exception:
                    pass
            with open(self.filename, "w", encoding=self.encoding) as f:
                f.write(msg + existing_content)
        except Exception:
            self.handleError(record)

logger = logging.getLogger("evolution")
if not logger.handlers:
    # Console Stream Handler
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S"
    ))
    logger.addHandler(stream_handler)

    # Reverse File Handler (Newest logs at the top)
    file_handler = ReverseFileHandler("evolution.log", encoding="utf-8")
    file_handler.setFormatter(logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    ))
    logger.addHandler(file_handler)
    logger.setLevel(logging.INFO)


class EvolutionEngine:
    def __init__(self, workspace_dir, target_file):
        self.workspace_dir = workspace_dir
        self.target_file = target_file
        self.target_basename = os.path.splitext(os.path.basename(target_file))[0]
        self.llm = LLMClient()
        self.apostles = self._load_apostles()
        self.core_objective = self._read_file("CORE_OBJECTIVE.md")
        self.candidate_format = self._read_file("CANDIDATE_FORMAT.md")
        self.voting_format = self._read_file("VOTING_FORMAT.md")
        self.local_objective = self._load_local_objective()

    def _read_file(self, filename):
        path = os.path.join(self.workspace_dir, filename)
        if not os.path.exists(path):
            return ""
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    def _load_apostles(self):
        apostles_dir = os.path.join(self.workspace_dir, "apostles")
        apostles = []
        if not os.path.exists(apostles_dir):
            return apostles
        for filename in sorted(os.listdir(apostles_dir)):
            if filename.endswith(".md"):
                content = self._read_file(os.path.join("apostles", filename))
                name = filename.split("_", 1)[1].replace(".md", "").capitalize()
                apostles.append({"id": filename.split("_")[0], "name": name, "content": content})
        return apostles

    def _find_root_basename(self) -> str:
        """Find the root seed basename for the current target."""
        basenames = get_organism_basenames(self.workspace_dir)
        roots = find_root_seeds(basenames)
        # The root is the shortest basename that is a prefix of target_basename
        prefixes = [r for r in roots if self.target_basename.startswith(r)]
        if prefixes:
            return min(prefixes, key=len)
        return self.target_basename

    def _load_local_objective(self) -> str | None:
        """Load the seed-specific objective file if it exists."""
        root = self._find_root_basename()
        obj_path = os.path.join(self.workspace_dir, f"{root}.objective.md")
        if os.path.exists(obj_path):
            with open(obj_path, 'r', encoding='utf-8') as f:
                return f.read()
        return None

    def _determine_issue_prompt(self):
        local_obj_section = ""
        if self.local_objective:
            local_obj_section = f"\nOrganism-Specific Objective:\n{self.local_objective}\n"

        basenames = get_organism_basenames(self.workspace_dir)
        roots = find_root_seeds(basenames)
        is_root = self.target_basename in roots

        if is_root:
            return (
                f"The system's Core Objective is:\n\n{self.core_objective}"
                f"{local_obj_section}\n"
                f"Propose the most critical first evolutionary step for this program."
            )
        else:
            parent_name = self.target_basename[:-1]
            parent_md = self._read_file(f"{parent_name}.md")
            if parent_md:
                return (
                    f"The previous evolutionary decision that led to the current version:\n\n{parent_md}"
                    f"{local_obj_section}\n"
                    f"Propose the next logical evolutionary step."
                )
            else:
                return (
                    f"The system's Core Objective is:\n\n{self.core_objective}"
                    f"{local_obj_section}\n"
                    f"Propose the next evolutionary step for this program."
                )

    def get_current_branch(self):
        result = subprocess.run(["git", "branch", "--show-current"], capture_output=True, text=True, cwd=self.workspace_dir)
        return result.stdout.strip()

    def generate_candidates(self, target_code, issue_prompt):
        logger.info("--- Phase 1: Candidate Generation ---")
        candidates_raw = []

        for apostle in self.apostles:
            logger.info(f"Asking {apostle['name']} Apostle for a proposal...")
            local_obj_section = ""
            if self.local_objective:
                local_obj_section = f"\nOrganism-Specific Objective:\n{self.local_objective}\n"

            prompt = f"""
You are the {apostle['name']} Apostle.
Your Persona:
{apostle['content']}

System Core Objective:
{self.core_objective}{local_obj_section}
Current Target Code ({self.target_file}):
```python
{target_code}
```

Evolution Issue:
{issue_prompt}

Based on your persona, propose exactly ONE evolutionary improvement to the target code above.
You MUST output ONLY the candidate following this exact markdown format, nothing else:

{self.candidate_format}
"""
            try:
                response, _ = self.llm.generate_content(prompt)
                candidates_raw.append(response.strip())
            except Exception as e:
                logger.warning(f"Failed to get proposal from {apostle['name']}: {e}")

        logger.info(f"Aggregating {len(candidates_raw)} candidates...")
        final_candidates = []
        for i, c_text in enumerate(candidates_raw):
            if i >= MAX_CANDIDATES:
                break
            char_id = BASE20_CHARS[i]

            title_match = re.search(r'## Candidate Name\s*\n(.*?)\n', c_text, re.IGNORECASE)
            title = title_match.group(1).strip() if title_match else f"Proposal from Apostle {i+1}"

            final_candidates.append({
                "id": char_id,
                "title": title,
                "content": c_text
            })

        return final_candidates

    def conduct_voting(self, candidates):
        logger.info("--- Phase 2: Voting & Evaluation ---")
        votes_data = {}

        candidates_text = "".join([
            f"\n\n============================\nCANDIDATE ID: {c['id']}\n============================\n{c['content']}"
            for c in candidates
        ])

        for apostle in self.apostles:
            logger.info(f"[{apostle['name']} Apostle] is evaluating and voting...")
            prompt = f"""
You are the {apostle['name']} Apostle.
Your Persona:
{apostle['content']}

System Core Objective:
{self.core_objective}

Voting Rules:
{self.voting_format}

Here are the candidates:
{candidates_text}

Task: Evaluate the candidates according to the Voting Rules. You have 10 points per category (5 categories).
If a candidate poses extreme danger according to your persona, set veto to true.
Output ONLY valid JSON in the following format (no markdown, just raw JSON):
[
  {{
    "candidate_id": "0",
    "impact_score": 5,
    "feasibility_score": 3,
    "alignment_score": 4,
    "safety_multiplier": 1.0,
    "cost_multiplier": 1.5,
    "reason": "Explain your scores here",
    "veto": false
  }}
]
"""
            parsed = False
            for retry in range(JSON_PARSE_MAX_RETRIES + 1):
                try:
                    response, _ = self.llm.generate_content(prompt)
                    response = response.replace("```json", "").replace("```", "").strip()
                    # Try to extract JSON array from response if it contains extra text
                    json_match = re.search(r'\[.*\]', response, re.DOTALL)
                    json_str = json_match.group(0) if json_match else response
                    vote_json = json.loads(json_str)
                    votes_data[apostle['name']] = vote_json
                    parsed = True
                    break
                except json.JSONDecodeError as e:
                    logger.warning(f"JSON parse error from {apostle['name']} (attempt {retry+1}/{JSON_PARSE_MAX_RETRIES+1}): {e}")
                    if retry < JSON_PARSE_MAX_RETRIES:
                        time.sleep(JSON_RETRY_DELAY * (2 ** retry))
                except Exception as e:
                    logger.error(f"Failed to get vote from {apostle['name']}: {e}")
                    break
            if not parsed:
                logger.error(f"All retries exhausted for {apostle['name']}. Skipping this apostle's vote.")

        return votes_data

    def calculate_results(self, candidates, votes_data):
        logger.info("--- Phase 3: Final Selection ---")
        scores = {c['id']: {"impact": 0, "feasibility": 0, "alignment": 0, "safety": 0, "cost": 0, "veto": False} for c in candidates}
        vetoes = []

        for apostle_name, votes in votes_data.items():
            for v in votes:
                c_id = str(v.get('candidate_id'))
                if c_id not in scores:
                    continue

                if v.get('veto', False):
                    scores[c_id]['veto'] = True
                    vetoes.append((c_id, apostle_name, v.get('reason', 'Unknown reason')))

                scores[c_id]['impact'] += v.get('impact_score', 0)
                scores[c_id]['feasibility'] += v.get('feasibility_score', 0)
                scores[c_id]['alignment'] += v.get('alignment_score', 0)
                scores[c_id]['safety'] += v.get('safety_multiplier', 1)
                scores[c_id]['cost'] += v.get('cost_multiplier', 1)

        final_results = []
        for c in candidates:
            c_id = c['id']
            s = scores[c_id]
            if s['veto']:
                final_score = 0
            else:
                cost = max(s['cost'], 1)
                final_score = (s['impact'] * s['feasibility'] * s['alignment'] * s['safety']) / cost

            final_results.append({
                "id": c_id, "title": c['title'], "scores": s,
                "final_score": final_score, "vetoed": s['veto']
            })

        final_results.sort(key=lambda x: x['final_score'], reverse=True)

        logger.info("Results:")
        for r in final_results:
            v_text = "(VETOED)" if r['vetoed'] else f"Score: {r['final_score']:.2f}"
            logger.info(f"  [{r['id']}] {r['title']}: {v_text}")

        return final_results, vetoes

    def mutate_code(self, target_code, winner, candidates):
        logger.info(f"--- Phase 4: Code Mutation ({winner['id']}) ---")
        winner_content = next(c['content'] for c in candidates if c['id'] == winner['id'])

        prompt = f"""
You are the Master Coder Apostle.
Your task is to take the current Python program and modify it to implement the winning evolutionary candidate.

Winning Candidate Details:
{winner_content}

Current Source Code:
```python
{target_code}
```

Instructions:
1. Implement the changes described in the winning candidate into the code.
2. The output must be a complete, valid, executable Python program.
3. Return ONLY the raw Python code. Do NOT wrap it in markdown code blocks.
"""
        logger.info("Requesting code mutation from LLM...")
        try:
            new_code, _ = self.llm.generate_content(prompt)
            new_code = new_code.replace("```python", "").replace("```", "").strip()
            return new_code
        except Exception as e:
            logger.error(f"Code generation failed: {e}")
            return None

    def _write_decision_log(self, candidates, final_results, vetoes, votes_data, children_info):
        """Write the decision log markdown file."""
        decision_log_path = os.path.join(self.workspace_dir, f"{self.target_basename}.md")
        with open(decision_log_path, "w", encoding="utf-8") as f:
            f.write(f"# Decision Log: {self.target_basename}.py\n\n")
            f.write("## Candidates Proposed\n")
            for c in candidates:
                f.write(f"\n### [{c['id']}] {c['title']}\n```markdown\n{c['content']}\n```\n")
            f.write("\n## Voting Results\n")
            for r in final_results:
                f.write(f"- **[{r['id']}] {r['title']}** -> Final Score: {r['final_score']:.2f} | Vetoed: {r['vetoed']}\n")
            if vetoes:
                f.write("\n## Vetoes\n")
                for v in vetoes:
                    f.write(f"- Candidate {v[0]} vetoed by {v[1]}: {v[2]}\n")
            f.write("\n## Children Spawned\n")
            if not children_info:
                f.write("\n⚠️ **ALL DROPPED** — No viable children were spawned in this generation.\n")
            for ci in children_info:
                f.write(f"- **{ci['filename']}** <- [{ci['id']}] {ci['title']}\n")
            f.write("\n## Raw Votes Data\n```json\n")
            f.write(json.dumps(votes_data, indent=2, ensure_ascii=False))
            f.write("\n```\n")
        return decision_log_path

    def _spawn_child(self, winner, candidates, target_code):
        """Mutate the code for a single winner and write the child .py file."""
        new_name = f"{self.target_basename}{winner['id']}"
        new_filename = f"{new_name}.py"
        new_filepath = os.path.join(self.workspace_dir, new_filename)

        if os.path.exists(new_filepath):
            logger.info(f"Child file '{new_filename}' already exists. Skipping LLM generation and reusing existing file.")
            return {"id": winner['id'], "title": winner['title'], "filename": new_filename, "name": new_name}

        new_code = self.mutate_code(target_code, winner, candidates)
        if not new_code:
            logger.warning(f"Mutation failed for {new_filename}. Skipping.")
            return None

        with open(new_filepath, "w", encoding="utf-8") as f:
            f.write(new_code)

        try:
            py_compile.compile(new_filepath, doraise=True)
            logger.info(f"Syntax check passed for {new_filename}.")
        except py_compile.PyCompileError as e:
            logger.error(f"SYNTAX ERROR in {new_filename}. Skipping.\n{e}")
            os.remove(new_filepath)
            return None

        return {"id": winner['id'], "title": winner['title'], "filename": new_filename, "name": new_name}

    def run(self, num_children=1):
        """Run one evolution cycle, spawning up to num_children branches."""
        target_path = os.path.join(self.workspace_dir, self.target_file)
        if not os.path.exists(target_path):
            logger.error(f"Target file '{self.target_file}' not found.")
            return []

        with open(target_path, "r", encoding="utf-8") as f:
            target_code = f.read()

        logger.info(f"Target: {self.target_file}")
        logger.debug(f"Current code:\n---\n{target_code}\n---")

        issue_prompt = self._determine_issue_prompt()

        candidates = self.generate_candidates(target_code, issue_prompt)
        if not candidates:
            return []

        votes_data = self.conduct_voting(candidates)
        final_results, vetoes = self.calculate_results(candidates, votes_data)

        # Select top N non-vetoed candidates as children
        valid_results = [r for r in final_results if not r['vetoed']]
        winners = valid_results[:num_children]

        children_info = []
        if not winners:
            logger.warning("ALL CANDIDATES DROPPED. No children spawned.")
        else:
            logger.info(f"--- Spawning {len(winners)} children ---")
            for w in winners:
                child = self._spawn_child(w, candidates, target_code)
                if child:
                    children_info.append(child)

        # Always write decision log (even on all-drop)
        self._write_decision_log(candidates, final_results, vetoes, votes_data, children_info)

        # Git: commit all changes on the current branch (DISABLED BY USER)
        # subprocess.run(["git", "add", "."], cwd=self.workspace_dir)
        # if children_info:
        #     child_names = ", ".join([c['filename'] for c in children_info])
        #     commit_msg = f"Evolve {self.target_basename}: spawn {child_names}"
        # else:
        #     commit_msg = f"Evolve {self.target_basename}: all dropped"
        # subprocess.run(["git", "commit", "-m", commit_msg], cwd=self.workspace_dir)

        logger.info(f"Evolution complete!")
        logger.info(f"  Decision log: {self.target_basename}.md")
        for ci in children_info:
            logger.info(f"  Child: {ci['filename']} <- [{ci['id']}] {ci['title']}")

        return children_info


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python evolution.py <target.py> [--children N] [--test]")
        print(f"  --children N  Spawn top N children (default: {DEFAULT_NUM_CHILDREN}, max: {MAX_CHILDREN})")
        print("  --test        Use only 3 apostles for faster testing")
        print("Example: python evolution.py 0.py --children 3")
        sys.exit(1)

    target = sys.argv[1]
    test_mode = "--test" in sys.argv
    num_children = DEFAULT_NUM_CHILDREN
    if "--children" in sys.argv:
        idx = sys.argv.index("--children")
        if idx + 1 < len(sys.argv):
            num_children = min(int(sys.argv[idx + 1]), MAX_CHILDREN)

    engine = EvolutionEngine(os.getcwd(), target)
    if test_mode:
        engine.apostles = engine.apostles[:3]
        logger.info(f"[TEST MODE] Using only {len(engine.apostles)} apostles: {[a['name'] for a in engine.apostles]}")
    engine.run(num_children=num_children)
