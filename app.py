"""
app.py — 13 Apostles System: Evolution Dashboard
"""
import sys
# ─── Stlite (WebAssembly) On-Demand HTTP File Fetching Patch ─────────────────
if "pyodide" in sys.modules:
    import builtins
    import urllib.request
    import os
    original_open = builtins.open
    
    def smart_open(file, *args, **kwargs):
        try:
            return original_open(file, *args, **kwargs)
        except FileNotFoundError as e:
            filename = str(file)
            # If a relative file is missing, fetch it dynamically from the server via HTTP
            if filename.endswith((".py", ".md", ".json")):
                import time
                url = f"./{filename}?v={int(time.time())}"
                try:
                    with urllib.request.urlopen(url) as response:
                        content = response.read()
                    dirname = os.path.dirname(filename)
                    if dirname:
                        os.makedirs(dirname, exist_ok=True)
                    with original_open(filename, "wb") as f:
                        f.write(content)
                    return original_open(file, *args, **kwargs)
                except Exception as ex:
                    print(f"[stlite-patch] Failed to fetch {filename} over HTTP: {ex}")
            raise e
            
    builtins.open = smart_open

import streamlit as st
import streamlit.components.v1 as components

# ─── Streamlit Version Compatibility Patch ───────────────────────────────────
# Futuristic local Streamlit uses st.iframe and deprecates components.html.
# Older Streamlit (and browser Wasm Stlite) does not have st.iframe and uses components.html.
if not hasattr(st, "iframe"):
    st.iframe = components.html

import os, sys, io, time, json, re, datetime, difflib, subprocess, signal
from evolution import EvolutionEngine
from tree_parser import (
    get_organism_basenames, build_edges,
    parse_decision_log_descriptions, load_code, load_decision_log,
    find_root_seeds,
)

WORKSPACE = os.path.dirname(os.path.abspath(__file__))

def auto_git_push():
    """
    Streamlit Cloud or local env helper to automatically stage, commit, 
    and push newly evolved organisms (*.py and *.md files) back to GitHub main branch.
    """
    import subprocess
    
    # 1. Retrieve GITHUB_TOKEN from Streamlit Secrets or Environment Variables
    token = None
    try:
        if hasattr(st, "secrets") and "GITHUB_TOKEN" in st.secrets:
            token = st.secrets["GITHUB_TOKEN"]
    except Exception:
        pass
        
    if not token:
        token = os.environ.get("GITHUB_TOKEN")
        
    # 2. Configure Git bot identity
    try:
        subprocess.run(["git", "config", "--global", "user.name", "13 Apostles Bot"], capture_output=True)
        subprocess.run(["git", "config", "--global", "user.email", "bot@13apostles.internal"], capture_output=True)
        
        # Stage newly created files
        subprocess.run(["git", "add", "."], capture_output=True, cwd=WORKSPACE)
        
        # Check if there are actual diffs to commit
        status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, cwd=WORKSPACE)
        if not status.stdout.strip():
            print("[Auto-Git] No changes to push.")
            return True
            
        # Commit the modifications
        commit_msg = f"chore: Auto-commit newly evolved organisms [web run {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]"
        subprocess.run(["git", "commit", "-m", commit_msg], capture_output=True, cwd=WORKSPACE)
        
        # 3. Push to GitHub
        if token:
            # Inject token securely to bypass password prompts in headless cloud
            remote_url = f"https://{token}@github.com/eljja/13apostles.git"
            res = subprocess.run(["git", "push", "-f", remote_url, "HEAD:main"], capture_output=True, text=True, cwd=WORKSPACE)
            if res.returncode == 0:
                print("[Auto-Git] Successfully pushed newly evolved organisms to GitHub main branch!")
                return True
            else:
                print(f"[Auto-Git] Push failed: {res.stderr}")
                return False
        else:
            # Fallback to local default push in development env
            res = subprocess.run(["git", "push", "-f", "13apostles", "HEAD:main"], capture_output=True, text=True, cwd=WORKSPACE)
            return res.returncode == 0
            
    except Exception as e:
        print(f"[Auto-Git] Exception during auto-commit: {str(e)}")
        return False

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

