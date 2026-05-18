# 13 Apostles Evolution Framework

An autonomous, self-modifying evolution engine that evolves a target Python program through 13 AI personas (Apostles). 

## Concept
The system is designed to iteratively improve code by generating, evaluating, and selecting optimal code mutations based on strict cost-bounded metrics. It uses a branching file-naming convention and automated Git integration to track the program's generational lineage.

## Features
- **13 AI Personas:** Specialized LLM agents that propose code modifications based on different architectural principles (Performance, Cost, Risk, Interpretability, etc.).
- **Autonomous Evolution:** The system can recursively run on its own output, building an evolutionary tree of code (e.g., `0.py` -> `01.py` -> `01a.py`).
- **Multi-Branching:** Supports spawning multiple candidate children per generation, enabling parallel evolutionary paths.
- **Streamlit Interface:** Interactive web UI to trigger evolution runs, specify iterations, and visualize the evolutionary tree and lineage descriptions.
- **Veto System:** Safety mechanisms allow Apostles to veto overly risky or misaligned code changes.

## Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Set your Google Gemini API key:
   ```bash
   # Windows PowerShell
   $env:GEMINI_API_KEY="your_api_key"
   
   # Linux/macOS
   export GEMINI_API_KEY="your_api_key"
   ```

## Usage

### Streamlit Web UI (Recommended)
Start the interactive dashboard to visualize the tree and run the evolution:
```bash
streamlit run app.py
```

### Command Line
Run the evolution engine directly from the terminal:
```bash
python evolution.py 0.py --children 3
```
*(Use `--test` to limit to 3 apostles for faster testing)*
