"""
app.py — 13 Apostles System: Evolution Dashboard
"""
import streamlit as st
import os, sys, io, time, json, datetime
from evolution import EvolutionEngine
from tree_parser import (
    get_organism_basenames, build_edges,
    parse_decision_log_descriptions, load_code, load_decision_log,
    find_root_seeds,
)

WORKSPACE = os.path.dirname(os.path.abspath(__file__))

st.set_page_config(page_title="13 Apostles System", page_icon="🧬", layout="wide")

# ─── CSS ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=JetBrains+Mono:wght@400&display=swap');
* { font-family: 'Inter', sans-serif; }
code, pre, .stCode { font-family: 'JetBrains Mono', monospace !important; }
[data-testid="stAppViewContainer"] {
    background: linear-gradient(160deg, #07071a 0%, #0d1117 50%, #0a0f2a 100%);
}
[data-testid="stHeader"] { background: transparent; }
[data-testid="stSidebar"] { display: none !important; }
.main-title {
    font-size: 3.2em; font-weight: 800;
    background: linear-gradient(135deg, #6366f1, #a78bfa, #ec4899);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text; margin: 0;
    line-height: 1.2;
}
.author-email {
    font-size: 0.8em; font-weight: 500;
    color: rgba(160,160,220,0.6);
    margin-left: 12px;
}
.section-label {
    font-size: 0.68em; font-weight: 700; letter-spacing: 0.1em;
    text-transform: uppercase; color: rgba(160,160,220,0.4);
    margin: 10px 0 4px 0;
}
.badge {
    display: inline-block; padding: 2px 7px; border-radius: 14px;
    font-size: 0.7em; font-weight: 600; margin-right: 3px;
}
.badge-i { background: rgba(99,102,241,0.18); color: #a5b4fc; }
.badge-g { background: rgba(16,185,129,0.18); color: #6ee7b7; }
.stButton > button {
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    color: white !important; border: none !important;
    border-radius: 7px !important; font-weight: 600 !important;
    font-size: 0.8em !important; padding: 6px 12px !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 5px 16px rgba(99,102,241,0.4) !important;
}
.stSelectbox label, .stSlider label, .stCheckbox label {
    font-size: 0.76em !important;
}
[data-baseweb="select"] { font-size: 0.8em !important; min-height: 30px !important; }
/* Dark mode code blocks */
[data-testid="stCodeBlock"] pre {
    background-color: #0d1117 !important;
    color: #e2e2f0 !important;
    border: 1px solid rgba(99,102,241,0.15) !important;
    border-radius: 8px !important;
}
[data-testid="stCodeBlock"] code { color: #e2e2f0 !important; }

/* Markdown text and headings compact */
.stMarkdown h1 { font-size: 1.3em !important; margin-top: 0.5em !important; padding-bottom: 0.2em !important; border-bottom: 1px solid rgba(99,102,241,0.2) !important; }
.stMarkdown h2 { font-size: 1.1em !important; margin-top: 0.8em !important; margin-bottom: 0.3em !important; color: #c7d2fe !important; }
.stMarkdown h3 { font-size: 0.95em !important; margin-top: 0.6em !important; margin-bottom: 0.2em !important; color: #a5b4fc !important; }
.stMarkdown p, .stMarkdown li { font-size: 0.85em !important; line-height: 1.5 !important; }

hr { border-color: rgba(99,102,241,0.12) !important; margin: 12px 0 !important; }
.footer {
    text-align: center; color: rgba(160,160,220,0.3);
    font-size: 0.7em; margin-top: 24px; padding: 10px 0;
    border-top: 1px solid rgba(99,102,241,0.1);
}
</style>
""", unsafe_allow_html=True)

# ─── Data ───────────────────────────────────────────────────────────────────
basenames = get_organism_basenames(WORKSPACE)
all_edges = build_edges(basenames)
descriptions = parse_decision_log_descriptions(WORKSPACE, basenames)
roots = find_root_seeds(basenames)

next_root_id = "0"
if roots:
    ints = []
    for r in roots:
        try: ints.append(int(r))
        except: pass
    if ints:
        next_root_id = str(max(ints) + 1)

# ─── Header ─────────────────────────────────────────────────────────────────
h1, h2, h3, h4, h5 = st.columns([5, 1, 1, 1, 1])
with h1:
    st.markdown('<div style="display: flex; align-items: baseline;"><span class="main-title">🧬 13 Apostles System</span><span class="author-email">eljja1@gmail.com</span></div>', unsafe_allow_html=True)
with h2:
    font_size = st.slider("Font Size", 4, 20, 7)
    root_font_size = font_size + 2
with h3:
    edge_length = st.slider("Arrow Length", 10, 150, 30)
with h4:
    zoom_level = st.slider("Zoom", 0.3, 3.0, 1.0, step=0.1)
with h5:
    st.markdown("<br>", unsafe_allow_html=True)
    c_btn1, c_btn2 = st.columns(2)
    with c_btn1:
        if st.button("🔄", key="refresh", help="Refresh"):
            st.rerun()
    with c_btn2:
        with st.popover("➕", help="Add New Root"):
            st.markdown(f"**Create `{next_root_id}.py`**")
            new_code = st.text_area("Seed Code (Python)", f"# PrimeOrganism-{next_root_id}\n\n", height=150)
            new_obj = st.text_area("Objective (Markdown, optional)", height=100)
            if st.button("Create Root", type="primary", use_container_width=True):
                with open(os.path.join(WORKSPACE, f"{next_root_id}.py"), "w", encoding="utf-8") as f:
                    f.write(new_code)
                if new_obj.strip():
                    with open(os.path.join(WORKSPACE, f"{next_root_id}.objective.md"), "w", encoding="utf-8") as f:
                        f.write(new_obj)
                st.rerun()

if not basenames:
    st.info("No organisms found. Create a seed file like `0.py`.")
    st.stop()

# ─── Read query params for click selection ──────────────────────────────────
params = st.query_params
inspect_id = params.get("inspect", basenames[-1])
inspect_type = params.get("type", "node")
if inspect_id not in basenames:
    inspect_id = basenames[-1]
    inspect_type = "node"

# ─── Cytoscape.js Interactive Graph ─────────────────────────────────────────
st.markdown(
    f'<p class="section-label">Evolution Tree</p>'
    f'<span class="badge badge-i">🌿 {len(basenames)} nodes</span>'
    f'<span class="badge badge-g">🔗 {len(all_edges)} edges</span>',
    unsafe_allow_html=True,
)

cy_elements = []
for node in basenames:
    label = f"{node}.py"
    if node in descriptions:
        d = descriptions[node]
        label += f"\n{d[:28]}..." if len(d) > 28 else f"\n{d}"
    cls = "root" if node in roots else "child"
    cy_elements.append({"data": {"id": node, "label": label}, "classes": cls})
for parent, child in all_edges:
    cy_elements.append({"data": {"source": parent, "target": child, "id": f"e_{parent}_{child}"}})

elements_json = json.dumps(cy_elements)
graph_h = 1000

cy_html = f"""
<div id="cy" style="width:100%;height:{graph_h}px;background:rgba(8,8,24,0.6);
     border:1px solid rgba(99,102,241,0.12);border-radius:10px;cursor:grab;"></div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/cytoscape/3.28.1/cytoscape.min.js"></script>
<script>
var cy = cytoscape({{
  container: document.getElementById('cy'),
  elements: {elements_json},
  style: [
    {{ selector: 'node', style: {{
        'label': 'data(label)', 'background-opacity': 0,
        'color': '#c7d2fe', 'text-valign': 'center', 'text-halign': 'center',
        'font-size': '{font_size}px', 'font-family': 'Inter,sans-serif',
        'text-wrap': 'wrap', 'text-max-width': '120px',
        'transition-property': 'color font-weight', 'transition-duration': '0.15s',
    }} }},
    {{ selector: 'node.root', style: {{
        'font-weight': 'bold', 'font-size': '{root_font_size}px', 'color': '#fff',
    }} }},
    {{ selector: 'node:active, node.tapped', style: {{
        'color': '#ec4899', 'font-weight': 'bold',
    }} }},
    {{ selector: 'edge', style: {{
        'width': 2, 'line-color': '#4f46e5',
        'target-arrow-color': '#818cf8', 'target-arrow-shape': 'triangle',
        'curve-style': 'bezier', 'opacity': 0.6,
        'transition-property': 'line-color opacity width', 'transition-duration': '0.15s',
    }} }},
    {{ selector: 'edge:active, edge.tapped', style: {{
        'line-color': '#ec4899', 'target-arrow-color': '#f472b6',
        'width': 3, 'opacity': 1,
    }} }},
  ],
  layout: {{
    name: 'cose',
    animate: false, fit: false, padding: 40,
    nodeRepulsion: function(){{ return 12000; }},
    idealEdgeLength: function(){{ return {edge_length}; }},
    edgeElasticity: function(){{ return 80; }},
    gravity: 0.6, numIter: 800,
    componentSpacing: 140,
  }},
  zoom: {zoom_level},
  userZoomingEnabled: true, userPanningEnabled: true,
  boxSelectionEnabled: false, autoungrabify: false,
  minZoom: 0.1, maxZoom: 5.0,
}});
cy.ready(function() {{
    cy.center();
}});
cy.on('tap', 'node', function(e) {{
  var id = e.target.id();
  cy.elements().removeClass('tapped');
  e.target.addClass('tapped');
  try {{
    var url = new URL(window.parent.location);
    url.searchParams.set('inspect', id);
    url.searchParams.set('type', 'node');
    window.parent.location.href = url.toString();
  }} catch(err) {{ }}
}});
cy.on('tap', 'edge', function(e) {{
  var src = e.target.source().id();
  cy.elements().removeClass('tapped');
  e.target.addClass('tapped');
  try {{
    var url = new URL(window.parent.location);
    url.searchParams.set('inspect', src);
    url.searchParams.set('type', 'edge');
    window.parent.location.href = url.toString();
  }} catch(err) {{ }}
}});
</script>
"""
st.components.v1.html(cy_html, height=graph_h + 10, scrolling=False)

# ─── Controls ───────────────────────────────────────────────────────────────
st.markdown("---")
c1, c2, c3, c4, c5, c6 = st.columns([3, 2, 2, 2, 2, 3])
with c1:
    target_node = st.selectbox("Evolve from", basenames, format_func=lambda x: f"{x}.py", index=len(basenames)-1)
with c2:
    num_children = st.slider("Children", 1, 13, 1)
with c3:
    select_children = st.slider("Select Children", 1, 13, 1)
with c4:
    generations = st.slider("Generations", 1, 100, 1)
with c5:
    test_mode = st.checkbox("⚡ Test (3)", value=False)
with c6:
    st.markdown("")
    run_btn = st.button(f"▶ Evolve {target_node}.py")

if run_btn:
    # Ensure 'Select Children' does not exceed the actual 'Children' count
    actual_select = min(select_children, num_children)
    
    queue = [f"{target_node}.py"]
    st.session_state.latest_log = []
    st.session_state.latest_status = []
    status_ph = st.empty()
    st.markdown('<p class="section-label">🏃 Live Execution Log</p>', unsafe_allow_html=True)
    live_log_ph = st.empty()
    
    class LiveLogBox(io.StringIO):
        def __init__(self, ph):
            super().__init__()
            self.ph = ph
            self.lines = []
        def write(self, s):
            super().write(s)
            if s.strip():
                now_str = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
                for line in s.strip().split('\n'):
                    if line.strip():
                        self.lines.append(f"{now_str} {line.strip()}")
                self.ph.code("\n".join(self.lines[-3:]), language="text")

    buf = None
    for i in range(generations):
        next_queue = []
        for current in queue:
            current_base = current[:-3] if current.endswith(".py") else current
            # Check existing direct children in the tree
            existing_children = [c for p, c in all_edges if p == current_base]
            
            if len(existing_children) >= actual_select:
                selected_existing = [f"{c}.py" for c in sorted(existing_children)[:actual_select]]
                msg = f"♻️ Reused existing {len(selected_existing)} children for {current}: {', '.join(selected_existing)}"
                status_ph.info(msg)
                st.session_state.latest_status.append(("success", msg))
                next_queue.extend(selected_existing)
                continue

            with st.spinner(f"Generation {i+1}/{generations}: Evolving {current}"):
                engine = EvolutionEngine(WORKSPACE, current)
                if test_mode:
                    engine.apostles = engine.apostles[:3]
                old_stdout = sys.stdout
                sys.stdout = buf = LiveLogBox(live_log_ph)
                children_info, error = [], None
                try:
                    children_info = engine.run(num_children=num_children)
                except Exception as e:
                    error = str(e)
                finally:
                    sys.stdout = old_stdout
                
                if error:
                    msg = f"Error on {current}: {error}"
                    status_ph.error(msg)
                    st.session_state.latest_status.append(("error", msg))
                elif children_info:
                    selected = children_info[:actual_select]
                    msg = f"✅ {current} -> {', '.join(c['filename'] for c in selected)}"
                    status_ph.success(msg)
                    st.session_state.latest_status.append(("success", msg))
                    next_queue.extend([c['filename'] for c in selected])
                else:
                    msg = f"⚠️ {current}: All dropped."
                    status_ph.warning(msg)
                    st.session_state.latest_status.append(("warning", msg))
        
        queue = next_queue
        if not queue:
            break
            
    if buf is not None:
        st.session_state.latest_log = buf.lines
    time.sleep(0.5); st.rerun()

# ─── Persisted Log Display ──────────────────────────────────────────────────
if "latest_status" in st.session_state and st.session_state.latest_status:
    st.markdown('<p class="section-label">🏁 Last Execution Result</p>', unsafe_allow_html=True)
    for stype, msg in st.session_state.latest_status:
        if stype == "error": st.error(msg)
        elif stype == "success": st.success(msg)
        else: st.warning(msg)
    
    if "latest_log" in st.session_state and st.session_state.latest_log:
        with st.expander("Show Full Log", expanded=True):
            st.code("\n".join(st.session_state.latest_log), language="text")

# ─── Inspector (auto-selected from graph click) ────────────────────────────
st.markdown("---")
st.markdown('<p class="section-label">🔍 Inspector</p>', unsafe_allow_html=True)

idx = basenames.index(inspect_id) if inspect_id in basenames else len(basenames)-1

inspect = st.selectbox(
    "Node", basenames,
    format_func=lambda x: f"{x}.py" + (f"  — {descriptions[x]}" if x in descriptions else ""),
    index=idx,
)

if inspect != inspect_id:
    st.query_params["inspect"] = inspect
    st.query_params["type"] = "node"
    st.rerun()

if inspect:
    if inspect_type == "edge":
        log = load_decision_log(WORKSPACE, inspect)
        if log:
            st.markdown(log)
        else:
            st.info("No decision log.")
    else:
        t_code, t_log = st.tabs(["💻 Code", "📋 Decision Log"])
        with t_code:
            code = load_code(WORKSPACE, inspect)
            if code:
                st.code(code, language="python", line_numbers=True)
            else:
                st.info("No source file.")
        with t_log:
            log = load_decision_log(WORKSPACE, inspect)
            if log:
                st.markdown(log)
            else:
                st.info("No decision log.")

# ─── Evolutionary Diversity Analyzer ─────────────────────────────────────────
st.markdown("---")
st.markdown('<p class="section-label">🧬 Evolutionary Diversity Analyzer</p>', unsafe_allow_html=True)
st.caption("Compare 2 to 5 organisms to measure code implementation and execution output similarity. Diagnoses convergence vs divergence in your evolutionary lineage.")

selected_compare = st.multiselect(
    "Select Organisms for Similarity Analysis",
    basenames,
    format_func=lambda x: f"{x}.py" + (f"  — {descriptions[x]}" if x in descriptions else ""),
    max_selections=5,
    key="compare_select"
)

if len(selected_compare) >= 2:
    if st.button("✨ Analyze Evolutionary Diversity", use_container_width=True):
        import difflib
        import subprocess
        
        # 1. Fetch code and execution output
        code_data = {}
        output_data = {}
        
        progress_ph = st.progress(0)
        status_text_ph = st.empty()
        
        total_steps = len(selected_compare)
        for idx, base in enumerate(selected_compare):
            status_text_ph.text(f"Running and analyzing {base}.py...")
            
            # Load Code
            code = load_code(WORKSPACE, base) or ""
            code_data[base] = code
            
            # Run program securely
            filepath = os.path.join(WORKSPACE, f"{base}.py")
            output = ""
            if os.path.exists(filepath):
                try:
                    res = subprocess.run(
                        [sys.executable, filepath],
                        capture_output=True,
                        text=True,
                        timeout=5,
                        cwd=WORKSPACE
                    )
                    if res.returncode == 0:
                        output = res.stdout.strip() if res.stdout.strip() else "(Successful execution with no output)"
                    else:
                        output = f"Error (code {res.returncode}):\n{res.stderr.strip()}"
                except subprocess.TimeoutExpired:
                    output = "Error: Timeout (5s limit)"
                except Exception as e:
                    output = f"Error running code: {str(e)}"
            else:
                output = "Error: File not found."
            
            output_data[base] = output
            progress_ph.progress(int((idx + 1) / total_steps * 100))
        
        status_text_ph.empty()
        progress_ph.empty()
        
        # 2. Pairwise similarity calculation
        code_sims = []
        out_sims = []
        
        # Build matrix tables
        matrix_code = {b1: {b2: "-" for b2 in selected_compare} for b1 in selected_compare}
        matrix_output = {b1: {b2: "-" for b2 in selected_compare} for b1 in selected_compare}
        
        for i, b1 in enumerate(selected_compare):
            matrix_code[b1][b1] = "100.0%"
            matrix_output[b1][b1] = "100.0%"
            for j in range(i + 1, len(selected_compare)):
                b2 = selected_compare[j]
                
                # Code similarity
                c_sim = difflib.SequenceMatcher(None, code_data[b1], code_data[b2]).ratio()
                code_sims.append(c_sim)
                matrix_code[b1][b2] = f"{c_sim * 100:.1f}%"
                matrix_code[b2][b1] = f"{c_sim * 100:.1f}%"
                
                # Output similarity
                o_sim = difflib.SequenceMatcher(None, output_data[b1], output_data[b2]).ratio()
                out_sims.append(o_sim)
                matrix_output[b1][b2] = f"{o_sim * 100:.1f}%"
                matrix_output[b2][b1] = f"{o_sim * 100:.1f}%"
        
        avg_code = sum(code_sims) / len(code_sims) if code_sims else 1.0
        avg_output = sum(out_sims) / len(out_sims) if out_sims else 1.0
        
        # Render Metrics
        m1, m2 = st.columns(2)
        with m1:
            st.metric("Average Code Similarity", f"{avg_code * 100:.1f}%")
        with m2:
            st.metric("Average Output Similarity", f"{avg_output * 100:.1f}%")
            
        # Render dynamic diagnoses
        st.markdown("### 📊 Diversity Verdict")
        if avg_code >= 0.8 and avg_output >= 0.8:
            st.success("🎯 **Evolutionary Convergence (수렴)**: The selected programs are highly similar in both structural implementation and execution behavior. The lineages are converging onto a unified standard design.")
        elif avg_output >= 0.8 and avg_code < 0.6:
            st.info("💡 **Functional Convergence with Diverse Code (기능 수렴 / 구조 분화)**: The programs solve the task differently in code structure, but yield highly identical execution outputs. This means the evolutionary pipeline is successfully exploring diverse mechanisms to achieve the same goal.")
        elif avg_code < 0.5 and avg_output < 0.5:
            st.warning("🌿 **Evolutionary Divergence (발산)**: The programs are highly diverse in both implementation and runtime output. The evolutionary engine is actively branching out to explore vastly different computational strategies.")
        else:
            st.info("⚖️ **Balanced Evolutionary Exploration (균형 잡힌 탐색)**: Moderate level of variance. The organisms show healthy behavioral and structural adjustments as they evolve.")
            
        # Detail Matrix Tables in Expanders
        tab_code, tab_out = st.tabs(["💻 Detailed Code Similarity Matrix", "🖥️ Detailed Output Similarity Matrix"])
        with tab_code:
            st.dataframe(matrix_code, use_container_width=True)
        with tab_out:
            st.dataframe(matrix_output, use_container_width=True)
            
        # Show Output Content comparison
        with st.expander("🔍 Compare Captured Execution Outputs", expanded=False):
            for base in selected_compare:
                st.subheader(f"{base}.py Output:")
                st.code(output_data[base], language="text")
else:
    st.info("Please select at least 2 organisms to begin similarity and diversity analysis.")

# ─── Footer ─────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="footer">Powered by eljja1@gmail.com · 13 Apostles System</div>',
    unsafe_allow_html=True,
)