/* ─── Enforce Dark Theme via CSS Variables on Base Streamlit Components (No toml required) ─── */
:root, [data-testid="stAppViewContainer"], html, body, .stApp {
    --theme-background-color: #0d1117 !important;
    --theme-secondary-background-color: #1e1e3a !important;
    --theme-text-color: #e2e2f0 !important;
    --theme-primary-color: #6366f1 !important;
    
    background-color: #0d1117 !important;
    color: #e2e2f0 !important;
}
div[data-baseweb="select"] > div {
    background-color: #0d1117 !important;
    color: #e2e2f0 !important;
    border-color: rgba(99, 102, 241, 0.25) !important;
}
div[data-baseweb="popover"], div[data-baseweb="menu"] {
    background-color: #0d1117 !important;
    color: #e2e2f0 !important;
    border: 1px solid rgba(99, 102, 241, 0.25) !important;
}
ul[role="listbox"] {
    background-color: #0d1117 !important;
    color: #e2e2f0 !important;
    border: 1px solid rgba(99, 102, 241, 0.25) !important;
}
li[role="option"] {
    background-color: #0d1117 !important;
    color: #e2e2f0 !important;
}
li[role="option"]:hover {
    background-color: rgba(99, 102, 241, 0.15) !important;
    color: #ffffff !important;
}
div[data-testid="stThumb"] {
    background-color: #6366f1 !important;
    border: 2px solid #ffffff !important;
}
div[data-testid="stTickBar"] {
    color: rgba(160, 160, 220, 0.4) !important;
}
input[type="text"], input[type="number"], textarea, [data-baseweb="input"] input {
    background-color: #0d1117 !important;
    color: #e2e2f0 !important;
    border: 1px solid rgba(99, 102, 241, 0.2) !important;
}
</style>
""", unsafe_allow_html=True)

# ─── Parent Window Event Listener Injection ──────────────────────────────────
# We inject a script into the parent window using a 0-height iframe to bypass
# Streamlit's st.markdown HTML sanitization of inline event handlers.
st.iframe("""
<script>
  const parentWin = window.parent;
  if (!parentWin.hasStreamlitParamListener) {
    parentWin.hasStreamlitParamListener = true;
    parentWin.addEventListener('message', function(event) {
      if (event.data && event.data.type === 'streamlit:update_params') {
        const params = event.data.params;
        try {
          const url = new URL(parentWin.location.href);
          let changed = false;
          for (const key in params) {
            if (params.hasOwnProperty(key)) {
              const oldVal = url.searchParams.get(key);
              const newVal = String(params[key]);
              
              if (key === 'zoom' && oldVal !== null) {
                if (Math.abs(parseFloat(oldVal) - parseFloat(newVal)) > 0.05) {
                  url.searchParams.set(key, newVal);
                  changed = true;
                }
              } else if (oldVal !== newVal) {
                url.searchParams.set(key, newVal);
                changed = true;
              }
            }
          }
          if (changed) {
            parentWin.location.href = url.toString();
          }
        } catch (e) {
          console.error("Failed to update parent URL:", e);
        }
      }
    });
  }
