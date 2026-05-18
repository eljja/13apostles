from magi_engine import MagiEngine
import os

def main():
    engine = MagiEngine(os.getcwd())
    
    issue_title = "What should this program do? (Initial Purpose Definition)"
    
    candidates = [
        {
            "id": "0",
            "title": "AI Task Automation Engine (Automated Local Agent)",
            "description": "A background agent that can monitor folders, run python scripts automatically, and automate tedious daily tasks based on natural language instructions.",
            "cost": "Medium (Requires local LLM or API integration, safe file-system access)",
            "risk": "Medium (Could accidentally modify wrong files if not sandboxed)"
        },
        {
            "id": "1",
            "title": "Personal Knowledge Graph Assistant",
            "description": "An AI tool that ingests daily logs, automatically tags them, and builds a searchable semantic graph of personal knowledge.",
            "cost": "High (Requires embedding models, vector DB, continuous indexing)",
            "risk": "Low (Mostly read-only operations on text data)"
        },
        {
            "id": "2",
            "title": "MAGI-13 Self-Evolving Codebase Framework",
            "description": "A meta-program where the core functionality is to continuously rewrite and optimize its own codebase based on external metrics or goals provided by the user.",
            "cost": "Low (Text manipulation)",
            "risk": "High (Self-destruction or infinite loops, requires strict veto checks)"
        }
    ]
    
    # Simulate 13 MAGI distributing 10 points each
    votes_data = {
        "Performance": [{"candidate_id": "0", "score": 8}, {"candidate_id": "1", "score": 2}],
        "Cost": [{"candidate_id": "0", "score": 3}, {"candidate_id": "1", "score": 2}, {"candidate_id": "2", "score": 5}],
        "Risk": [{"candidate_id": "0", "score": 4}, {"candidate_id": "1", "score": 6}, {"candidate_id": "2", "score": 0, "veto": True, "reason": "Self-modifying code without sandbox is too dangerous initially."}],
        "Novelty": [{"candidate_id": "2", "score": 8}, {"candidate_id": "0", "score": 2}],
        "Feasibility": [{"candidate_id": "0", "score": 7}, {"candidate_id": "1", "score": 3}],
        "Scalability": [{"candidate_id": "1", "score": 5}, {"candidate_id": "0", "score": 5}],
        "Robustness": [{"candidate_id": "1", "score": 8}, {"candidate_id": "0", "score": 2}],
        "Safety": [{"candidate_id": "1", "score": 10}, {"candidate_id": "2", "score": 0, "veto": True, "reason": "Unpredictable execution."}],
        "Interpretability": [{"candidate_id": "0", "score": 5}, {"candidate_id": "1", "score": 5}],
        "Alignment": [{"candidate_id": "0", "score": 6}, {"candidate_id": "1", "score": 4}],
        "Data": [{"candidate_id": "0", "score": 9}, {"candidate_id": "1", "score": 1}],
        "Architecture": [{"candidate_id": "0", "score": 7}, {"candidate_id": "1", "score": 3}],
        "Meta": [{"candidate_id": "0", "score": 5}, {"candidate_id": "1", "score": 5}]
    }

    winner = engine.run_simulation(issue_title, candidates, votes_data)

if __name__ == "__main__":
    main()
