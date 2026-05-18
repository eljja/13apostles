import os
import sys
import json
import re
import subprocess
import py_compile
from llm_client import LLMClient

# ==============================================================================
# PAYLOAD: AI Task Automation Engine
# ==============================================================================
def agent_payload():
    """
    This is the core automation agent. Currently, it is a basic stub.
    Future evolutionary generations will expand this function or add classes 
    to perform complex local tasks, monitor files, and execute natural language commands.
    """
    print("AI Task Automation Engine payload is currently running.")
    # Placeholder for future automation logic


# ==============================================================================
# CORE EVOLUTION ENGINE
# ==============================================================================
class EvolutionEngine:
    def __init__(self, workspace_dir):
        self.workspace_dir = workspace_dir
        self.llm = LLMClient()
        self.apostles = self._load_apostles()
        self.core_objective = self._read_file("CORE_OBJECTIVE.md")
        self.candidate_format = self._read_file("CANDIDATE_FORMAT.md")
        self.voting_format = self._read_file("VOTING_FORMAT.md")

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

    def get_current_branch(self):
        result = subprocess.run(["git", "branch", "--show-current"], capture_output=True, text=True, cwd=self.workspace_dir)
        return result.stdout.strip()

    def generate_candidates(self, current_state_description, issue_prompt):
        print("\n--- Phase 1: Candidate Generation ---")
        candidates_raw = []
        
        for apostle in self.apostles:
            print(f"Asking {apostle['name']} Apostle for a proposal...")
            prompt = f"""
You are the {apostle['name']} Apostle.
Your Persona:
{apostle['content']}

System Core Objective:
{self.core_objective}

Current System State:
{current_state_description}

Task: {issue_prompt}
Based on your persona, propose exactly ONE evolutionary candidate to address the task.
You MUST output ONLY the candidate following this exact markdown format, nothing else:

{self.candidate_format}
"""
            try:
                response, _ = self.llm.generate_content(prompt)
                candidates_raw.append(response.strip())
            except Exception as e:
                print(f"Failed to get proposal from {apostle['name']}: {e}")

        print("Aggregating candidates...")
        base20_chars = "0123456789abcdefghij"
        final_candidates = []
        for i, c_text in enumerate(candidates_raw):
            if i >= 20: break
            char_id = base20_chars[i]
            
            title_match = re.search(r'## Candidate Name\s*\n(.*?)\n', c_text, re.IGNORECASE)
            title = title_match.group(1).strip() if title_match else f"Proposal from Apostle {i+1}"
            
            final_candidates.append({
                "id": char_id,
                "title": title,
                "content": c_text
            })
            
        return final_candidates

    def conduct_voting(self, candidates):
        print("\n--- Phase 2: Voting & Evaluation ---")
        votes_data = {}
        
        candidates_text = "".join([f"\n\n============================\nCANDIDATE ID: {c['id']}\n============================\n{c['content']}" for c in candidates])

        for apostle in self.apostles:
            print(f"[{apostle['name']} Apostle] is evaluating and voting...")
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
Output ONLY valid JSON in the following format:
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
            try:
                response, _ = self.llm.generate_content(prompt)
                response = response.replace("```json", "").replace("```", "").strip()
                vote_json = json.loads(response)
                votes_data[apostle['name']] = vote_json
            except Exception as e:
                print(f"Failed to get vote from {apostle['name']}: {e}")
                
        return votes_data

    def calculate_results(self, candidates, votes_data):
        print("\n--- Phase 3: Final Selection ---")
        scores = {c['id']: {"impact": 0, "feasibility": 0, "alignment": 0, "safety": 0, "cost": 0, "veto": False} for c in candidates}
        vetoes = []
        
        for apostle_name, votes in votes_data.items():
            for v in votes:
                c_id = str(v.get('candidate_id'))
                if c_id not in scores: continue
                
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
                "id": c_id, "title": c['title'], "scores": s, "final_score": final_score, "vetoed": s['veto']
            })
            
        final_results.sort(key=lambda x: x['final_score'], reverse=True)
        
        print("\nResults:")
        for r in final_results:
            v_text = "(VETOED)" if r['vetoed'] else f"Score: {r['final_score']:.2f}"
            print(f"- [{r['id']}] {r['title']}: {v_text}")
            
        winner = final_results[0] if not final_results[0]['vetoed'] else None
        if winner: print(f"\nWINNER: [{winner['id']}] {winner['title']}")
        else: print("\nALL TOP CANDIDATES VETOED.")
            
        return winner, final_results, vetoes

    def mutate_codebase(self, winner, candidates):
        print(f"\n--- Phase 4: Code Mutation ({winner['id']}) ---")
        winner_content = next(c['content'] for c in candidates if c['id'] == winner['id'])
        
        current_script_path = os.path.abspath(__file__)
        with open(current_script_path, "r", encoding="utf-8") as f:
            current_code = f.read()

        prompt = f"""
You are the Master Coder Apostle.
Your task is to take the current Python codebase of this evolutionary engine and modify it to implement the winning evolutionary candidate's features.

Winning Candidate Details:
{winner_content}

Current Source Code ({current_script_path}):
```python
{current_code}
```

Instructions:
1. Integrate the requested feature into the `PAYLOAD` section (e.g., expand `agent_payload()`).
2. DO NOT break the `CORE EVOLUTION ENGINE` logic. The program must still be able to evolve.
3. Return ONLY the complete, newly modified, valid, executable Python code.
4. Do not wrap the output in markdown blocks (e.g. ```python). Just return the raw code.
"""
        print("Requesting code mutation from LLM...")
        try:
            new_code, _ = self.llm.generate_content(prompt)
            new_code = new_code.replace("```python", "").replace("```", "").strip()
            return new_code
        except Exception as e:
            print(f"Code generation failed: {e}")
            return None

    def apply_decision(self, current_branch, winner, candidates, votes_data, final_results, vetoes):
        if not winner: return

        new_branch = f"{current_branch}{winner['id']}"
        new_filename = f"{new_branch}.py"
        print(f"\nApplying decision: Evolving to {new_filename}")
        
        # 1. Mutate Code
        new_code = self.mutate_codebase(winner, candidates)
        if not new_code:
            print("Mutation failed. Aborting.")
            return
            
        new_filepath = os.path.join(self.workspace_dir, new_filename)
        with open(new_filepath, "w", encoding="utf-8") as f:
            f.write(new_code)
            
        # 2. Syntax Check
        try:
            py_compile.compile(new_filepath, doraise=True)
            print(f"Syntax check passed for {new_filename}.")
        except py_compile.PyCompileError as e:
            print(f"SYNTAX ERROR IN MUTATED CODE. Aborting evolution.\n{e}")
            os.remove(new_filepath)
            return

        # 3. Write Decision Log
        decision_log_path = os.path.join(self.workspace_dir, f"{current_branch}.md")
        with open(decision_log_path, "w", encoding="utf-8") as f:
            f.write(f"# Decision Log for Evolution from {current_branch}.py to {new_filename}\n\n")
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
            f.write("\n## Raw Votes Data\n```json\n")
            f.write(json.dumps(votes_data, indent=2, ensure_ascii=False))
            f.write("\n```\n")
            
        # 4. Git operations
        subprocess.run(["git", "checkout", "-b", new_branch], cwd=self.workspace_dir)
        subprocess.run(["git", "add", "."], cwd=self.workspace_dir)
        subprocess.run(["git", "commit", "-m", f"Evolve to {new_branch}: {winner['title']}"], cwd=self.workspace_dir)
        
        print(f"Evolution complete. Please run `python {new_filename}` to continue.")

    def run(self, issue_prompt):
        # Always run payload first
        agent_payload()

        print("\nChecking for evolution triggers...")
        current_branch = self.get_current_branch()
        current_state_description = "The system is currently an AI Task Automation Engine basic stub, capable of self-modifying its own code to evolve."
            
        candidates = self.generate_candidates(current_state_description, issue_prompt)
        if not candidates: return
            
        votes_data = self.conduct_voting(candidates)
        winner, final_results, vetoes = self.calculate_results(candidates, votes_data)
        
        self.apply_decision(current_branch, winner, candidates, votes_data, final_results, vetoes)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 0.py <issue_prompt>")
        sys.exit(1)
        
    engine = EvolutionEngine(os.getcwd())
    engine.run(sys.argv[1])