</script>
""", height=1)


# ─── Custom Decision Log Renderer ───────────────────────────────────────────
# ─── Custom Decision Log Renderers ──────────────────────────────────────────
def render_decision_log_text(log_content: str):

    # Split at '## Voting Results' section — everything from there belongs in the votes tab
    vote_section_match = re.search(r'^## Voting Results', log_content, re.MULTILINE)
    if vote_section_match:
        markdown_before = log_content[:vote_section_match.start()].strip()
    else:
        # Fallback: try splitting at Raw Votes Data JSON block
        pattern = r'## Raw Votes Data\s*```json\s*(.*?)\s*```'
        match = re.search(pattern, log_content, re.DOTALL)
        if match:
            markdown_before = log_content[:match.start()].strip()
        else:
            markdown_before = log_content

    st.markdown(markdown_before)


def render_decision_log_votes_table(log_content: str, inspect_id: str):

    # Render the text-based Voting Results + Children Spawned sections first
    vote_section_match = re.search(r'^## Voting Results', log_content, re.MULTILINE)
    raw_json_pattern = r'## Raw Votes Data\s*```json\s*(.*?)\s*```'
    raw_json_match = re.search(raw_json_pattern, log_content, re.DOTALL)

    if vote_section_match:
        # Extract text between '## Voting Results' and '## Raw Votes Data'
        end_pos = raw_json_match.start() if raw_json_match else len(log_content)
        vote_text = log_content[vote_section_match.start():end_pos].strip()
        if vote_text:
            st.markdown(vote_text)
            st.markdown("---")

    if not raw_json_match:
        if not vote_section_match:
            st.info("No voting data available for this seed node.")
        return

    match = raw_json_match

    # Extract JSON content
    raw_json_str = match.group(1).strip()

    # Parse the votes data
    try:
        votes_data = json.loads(raw_json_str)
    except Exception as e:
        st.markdown("### Raw Votes Data")
        st.code(raw_json_str, language="json")
        return

    # 2. Extract Candidate titles
    candidate_titles = {}
    for m in re.finditer(r'^###\s*\[\s*([^\]\s]+)\s*\]\s*(.*?)$', log_content, re.MULTILINE):
        c_id = m.group(1).strip()
        title = m.group(2).strip()
        candidate_titles[c_id] = title

    # 3. Extract Children Spawned
    spawned_candidates = {}
    for m in re.finditer(r'-\s*\*\*(.*?)\.py\*\*\s*<-\s*\[(.*?)\]', log_content):
        child_base = m.group(1).strip()
        c_id = m.group(2).strip()
        spawned_candidates[c_id] = child_base

    # 4. Extract Veto details
    veto_details = {}
    for m in re.finditer(r'-\s*Candidate\s*\[?([^\s\]]+)\]?\s*vetoed\s*by\s*([^:]+):\s*(.*?)$', log_content, re.MULTILINE):
        c_id = m.group(1).strip()
        apostle = m.group(2).strip()
        reason = m.group(3).strip()
        if c_id not in veto_details:
            veto_details[c_id] = []
        veto_details[c_id].append({"apostle": apostle, "reason": reason})

    # 5. Identify candidates and calculate scores
    all_candidate_ids = set()
    for apostle_name, votes in votes_data.items():
        for v in votes:
            if 'candidate_id' in v:
                all_candidate_ids.add(str(v['candidate_id']))

    def sort_key(c_id):
        try:
            return (0, int(c_id))
        except ValueError:
            return (1, c_id)

    all_candidate_ids = sorted(list(all_candidate_ids), key=sort_key)

    scores = {c_id: {"impact": 0, "feasibility": 0, "alignment": 0, "safety": 0, "cost": 0, "veto": False} for c_id in all_candidate_ids}

    for apostle_name, votes in votes_data.items():
        for v in votes:
            c_id = str(v.get('candidate_id'))
            if c_id not in scores:
                continue
            if v.get('veto', False):
                scores[c_id]['veto'] = True

            scores[c_id]['impact'] += v.get('impact_score', 0)
            scores[c_id]['feasibility'] += v.get('feasibility_score', 0)
            scores[c_id]['alignment'] += v.get('alignment_score', 0)
            scores[c_id]['safety'] += v.get('safety_multiplier', 1.0)
            scores[c_id]['cost'] += v.get('cost_multiplier', 1.0)

    final_results = []
    for c_id in all_candidate_ids:
        s = scores[c_id]
        if s['veto']:
            final_score = 0.0
        else:
            cost = max(s['cost'], 1.0)
            final_score = (s['impact'] * s['feasibility'] * s['alignment'] * s['safety']) / cost

        final_results.append({
            "id": c_id,
            "title": candidate_titles.get(c_id, f"Candidate {c_id}"),
            "scores": s,
            "final_score": final_score,
            "vetoed": s['veto']
        })

    final_results.sort(key=lambda x: (not x['vetoed'], x['final_score']), reverse=True)

    # 6. Render styles and Aggregated Table
    styles = """
    <style>
    .decision-table-container {
        margin: 20px 0;
        width: 100%;
    }
    .decision-table {
        width: 100%;
        border-collapse: collapse;
        background: rgba(13, 17, 23, 0.7);
        border: 1px solid rgba(99, 102, 241, 0.15);
        border-radius: 8px;
        overflow: visible;
        margin-bottom: 25px;
        font-size: 0.85em;
    }
    .decision-table th {
        background: rgba(99, 102, 241, 0.12);
        color: #c7d2fe;
        font-weight: 600;
        padding: 10px 12px;
        text-align: left;
        border-bottom: 1px solid rgba(99, 102, 241, 0.2);
    }
    .decision-table td {
        padding: 10px 12px;
        border-bottom: 1px solid rgba(99, 102, 241, 0.08);
        color: #e2e2f0;
        vertical-align: middle;
    }
    .decision-table tr:hover {
        background: rgba(99, 102, 241, 0.04);
    }
    .decision-table tr.adopted-row {
        background: rgba(16, 185, 129, 0.06) !important;
        border-left: 4px solid #10b981 !important;
    }
    .decision-table tr.vetoed-row {
        background: rgba(239, 68, 68, 0.03) !important;
    }
    .decision-table tr.vetoed-row td {
        color: rgba(226, 226, 240, 0.55);
    }
    .val-pill {
        display: inline-block;
        padding: 2px 7px;
        border-radius: 5px;
        font-weight: 600;
        font-size: 0.9em;
    }
    .val-emerald {
        color: #34d399;
        background: rgba(16, 185, 129, 0.12);
    }
    .val-amber {
        color: #fbbf24;
        background: rgba(251, 191, 36, 0.12);
    }
    .val-rose {
        color: #f87171;
        background: rgba(239, 68, 68, 0.12);
    }
    .val-neutral {
        color: #9ca3af;
        background: rgba(156, 163, 175, 0.08);
    }
    .status-badge {
        display: inline-block;
        padding: 3px 9px;
        border-radius: 12px;
        font-weight: 700;
        font-size: 0.75em;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .status-adopted {
        background: rgba(16, 185, 129, 0.2);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.4);
        box-shadow: 0 0 10px rgba(16, 185, 129, 0.15);
    }
    .status-vetoed {
        background: rgba(239, 68, 68, 0.2);
        color: #f87171;
        border: 1px solid rgba(239, 68, 68, 0.4);
    }
    .status-evaluated {
        background: rgba(156, 163, 175, 0.15);
        color: #d1d5db;
        border: 1px solid rgba(156, 163, 175, 0.25);
    }
    .veto-reason-tooltip {
        text-decoration: underline dotted;
        cursor: help;
        color: #f87171;
    }
    .reason-cell {
        cursor: help;
        color: #a5b4fc;
        font-size: 1.1em;
        text-align: center;
    }
    /* Premium CSS Tooltip */
    .custom-tooltip {
        position: relative;
        display: inline-block;
        cursor: help;
    }
    .custom-tooltip .tooltip-text {
        visibility: hidden;
        width: 280px;
        background-color: #1e1e30;
        color: #e2e2f0;
        text-align: left;
        border: 1px solid rgba(99, 102, 241, 0.4);
        border-radius: 6px;
        padding: 8px 12px;
        position: absolute;
        z-index: 1000;
        bottom: 125%;
        left: 50%;
        transform: translateX(-50%);
        opacity: 0;
        transition: opacity 0.15s ease-in-out;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.6);
        font-size: 1.05em;
        font-weight: normal;
        white-space: normal;
        pointer-events: none;
        line-height: 1.4;
    }
    .custom-tooltip .tooltip-text::after {
        content: "";
        position: absolute;
        top: 100%;
        left: 50%;
        margin-left: -5px;
        border-width: 5px;
        border-style: solid;
        border-color: #1e1e30 transparent transparent transparent;
    }
    .custom-tooltip:hover .tooltip-text {
        visibility: visible;
        opacity: 1;
    }
    </style>
    """
    clean_styles = "\n".join(line.strip() for line in styles.split("\n") if line.strip())
    st.markdown(clean_styles, unsafe_allow_html=True)

    st.markdown('### 📊 Candidates Leaderboard')

    table_rows = []
    for r in final_results:
        c_id = r['id']
        title = r['title']
        s = r['scores']
        f_score = r['final_score']
        vetoed = r['vetoed']

        is_adopted = c_id in spawned_candidates
        if is_adopted:
            child_base = spawned_candidates[c_id]
            status_html = f'<span class="status-badge status-adopted" title="Spawned organism: {child_base}.py">Adopted</span>'
            row_class = 'class="adopted-row"'
        elif vetoed:
            v_reasons_str = " | ".join([f"{v['apostle']}: {v['reason']}" for v in veto_details.get(c_id, [])])
            if not v_reasons_str:
                v_reasons_str = "Vetoed by Apostle"
            v_reasons_str_escaped = v_reasons_str.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#x27;')
            status_html = f'<span class="status-badge status-vetoed custom-tooltip">Vetoed<span class="tooltip-text">{v_reasons_str_escaped}</span></span>'
            row_class = 'class="vetoed-row"'
        else:
            status_html = '<span class="status-badge status-evaluated">Evaluated</span>'
            row_class = ''

        imp_class = 'val-emerald' if s['impact'] >= 45 else ('val-amber' if s['impact'] >= 30 else 'val-rose')
        imp_html = f'<span class="val-pill {imp_class}">{s["impact"]}</span>'

        feas_class = 'val-emerald' if s['feasibility'] >= 45 else ('val-amber' if s['feasibility'] >= 30 else 'val-rose')
        feas_html = f'<span class="val-pill {feas_class}">{s["feasibility"]}</span>'

        al_class = 'val-emerald' if s['alignment'] >= 45 else ('val-amber' if s['alignment'] >= 30 else 'val-rose')
        al_html = f'<span class="val-pill {al_class}">{s["alignment"]}</span>'

        safe_class = 'val-emerald' if s['safety'] >= 15.0 else ('val-amber' if s['safety'] >= 11.0 else 'val-rose')
        safe_html = f'<span class="val-pill {safe_class}">{s["safety"]:.2f}</span>'

        cost_class = 'val-emerald' if s['cost'] <= 12.0 else ('val-amber' if s['cost'] <= 15.0 else 'val-rose')
        cost_html = f'<span class="val-pill {cost_class}">{s["cost"]:.2f}</span>'

        if vetoed:
            fs_html = '<span class="val-pill val-rose">VETOED</span>'
        else:
            fs_html = f'<span class="val-pill val-emerald" style="font-weight:700;">{f_score:.2f}</span>'

        table_rows.append(f"""
        <tr {row_class}>
            <td style="font-weight: 700; color: #a5b4fc; text-align: center;">[{c_id}]</td>
            <td style="font-weight: 600; color: #f8fafc;">{title}</td>
            <td style="text-align: center;">{status_html}</td>
            <td style="text-align: center;">{imp_html}</td>
            <td style="text-align: center;">{feas_html}</td>
            <td style="text-align: center;">{al_html}</td>
            <td style="text-align: center;">{safe_html}</td>
            <td style="text-align: center;">{cost_html}</td>
            <td style="text-align: center;">{fs_html}</td>
        </tr>
        """)

    leaderboard_html = f"""
    <div class="decision-table-container">
        <table class="decision-table">
            <thead>
                <tr>
                    <th style="width: 6%; text-align: center;">ID</th>
                    <th style="width: 32%;">Candidate Name</th>
                    <th style="width: 12%; text-align: center;">Status</th>
                    <th style="width: 9%; text-align: center;">Impact ⚡</th>
                    <th style="width: 9%; text-align: center;">Feas. 🛠️</th>
                    <th style="width: 9%; text-align: center;">Align. 🎯</th>
                    <th style="width: 9%; text-align: center;">Safety 🛡️</th>
                    <th style="width: 9%; text-align: center;">Cost 💎</th>
                    <th style="width: 10%; text-align: center;">Final Score</th>
                </tr>
            </thead>
            <tbody>
                {"".join(table_rows)}
            </tbody>
        </table>
    </div>
    """
    clean_leaderboard_html = "\n".join(line.strip() for line in leaderboard_html.split("\n") if line.strip())
    st.markdown(clean_leaderboard_html, unsafe_allow_html=True)

    st.markdown('### 🕵️ Detailed Apostle Votes')

    # Parse candidate IDs for dropdown select
    all_candidate_ids = sorted(list(all_candidate_ids), key=sort_key)

    selected_c_id = st.selectbox(
        "Select Candidate for Detailed Breakdown",
        all_candidate_ids,
        format_func=lambda x: f"[{x}] {candidate_titles.get(x, f'Candidate {x}')}" + (" (Adopted)" if x in spawned_candidates else (" (Vetoed)" if scores[x]["veto"] else "")),
        key=f"detailed_votes_{inspect_id}"
    )

    if selected_c_id:
        apostle_rows = []
        sorted_apostles = sorted(votes_data.keys())

        for name in sorted_apostles:
            apostle_vote = None
            for v in votes_data[name]:
                if str(v.get('candidate_id')) == selected_c_id:
                    apostle_vote = v
                    break

            if not apostle_vote:
                continue

            imp = apostle_vote.get('impact_score', 0)
            feas = apostle_vote.get('feasibility_score', 0)
            al = apostle_vote.get('alignment_score', 0)
            safe = apostle_vote.get('safety_multiplier', 1.0)
            cost = apostle_vote.get('cost_multiplier', 1.0)
            veto = apostle_vote.get('veto', False)
            raw_reason = apostle_vote.get('reason', '')
            reason = raw_reason.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#x27;')

            imp_class = 'val-emerald' if imp >= 4 else ('val-amber' if imp == 3 else 'val-rose')
            imp_html = f'<span class="val-pill {imp_class}">{imp}</span>'

            feas_class = 'val-emerald' if feas >= 4 else ('val-amber' if feas == 3 else 'val-rose')
            feas_html = f'<span class="val-pill {feas_class}">{feas}</span>'

            al_class = 'val-emerald' if al >= 4 else ('val-amber' if al == 3 else 'val-rose')
            al_html = f'<span class="val-pill {al_class}">{al}</span>'

            safe_class = 'val-emerald' if safe > 1.0 else ('val-rose' if safe < 1.0 else 'val-neutral')
            safe_html = f'<span class="val-pill {safe_class}">{safe:.2f}</span>'

            cost_class = 'val-emerald' if cost < 1.0 else ('val-rose' if cost > 1.0 else 'val-neutral')
            cost_html = f'<span class="val-pill {cost_class}">{cost:.2f}</span>'

            veto_html = '<span class="status-badge status-vetoed">VETO</span>' if veto else '<span style="color: #34d399; font-weight:700;">No</span>'
            row_style = 'class="vetoed-row"' if veto else ''
            reason_html = f'<td class="reason-cell"><span class="custom-tooltip">💬<span class="tooltip-text">{reason}</span></span></td>'

            apostle_rows.append(f"""
            <tr {row_style}>
                <td style="font-weight: 700; color: #c7d2fe;">{name}</td>
                <td style="text-align: center;">{imp_html}</td>
                <td style="text-align: center;">{feas_html}</td>
                <td style="text-align: center;">{al_html}</td>
                <td style="text-align: center;">{safe_html}</td>
                <td style="text-align: center;">{cost_html}</td>
                <td style="text-align: center;">{veto_html}</td>
                {reason_html}
            </tr>
            """)

        detailed_table_html = f"""
        <div class="decision-table-container">
            <table class="decision-table">
                <thead>
                    <tr>
                        <th style="width: 25%;">Apostle Name</th>
                        <th style="width: 10%; text-align: center;">Impact ⚡</th>
                        <th style="width: 10%; text-align: center;">Feasibility 🛠️</th>
                        <th style="width: 10%; text-align: center;">Alignment 🎯</th>
                        <th style="width: 10%; text-align: center;">Safety Mult. 🛡️</th>
                        <th style="width: 10%; text-align: center;">Cost Mult. 💎</th>
                        <th style="width: 10%; text-align: center;">Veto</th>
                        <th style="width: 15%; text-align: center;">Apostle Reason (Hover)</th>
                    </tr>
                </thead>
                <tbody>
                    {"".join(apostle_rows)}
                </tbody>
            </table>
        </div>
        """
        clean_detailed_table_html = "\n".join(line.strip() for line in detailed_table_html.split("\n") if line.strip())
        st.markdown(clean_detailed_table_html, unsafe_allow_html=True)


# ─── Data ───────────────────────────────────────────────────────────────────
basenames = get_organism_basenames(WORKSPACE)
all_edges = build_edges(basenames)
descriptions = parse_decision_log_descriptions(WORKSPACE, basenames)
roots = find_root_seeds(basenames)

# ─── Read query params for click selection and zoom ─────────────────────────
params = st.query_params

def get_param(name, default):
    val = params.get(name, default)
    if isinstance(val, (list, tuple)):
        return val[0] if val else default
    return val

def set_query_params(**kwargs):
    try:
        for k, v in kwargs.items():
            st.query_params[k] = v
    except Exception:
        pass

reset_layout = get_param("reset_layout", "false")
if reset_layout == "true":
    set_query_params(reset_layout="false")

inspect_id = get_param("inspect", basenames[-1] if basenames else "0")
inspect_type = get_param("type", "node")
if inspect_id not in basenames and basenames:
    inspect_id = basenames[-1]
    inspect_type = "node"

idx = basenames.index(inspect_id) if inspect_id in basenames else (len(basenames)-1 if basenames else 0)

try:
    zoom_val = float(get_param("zoom", 1.0))
except Exception:
    zoom_val = 1.0
zoom_val = max(0.3, min(3.0, zoom_val))

next_root_id = "0"
if roots:
    ints = []
    for r in roots:
        try: ints.append(int(r))
        except: pass
    if ints:
        next_root_id = str(max(ints) + 1)

# ─── Git Commit & Version Helper ─────────────────────────────────────────────
def get_version_info() -> tuple[str, str]:
    version = "v1.3.0"
    commit_hash = "7a47a0f"
    if "pyodide" not in sys.modules:
        try:
            import subprocess
            res = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True)
            if res.returncode == 0 and res.stdout.strip():
                commit_hash = res.stdout.strip()
        except Exception:
            pass
    return version, commit_hash

# ─── Header ─────────────────────────────────────────────────────────────────
h1, h2, h3, h4, h5 = st.columns([5, 1, 1, 1, 1])
with h1:
    version, commit_hash = get_version_info()
    st.markdown(
        f'<div style="display: flex; align-items: center; gap: 16px;">'
        f'  <span class="main-title">🧬 13 Apostles System</span>'
        f'  <div style="display: flex; flex-direction: column; align-items: flex-start; justify-content: center; margin-top: 4px;">'
        f'    <span class="author-email" style="margin-left: 0; font-size: 0.82em; color: rgba(160,160,220,0.6); line-height: 1.2;">eljja1@gmail.com</span>'
        f'    <span style="font-size: 0.72em; font-weight: 600; color: #a5b4fc; background: rgba(99,102,241,0.15); padding: 2px 7px; border-radius: 10px; border: 1px solid rgba(99,102,241,0.25); letter-spacing: 0.02em; margin-top: 3px; line-height: 1.2; white-space: nowrap;">{version}</span>'
        f'    <span style="font-size: 0.68em; font-weight: 600; color: rgba(165,180,252,0.8); background: rgba(99,102,241,0.08); padding: 1.5px 6px; border-radius: 8px; border: 1px solid rgba(99,102,241,0.15); letter-spacing: 0.02em; margin-top: 2px; line-height: 1.2; white-space: nowrap;">({commit_hash})</span>'
        f'  </div>'
        f'</div>',
        unsafe_allow_html=True
    )
with h2:
    font_size = st.slider("Font Size", 4, 20, 7)
    root_font_size = font_size + 2
with h3:
    edge_length = st.slider("Arrow Length", 10, 150, 30)
with h4:
    zoom_level = st.slider("Zoom", 0.3, 3.0, zoom_val, step=0.05)
    if zoom_level != zoom_val:
        set_query_params(zoom=f"{zoom_level:.2f}")
        st.rerun()
with h5:
    st.markdown("<br>", unsafe_allow_html=True)
    c_btn1, c_btn2 = st.columns(2)
    with c_btn1:
        if st.button("🔄", key="refresh", help="Refresh and Reset Layout"):
            set_query_params(reset_layout="true")
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

# Query parameters are processed globally above

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
<style>
  html, body {{
    margin: 0;
    padding: 0;
    overflow: hidden;
    background: transparent;
    width: 100%;
    height: 100%;
  }}
</style>
<div id="cy" style="width:100%;height:{graph_h}px;background:rgba(8,8,24,0.6);
     border:1px solid rgba(99,102,241,0.12);border-radius:10px;cursor:grab;"></div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/cytoscape/3.28.1/cytoscape.min.js"></script>
<script>
var resetLayout = '{reset_layout}';
if (resetLayout === 'true') {{
  try {{
    localStorage.removeItem('13apostles:node_positions');
  }} catch(e) {{}}
}}

var savedPositions = null;
try {{
  savedPositions = JSON.parse(localStorage.getItem('13apostles:node_positions')) || {{}};
}} catch(e) {{}}

var hasAllPositions = true;
var elements = {elements_json};
var nodesOnly = elements.filter(function(el) {{ return el.data && !el.data.source; }});
nodesOnly.forEach(function(node) {{
  if (!savedPositions[node.data.id]) {{
    hasAllPositions = false;
  }}
}});

var layoutConfig;
if (hasAllPositions && resetLayout !== 'true') {{
  layoutConfig = {{
    name: 'preset',
    positions: function(node) {{
      return savedPositions[node.id()];
    }}
  }};
}} else {{
  layoutConfig = {{
    name: 'cose',
    animate: false, fit: false, padding: 40,
    nodeRepulsion: function(){{ return 12000; }},
    idealEdgeLength: function(){{ return {edge_length}; }},
    edgeElasticity: function(){{ return 80; }},
    gravity: 0.6, numIter: 800,
    componentSpacing: 140,
  }};
}}

function savePositions() {{
  var positions = {{}};
  cy.nodes().forEach(function(node) {{
    positions[node.id()] = node.position();
  }});
  try {{
    localStorage.setItem('13apostles:node_positions', JSON.stringify(positions));
  }} catch(e) {{}}
}}

var cy = cytoscape({{
  container: document.getElementById('cy'),
  elements: elements,
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
  layout: layoutConfig,
  zoom: {zoom_level},
  userZoomingEnabled: true, userPanningEnabled: true,
  boxSelectionEnabled: false, autoungrabify: false,
  minZoom: 0.1, maxZoom: 5.0,
  wheelSensitivity: 0.12,
}});
cy.ready(function() {{
    if (!hasAllPositions || resetLayout === 'true') {{
      cy.center();
      savePositions();
    }}
    var inspectType = '{inspect_type}';
    var inspectId = '{inspect_id}';
    if (inspectType === 'edge') {{
        cy.edges('[source = "' + inspectId + '"]').addClass('tapped');
    }} else {{
        var activeNode = cy.getElementById(inspectId);
        if (activeNode.length > 0) {{
            activeNode.addClass('tapped');
        }}
    }}
}});

cy.on('free', 'node', function() {{
  savePositions();
}});

cy.on('layoutstop', function() {{
  savePositions();
}});
function updateParent(params) {{
  try {{
    window.parent.postMessage({{
      type: 'streamlit:update_params',
      params: params
    }}, '*');
  }} catch (err) {{
    console.error("postMessage failed:", err);
  }}
}}

cy.on('tap', 'node', function(e) {{
  var id = e.target.id();
  cy.elements().removeClass('tapped');
  e.target.addClass('tapped');
  updateParent({{ 'inspect': id, 'type': 'node' }});
}});

cy.on('tap', 'edge', function(e) {{
  var src = e.target.source().id();
  cy.elements().removeClass('tapped');
  e.target.addClass('tapped');
  updateParent({{ 'inspect': src, 'type': 'edge' }});
}});

var zoomTimeout;
cy.on('zoom', function(e) {{
  clearTimeout(zoomTimeout);
  zoomTimeout = setTimeout(function() {{
    var z = cy.zoom();
    updateParent({{ 'zoom': z.toFixed(2) }});
  }}, 800);
}});
</script>
"""
st.iframe(cy_html, height=graph_h + 10)

