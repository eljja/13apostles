import json
import os
import sys

MAGI_ROLES = [
    "Performance", "Cost", "Risk", "Novelty", "Feasibility",
    "Scalability", "Robustness", "Safety", "Interpretability",
    "Alignment", "Data", "Architecture", "Meta"
]

class MagiEngine:
    def __init__(self, workspace_dir):
        self.workspace_dir = workspace_dir
        self.docs_dir = os.path.join(workspace_dir, "docs", "evolution")
        os.makedirs(self.docs_dir, exist_ok=True)

    def print_header(self, text):
        print(f"\n{'='*50}\n{text}\n{'='*50}")

    def run_simulation(self, issue_title, candidates, votes_data):
        self.print_header(f"MAGI-13 Evolution Loop Started\nIssue: {issue_title}")

        if len(candidates) > 20:
            print("Error: Maximum 20 candidates allowed.")
            return

        print(f"Loaded {len(candidates)} candidates.")

        # Tally votes
        scores = {c['id']: 0 for c in candidates}
        vetoes = []

        self.print_header("13 MAGI Voting Process")
        for magi, magi_votes in votes_data.items():
            print(f"[{magi} MAGI] casting votes...")
            for vote in magi_votes:
                c_id = vote['candidate_id']
                score = vote['score']
                is_veto = vote.get('veto', False)

                if is_veto:
                    print(f"  -> VETO invoked by {magi} on candidate {c_id}: {vote.get('reason', '')}")
                    vetoes.append(c_id)
                else:
                    scores[c_id] += score

        self.print_header("Voting Results")
        valid_candidates = [c for c in candidates if c['id'] not in vetoes]
        if not valid_candidates:
            print("All candidates were vetoed! Needs new proposals.")
            return

        sorted_candidates = sorted(valid_candidates, key=lambda x: scores[x['id']], reverse=True)
        for c in sorted_candidates:
            print(f"Candidate {c['id']}: {scores[c['id']]} points - {c['title']}")

        winner = sorted_candidates[0]
        self.print_header(f"Selected Candidate: {winner['id']} - {winner['title']}")

        self.save_decision(issue_title, candidates, votes_data, winner, scores, vetoes)
        print(f"\nDecision documented in {self.docs_dir}")
        return winner

    def save_decision(self, issue_title, candidates, votes_data, winner, scores, vetoes):
        files = os.listdir(self.docs_dir)
        gen_num = len([f for f in files if f.startswith("gen_")])
        file_path = os.path.join(self.docs_dir, f"gen_{gen_num}_decision.md")

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"# Generation {gen_num} Decision\n\n")
            f.write(f"**Issue:** {issue_title}\n\n")

            f.write("## Candidates\n")
            for c in candidates:
                f.write(f"### Candidate {c['id']}: {c['title']}\n")
                f.write(f"- **Description:** {c['description']}\n")
                f.write(f"- **Cost:** {c.get('cost', 'Unknown')}\n")
                f.write(f"- **Risk:** {c.get('risk', 'Unknown')}\n\n")

            f.write("## Voting Results\n")
            for c_id, score in scores.items():
                status = "(VETOED)" if c_id in vetoes else ""
                f.write(f"- Candidate {c_id}: {score} points {status}\n")

            f.write("\n## Final Selection\n")
            f.write(f"**Winner:** Candidate {winner['id']} ({winner['title']})\n")
            f.write(f"**Score:** {scores[winner['id']]}\n\n")
            f.write("## Next Steps\n")
            f.write(f"Creating git branch corresponding to this candidate (e.g. `{winner['id']}`).\n")


if __name__ == "__main__":
    print("MAGI-13 Engine initialized. Awaiting input data for simulation.")
