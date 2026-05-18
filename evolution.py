import os
import sys
import json
import re
import subprocess
import py_compile
from llm_client import LLMClient


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

    def _determine_issue_prompt(self):
        if len(self.target_basename) <= 1:
            return f"The system's Core Objective is:\n\n{self.core_objective}\n\nPropose the most critical first evolutionary step for this program."
        else:
            parent_name = self.target_basename[:-1]
            parent_md = self._read_file(f"{parent_name}.md")
            if parent_md:
                return f"The previous evolutionary decision that led to the current version:\n\n{parent_md}\n\nPropose the next logical evolutionary step."
            else:
                return f"The system's Core Objective is:\n\n{self.core_objective}\n\nPropose the next evolutionary step for this program."

    def get_current_branch(self):
        result = subprocess.run(["git", "branch", "--show-current"], capture_output=True, text=True, cwd=self.workspace_dir)
        return result.stdout.strip()

    def generate_candidates(self, target_code, issue_prompt):
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
                print(f"Failed to get proposal from {apostle['name']}: {e}")

        print(f"Aggregating {len(candidates_raw)} candidates...")
        base20_chars = "0123456789abcdefghij"
        final_candidates = []
        for i, c_text in enumerate(candidates_raw):
            if i >= 20:
                break
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

        candidates_text = "".join([
            f"\n\n============================\nCANDIDATE ID: {c['id']}\n============================\n{c['content']}"
            for c in candidates
        ])

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

        print("\nResults:")
        for r in final_results:
            v_text = "(VETOED)" if r['vetoed'] else f"Score: {r['final_score']:.2f}"
            print(f"- [{r['id']}] {r['title']}: {v_text}")

        return final_results, vetoes

    def mutate_code(self, target_code, winner, candidates):
        print(f"\n--- Phase 4: Code Mutation ({winner['id']}) ---")
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
        print("Requesting code mutation from LLM...")
        try:
            new_code, _ = self.llm.generate_content(prompt)
            new_code = new_code.replace("```python", "").replace("```", "").strip()
            return new_code
        except Exception as e:
            print(f"Code generation failed: {e}")
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

        new_code = self.mutate_code(target_code, winner, candidates)
        if not new_code:
            print(f"Mutation failed for {new_filename}. Skipping.")
            return None

        with open(new_filepath, "w", encoding="utf-8") as f:
            f.write(new_code)

        try:
            py_compile.compile(new_filepath, doraise=True)
            print(f"Syntax check passed for {new_filename}.")
        except py_compile.PyCompileError as e:
            print(f"SYNTAX ERROR in {new_filename}. Skipping.\n{e}")
            os.remove(new_filepath)
            return None

        return {"id": winner['id'], "title": winner['title'], "filename": new_filename, "name": new_name}

    def run(self, num_children=1):
        """Run one evolution cycle, spawning up to num_children branches."""
        target_path = os.path.join(self.workspace_dir, self.target_file)
        if not os.path.exists(target_path):
            print(f"Error: Target file '{self.target_file}' not found.")
            return []

        with open(target_path, "r", encoding="utf-8") as f:
            target_code = f.read()

        print(f"Target: {self.target_file}")
        print(f"Current code:\n---\n{target_code}\n---")

        issue_prompt = self._determine_issue_prompt()

        candidates = self.generate_candidates(target_code, issue_prompt)
        if not candidates:
            return []

        votes_data = self.conduct_voting(candidates)
        final_results, vetoes = self.calculate_results(candidates, votes_data)

        # Select top N non-vetoed candidates as children
        valid_results = [r for r in final_results if not r['vetoed']]
        winners = valid_results[:num_children]

        if not winners:
            print("ALL CANDIDATES VETOED. No children spawned.")
            return []

        print(f"\n--- Spawning {len(winners)} children ---")
        children_info = []
        for w in winners:
            child = self._spawn_child(w, candidates, target_code)
            if child:
                children_info.append(child)

        # Write decision log
        self._write_decision_log(candidates, final_results, vetoes, votes_data, children_info)

        # Git: commit all changes on the current branch
        subprocess.run(["git", "add", "."], cwd=self.workspace_dir)
        child_names = ", ".join([c['filename'] for c in children_info])
        subprocess.run(["git", "commit", "-m",
                         f"Evolve {self.target_basename}: spawn {child_names}"],
                        cwd=self.workspace_dir)

        print(f"\nEvolution complete!")
        print(f"  Decision log: {self.target_basename}.md")
        for ci in children_info:
            print(f"  Child: {ci['filename']} <- [{ci['id']}] {ci['title']}")

        return children_info


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python evolution.py <target.py> [--children N] [--test]")
        print("  --children N  Spawn top N children (default: 1, max: 5)")
        print("  --test        Use only 3 apostles for faster testing")
        print("Example: python evolution.py 0.py --children 3")
        sys.exit(1)

    target = sys.argv[1]
    test_mode = "--test" in sys.argv
    num_children = 1
    if "--children" in sys.argv:
        idx = sys.argv.index("--children")
        if idx + 1 < len(sys.argv):
            num_children = min(int(sys.argv[idx + 1]), 5)

    engine = EvolutionEngine(os.getcwd(), target)
    if test_mode:
        engine.apostles = engine.apostles[:3]
        print(f"[TEST MODE] Using only {len(engine.apostles)} apostles: {[a['name'] for a in engine.apostles]}")
    engine.run(num_children=num_children)