# ─── Controls ───────────────────────────────────────────────────────────────
st.markdown("---")
c1, c2, c3, c4, c5, c6 = st.columns([2.5, 1.5, 1.5, 1.5, 1.5, 4.5])
with c1:
    target_node = st.selectbox("Evolve from", basenames, format_func=lambda x: f"{x}.py", index=idx)
    if target_node != inspect_id:
        set_query_params(inspect=target_node, type="node")
        st.rerun()
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
    sub_col1, sub_col2 = st.columns([3.5, 1])
    with sub_col1:
        with st.popover(f"▶ Evolve {target_node}.py", use_container_width=True):
            st.markdown("**🔒 Authorization Required**")
            st.caption("Please enter the system password to execute Gemini API evolution.")
            password = st.text_input("Enter Password", type="password", key="evo_password_input")
            run_btn = st.button("Confirm Speciation", type="primary", use_container_width=True)
    with sub_col2:
        stop_btn = st.button("🛑 Stop", type="secondary", use_container_width=True, disabled=not st.session_state.get("evo_active", False))

# Initialize evolution state variables in session_state if not present
if "evo_active" not in st.session_state:
    st.session_state.evo_active = False

if "latest_status" not in st.session_state:
    st.session_state.latest_status = []

if stop_btn:
    st.session_state.evo_active = False
    st.session_state.evo_queue = []
    st.session_state.evo_next_queue = []
    st.session_state.latest_status.append(("warning", "🛑 Evolution sequence was stopped manually by the user."))
    st.rerun()

