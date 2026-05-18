import streamlit as st
import os
import re
import sys
import io
from evolution import EvolutionEngine

st.set_page_config(page_title="13 Apostles Evolution", layout="wide")

st.title("The 13 Apostles Evolution Engine")

# Sidebar Configuration
st.sidebar.header("Evolution Parameters")
target_file = st.sidebar.text_input("Target File (e.g., 0.py)", value="0.py")
num_runs = st.sidebar.slider("Number of Iterations (Runs)", min_value=1, max_value=10, value=1)
num_children = st.sidebar.slider("Children per Generation", min_value=1, max_value=5, value=1)
test_mode = st.sidebar.checkbox("Test Mode (Fast, 3 Apostles)", value=False)

def parse_lineage():
    """Reads .md files to build a graph of evolution."""
    nodes = set()
    edges = []
    descriptions = {}
    
    for file in os.listdir("."):
        if file.endswith(".md") and not file in ["CORE_OBJECTIVE.md", "CANDIDATE_FORMAT.md", "VOTING_FORMAT.md", "README.md"]:
            basename = file[:-3]
            nodes.add(basename)
            
            with open(file, "r", encoding="utf-8") as f:
                content = f.read()
                
            # Extract children info
            children_match = re.search(r'## Children Spawned\n(.*?)(?:\n##|\Z)', content, re.DOTALL)
            if children_match:
                lines = children_match.group(1).strip().split('\n')
                for line in lines:
                    match = re.search(r'- \*\*(.*?)\.py\*\* <- \[(.*?)\] (.*)', line)
                    if match:
                        child_base = match.group(1)
                        title = match.group(3).strip()
                        nodes.add(child_base)
                        edges.append((basename, child_base))
                        descriptions[child_base] = title
                        
    return nodes, edges, descriptions

st.subheader("Evolutionary Tree")
nodes, edges, descriptions = parse_lineage()

if not nodes:
    st.info("No evolution history found yet.")
else:
    mermaid_code = "graph TD\n"
    for node in nodes:
        label = f"{node}.py"
        if node in descriptions:
            label += f"<br/><i>{descriptions[node]}</i>"
        mermaid_code += f'    {node}["{label}"]\n'
        
    for parent, child in edges:
        mermaid_code += f"    {parent} --> {child}\n"
        
    st.components.v1.html(f'''
        <div class="mermaid">
        {mermaid_code}
        </div>
        <script type="module">
          import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
          mermaid.initialize({{ startOnLoad: true }});
        </script>
    ''', height=600, scrolling=True)

if st.sidebar.button("Run Evolution"):
    current_target = target_file
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    log_area = st.empty()
    
    for run in range(num_runs):
        status_text.text(f"Run {run+1}/{num_runs}: Evolving {current_target}...")
        
        engine = EvolutionEngine(os.getcwd(), current_target)
        if test_mode:
            engine.apostles = engine.apostles[:3]
        
        # Capture stdout to display in UI
        old_stdout = sys.stdout
        new_stdout = io.StringIO()
        sys.stdout = new_stdout
        
        try:
            children_info = engine.run(num_children=num_children)
        except Exception as e:
            sys.stdout = old_stdout
            st.error(f"Error during evolution: {e}")
            break
            
        sys.stdout = old_stdout
        log_area.text_area(f"Log for Run {run+1}", new_stdout.getvalue(), height=300)
        
        if not children_info:
            st.warning("No children spawned. Evolution halted.")
            break
            
        # For multiple consecutive runs, follow the first child node
        current_target = children_info[0]['filename']
        progress_bar.progress((run + 1) / num_runs)
        
    status_text.text("Evolution complete!")
    st.rerun()