if run_btn:
    if password == "pemspems1!":
        # Initialize the state machine for multi-generation evolution
        st.session_state.evo_active = True
        st.session_state.evo_queue = [f"{target_node}.py"]
        st.session_state.evo_next_queue = []
        st.session_state.evo_generation = 0
        st.session_state.evo_total_generations = generations
        st.session_state.evo_num_children = num_children
        st.session_state.evo_select_children = select_children
        st.session_state.evo_test_mode = test_mode
        st.session_state.latest_log = []
        st.session_state.latest_status = []
        st.rerun()
    else:
        st.error("🔒 Incorrect password! Speciation blocked.")

# ─── Gradual State Machine Evolution Executor ────────────────────────────────
if st.session_state.evo_active:
    queue = st.session_state.evo_queue
    next_queue = st.session_state.evo_next_queue
    gen = st.session_state.evo_generation
    total_gens = st.session_state.evo_total_generations
    num_children = st.session_state.evo_num_children
    select_children = st.session_state.evo_select_children
    actual_select = min(select_children, num_children)
    test_mode = st.session_state.evo_test_mode

    # If the queue is empty, transition generation or terminate
    if not queue:
        next_gen = gen + 1
        if next_gen < total_gens and next_queue:
            st.session_state.evo_queue = next_queue
            st.session_state.evo_next_queue = []
            st.session_state.evo_generation = next_gen
            st.rerun()
        else:
            st.session_state.evo_active = False
            # Automatically sync newly evolved files to GitHub main branch upon full completion
            auto_git_push()
            st.rerun()

    # Process exactly ONE node from the queue per rerun to allow instant UI refresh
    current = queue[0]
    current_base = current[:-3] if current.endswith(".py") else current
    
    st.markdown('<p class="section-label">🏃 Live Execution Log</p>', unsafe_allow_html=True)
    status_ph = st.empty()
    live_log_ph = st.empty()
    
    class LiveLogBox(io.StringIO):
        def __init__(self, ph):
            super().__init__()
            self.ph = ph
            self.lines = list(st.session_state.latest_log)
        def write(self, s):
            super().write(s)
            if s.strip():
                now_str = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
                for line in s.strip().split('\n'):
                    if line.strip():
                        self.lines.append(f"{now_str} {line.strip()}")
                self.ph.code("\n".join(self.lines[-3:]), language="text")

    # Check existing direct children for cache reuse
    existing_children = [c for p, c in all_edges if p == current_base]
    
    if len(existing_children) >= actual_select:
        selected_existing = [f"{c}.py" for c in sorted(existing_children)[:actual_select]]
        msg = f"♻️ Reused existing {len(selected_existing)} children for {current}: {', '.join(selected_existing)}"
        status_ph.info(msg)
        st.session_state.latest_status.append(("success", msg))
        
        # Advance state queue instantly
        st.session_state.evo_queue = queue[1:]
        st.session_state.evo_next_queue.extend(selected_existing)
        time.sleep(0.1)
        st.rerun()
    else:
        # Run actual evolution for the current target node
        with st.spinner(f"Generation {gen+1}/{total_gens}: Evolving {current} ..."):
            engine = EvolutionEngine(WORKSPACE, current)
            if test_mode:
                engine.apostles = engine.apostles[:3]
                
            old_stdout = sys.stdout
            buf = LiveLogBox(live_log_ph)
            sys.stdout = buf
            children_info, error = [], None
            try:
                children_info = engine.run(num_children=num_children)
            except Exception as e:
                error = str(e)
            finally:
                sys.stdout = old_stdout
            
            # Persist logs
            st.session_state.latest_log = buf.lines
            
            if error:
                msg = f"Error on {current}: {error}"
                status_ph.error(msg)
                st.session_state.latest_status.append(("error", msg))
            elif children_info:
                selected = children_info[:actual_select]
                msg = f"✅ {current} -> {', '.join(c['filename'] for c in selected)}"
                status_ph.success(msg)
                st.session_state.latest_status.append(("success", msg))
                st.session_state.evo_next_queue.extend([c['filename'] for c in selected])
            else:
                msg = f"⚠️ {current}: All dropped."
                status_ph.warning(msg)
                st.session_state.latest_status.append(("warning", msg))
            
            # Advance state queue
            st.session_state.evo_queue = queue[1:]
            
            # Instantly rerun: this rewrites the tree map with the newly created child, 
            # while keeping the next evolution step running seamlessly on the next cycle!
            time.sleep(0.1)
            st.rerun()

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

inspect = st.selectbox(
    "Node", basenames,
    format_func=lambda x: f"{x}.py" + (f"  — {descriptions[x]}" if x in descriptions else ""),
    index=idx,
)

if inspect != inspect_id:
    set_query_params(inspect=inspect, type="node")
    st.rerun()

# ─── Helper: Render Evolutionary Diversity Analyzer ─────────────────────────
def render_diversity_analyzer():

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
                    # ─── WebAssembly (Pyodide) In-Process Secure Execution ────────
                    if "pyodide" in sys.modules:
                        import io, contextlib
                        stdout_buffer = io.StringIO()
                        try:
                            # Prepare isolated execution namespace
                            local_ns = {}
                            with contextlib.redirect_stdout(stdout_buffer), contextlib.redirect_stderr(stdout_buffer):
                                exec(code, local_ns, local_ns)
                            output = stdout_buffer.getvalue().strip()
                            if not output:
                                output = "(Successful execution with no output)"
                        except Exception as e:
                            output = f"Error running code in Wasm sandbox: {str(e)}"
                    else:
                        # ─── Standard Subprocess Execution (Local Desktop) ───────────
                        try:
                            # H-1: Use Popen with process group to prevent zombie child processes
                            creationflags = 0
                            preexec_fn = None
                            if sys.platform == 'win32':
                                creationflags = subprocess.CREATE_NEW_PROCESS_GROUP
                            else:
                                preexec_fn = os.setsid

                            proc = subprocess.Popen(
                                [sys.executable, filepath],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                text=True,
                                cwd=WORKSPACE,
                                creationflags=creationflags,
                                preexec_fn=preexec_fn,
                            )
                            try:
                                stdout, stderr = proc.communicate(timeout=5)
                                if proc.returncode == 0:
                                    output = stdout.strip() if stdout.strip() else "(Successful execution with no output)"
                                else:
                                    output = f"Error (code {proc.returncode}):\n{stderr.strip()}"
                            except subprocess.TimeoutExpired:
                                # Kill entire process group to prevent zombies
                                try:
                                    if sys.platform == 'win32':
                                        proc.kill()
                                    else:
                                        os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
                                except OSError:
                                    proc.kill()
                                proc.wait()
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


if inspect:
    if inspect_type == "edge":
        log = load_decision_log(WORKSPACE, inspect)
        if log:
            # Strip the redundant first-line title if it duplicates the visual header
            lines = log.splitlines()
            if lines and lines[0].strip().startswith("# Decision Log:"):
                log = "\n".join(lines[1:]).strip()

            t_log, t_vote, t_div = st.tabs(["📋 Decision Log", "🗳️ Voting Results", "🧬 Diversity"])
            with t_log:
                render_decision_log_text(log)
            with t_vote:
                render_decision_log_votes_table(log, inspect)
            with t_div:
                render_diversity_analyzer()
        else:
            st.info("No decision log.")
    else:
        # Load decision log first to avoid duplicate calls
        log = load_decision_log(WORKSPACE, inspect)
        if log:
            lines = log.splitlines()
            if lines and lines[0].strip().startswith("# Decision Log:"):
                log = "\n".join(lines[1:]).strip()

        t_code, t_log, t_vote, t_div = st.tabs(["💻 Code", "📋 Decision Log", "🗳️ Voting Results", "🧬 Diversity"])
        with t_code:
            code = load_code(WORKSPACE, inspect)
            if code:
                st.code(code, language="python", line_numbers=True)
            else:
                st.info("No source file.")
        with t_log:
            if log:
                render_decision_log_text(log)
            else:
                st.info("No decision log.")
        with t_vote:
            if log:
                render_decision_log_votes_table(log, inspect)
            else:
                st.info("No voting data available for this seed node.")
        with t_div:
            render_diversity_analyzer()
else:
    # No node/edge selected — show Diversity Analyzer as standalone
    st.markdown("---")
    st.markdown('<p class="section-label">🧬 Evolutionary Diversity Analyzer</p>', unsafe_allow_html=True)
    render_diversity_analyzer()

# ─── Footer ─────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="footer">Powered by eljja1@gmail.com · 13 Apostles System</div>',
    unsafe_allow_html=True,
)
