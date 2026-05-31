"""
tree_parser.py — Multi-organism evolution tree parser.

Parses the workspace to find all organism seeds (0.py, 1.py, ...),
builds parent-child relationships from file naming convention,
and extracts decision log descriptions from .md files.

Naming convention:
  - Root seed:  {digit}.py          e.g. 0.py, 1.py
  - Children:   {parent}{id}.py     e.g. 01.py, 0a.py (children of 0.py)
  - Grandchild: {parent}{id}.py     e.g. 01a.py        (child of 01.py)

A node is a ROOT if no other organism basename is a strict prefix of it.
"""

import os
import re
import sys

# Files that belong to the framework, not organisms
FRAMEWORK_FILES = {
    'app', 'evolution', 'llm_client', 'magi_engine',
    'simulate_gen_0', 'tree_parser', 'setup', 'conftest',
}


def get_organism_basenames(workspace_dir: str) -> list[str]:
    """Return sorted list of organism .py basenames (digit-starting, non-framework)."""
    # ─── WebAssembly (Pyodide) Virtual Filesystem Override ──────────────────────
    if "pyodide" in sys.modules:
        import json
        json_path = os.path.join(workspace_dir, "organism_basenames.json")
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return sorted(data)
        except Exception as e:
            print(f"[stlite-patch] Failed to load basenames from JSON: {e}")

    basenames = []
    for f in sorted(os.listdir(workspace_dir)):
        if not f.endswith('.py'):
            continue
        base = f[:-3]
        if base in FRAMEWORK_FILES:
            continue
        if base.startswith('__') or base.startswith('.'):
            continue
        if base and base[0].isdigit():
            basenames.append(base)
    return basenames


def find_root_seeds(basenames: list[str]) -> list[str]:
    """
    Find root seed basenames — nodes that have no other node as a prefix.
    e.g. ['0', '01', '01a', '1', '10'] → roots = ['0', '1']
    """
    roots = []
    for b in basenames:
        is_child = any(
            other != b and b.startswith(other)
            for other in basenames
        )
        if not is_child:
            roots.append(b)
    return sorted(roots)


def find_root_for(basename: str, basenames: list[str]) -> str | None:
    """Find the root seed that a given basename belongs to."""
    prefixes = [other for other in basenames if other != basename and basename.startswith(other)]
    if not prefixes:
        return basename  # It is itself a root
    # Walk up to the shortest prefix (the root)
    root_candidate = min(prefixes, key=len)
    return find_root_for(root_candidate, basenames)


def build_edges(basenames: list[str]) -> list[tuple[str, str]]:
    """
    Build direct parent→child edges.
    The direct parent of a node is its longest prefix that exists in basenames.
    Includes cycle detection: edges that would create a cycle are skipped.
    """
    edges = []
    children_of = {}  # Track children for cycle detection
    for b in basenames:
        prefixes = [other for other in basenames if other != b and b.startswith(other)]
        if prefixes:
            parent = max(prefixes, key=len)  # longest prefix = direct parent
            # Cycle guard: ensure parent is not a descendant of b
            # (should be impossible with prefix naming, but defensive)
            ancestor = parent
            cycle_detected = False
            visited = set()
            while ancestor in children_of:
                if ancestor in visited or ancestor == b:
                    cycle_detected = True
                    break
                visited.add(ancestor)
                # Walk up: find parent of ancestor
                anc_prefixes = [o for o in basenames if o != ancestor and ancestor.startswith(o)]
                if anc_prefixes:
                    ancestor = max(anc_prefixes, key=len)
                else:
                    break
            if not cycle_detected:
                edges.append((parent, b))
                children_of.setdefault(parent, []).append(b)
    return edges


def parse_decision_log_descriptions(workspace_dir: str, basenames: list[str]) -> dict[str, str]:
    """
    Extract short titles for child nodes from all .md decision logs.
    Returns {child_basename: title_string}
    """
    descriptions = {}
    
    # ─── WebAssembly (Pyodide) Virtual Filesystem Patch ────────────────────────
    # In Pyodide WebAssembly, individual markdown files aren't in VFS.
    # We load descriptions directly from the pre-bundled detailed_decision_analysis.json.
    if "pyodide" in sys.modules or not any(os.path.exists(os.path.join(workspace_dir, f"{b}.md")) for b in basenames):
        json_path = os.path.join(workspace_dir, "detailed_decision_analysis.json")
        if os.path.exists(json_path):
            try:
                import json
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                for parent_name, parent_data in data.items():
                    candidates_map = {str(c["id"]): c["title"] for c in parent_data.get("candidates", [])}
                    for child in parent_data.get("children", []):
                        child_fn = child.get("filename", "")
                        if child_fn.endswith(".py"):
                            child_base = child_fn[:-3]
                            cand_id = str(child.get("parent_candidate_id", ""))
                            if cand_id in candidates_map:
                                descriptions[child_base] = candidates_map[cand_id]
            except Exception as e:
                print(f"[stlite-patch] Failed to parse descriptions from detailed_decision_analysis.json: {e}")
        if descriptions:
            return descriptions

    for base in basenames:
        md_path = os.path.join(workspace_dir, f"{base}.md")
        if not os.path.exists(md_path):
            continue
        try:
            with open(md_path, 'r', encoding='utf-8') as f:
                content = f.read()
            match = re.search(r'## Children Spawned\n(.*?)(?:\n##|\Z)', content, re.DOTALL)
            if match:
                for line in match.group(1).strip().split('\n'):
                    m = re.search(r'- \*\*(.*?)\.py\*\* <- \[(.*?)\] (.*)', line)
                    if m:
                        descriptions[m.group(1)] = m.group(3).strip()
        except Exception:
            pass
    return descriptions


def load_objective(workspace_dir: str, root_basename: str) -> str | None:
    """Load the local objective .md for a root seed, if it exists."""
    # ─── WebAssembly (Pyodide) HTTP Fetching Patch ──────────────────────────────
    if "pyodide" in sys.modules:
        from pyodide.http import open_url
        import time
        try:
            url = f"./{root_basename}.objective.md?v={int(time.time())}"
            return open_url(url).read()
        except Exception:
            return None

    obj_path = os.path.join(workspace_dir, f"{root_basename}.objective.md")
    if os.path.exists(obj_path):
        with open(obj_path, 'r', encoding='utf-8') as f:
            return f.read()
    return None


def load_decision_log(workspace_dir: str, basename: str) -> str | None:
    """Load the full decision log .md for a node, or dynamically extract it from ancestors."""
    # ─── WebAssembly (Pyodide) HTTP Fetching Patch ──────────────────────────────
    if "pyodide" in sys.modules:
        from pyodide.http import open_url
        import time
        try:
            url = f"./{basename}.md?v={int(time.time())}"
            return open_url(url).read()
        except Exception:
            pass

    md_path = os.path.join(workspace_dir, f"{basename}.md")
    if os.path.exists(md_path):
        with open(md_path, 'r', encoding='utf-8') as f:
            return f.read()

    # Fallback: extract from nearest ancestor .md file
    basenames = get_organism_basenames(workspace_dir)
    ancestors = [b for b in basenames if b != basename and basename.startswith(b)]
    ancestors = sorted(ancestors, key=len, reverse=True)

    for ancestor in ancestors:
        content = None
        if "pyodide" in sys.modules:
            from pyodide.http import open_url
            import time
            try:
                url = f"./{ancestor}.md?v={int(time.time())}"
                content = open_url(url).read()
            except Exception:
                pass
        else:
            anc_md_path = os.path.join(workspace_dir, f"{ancestor}.md")
            if os.path.exists(anc_md_path):
                try:
                    with open(anc_md_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                except Exception:
                    pass

        if content:
            try:
                # Search for basename in the ancestor's spawned list to get the candidate key
                pattern = r'-\s*\*\*' + re.escape(basename) + r'\.py\*\*\s*<-\s*\[(.*?)\]'
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    key = match.group(1).strip()

                    # Find the candidate section starting with `### [key]`
                    sec_pattern = r'^###\s*\[\s*' + re.escape(key) + r'\s*\].*$'
                    sec_match = re.search(sec_pattern, content, re.MULTILINE)
                    if sec_match:
                        start_idx = sec_match.end()

                        # Try to extract the markdown code block inside the section
                        code_start_match = re.search(r'```(?:markdown)?\s*\n', content[start_idx:], re.IGNORECASE)
                        if code_start_match:
                            block_start = start_idx + code_start_match.end()
                            code_end_match = re.search(r'\n```', content[block_start:])
                            if code_end_match:
                                block_end = block_start + code_end_match.start()
                                extracted_content = content[block_start:block_end].strip()
                                return f"# Decision Log for {basename}.py\n*Extracted from candidate [{key}] in {ancestor}.md*\n\n{extracted_content}"

                        # If no markdown code block is found, extract until the next header
                        end_pattern = r'^(?:###|##)\s'
                        end_match = re.search(end_pattern, content[start_idx:], re.MULTILINE)
                        if end_match:
                            sec_content = content[start_idx : start_idx + end_match.start()].strip()
                        else:
                            sec_content = content[start_idx:].strip()
                        return f"# Decision Log for {basename}.py\n*Extracted from candidate [{key}] in {ancestor}.md*\n\n{sec_content}"
            except Exception:
                pass

    return None


def load_code(workspace_dir: str, basename: str) -> str | None:
    """Load the Python source of a node."""
    # ─── WebAssembly (Pyodide) HTTP Fetching Patch ──────────────────────────────
    if "pyodide" in sys.modules:
        from pyodide.http import open_url
        import time
        try:
            url = f"./{basename}.py?v={int(time.time())}"
            return open_url(url).read()
        except Exception as e:
            print(f"[stlite-patch] Failed to fetch {basename}.py over HTTP: {e}")
            pass

    py_path = os.path.join(workspace_dir, f"{basename}.py")
    if os.path.exists(py_path):
        with open(py_path, 'r', encoding='utf-8') as f:
            return f.read()
    return None


def build_mermaid(nodes: list[str], edges: list[tuple[str, str]],
                  descriptions: dict[str, str], highlight: str | None = None) -> str:
    """Generate a Mermaid graph TD diagram for a single tree."""
    lines = ['graph TD']
    for node in nodes:
        label = f"{node}.py"
        if node in descriptions:
            # Truncate long descriptions
            desc = descriptions[node]
            if len(desc) > 40:
                desc = desc[:37] + '...'
            label += f'<br/><i style="font-size:0.8em">{desc}</i>'
        style = ''
        if node == highlight:
            style = f'    style {node} fill:#6366f1,color:#fff,stroke:#8b5cf6\n'
        lines.append(f'    {node}["{label}"]')
        if style:
            lines.append(style.strip())
    for parent, child in edges:
        lines.append(f'    {parent} --> {child}')
    return '\n'.join(lines)


def build_full_tree_data(workspace_dir: str) -> tuple[dict, list[str]]:
    """
    Build complete multi-tree data for the workspace.

    Returns:
        trees: dict keyed by root basename, each with:
            'nodes'        : list of all basenames in this tree
            'edges'        : list of (parent, child) tuples
            'descriptions' : dict {child_basename: short_title}
            'objective'    : string content of objective.md, or None
        roots: sorted list of root basenames
    """
    basenames = get_organism_basenames(workspace_dir)
    roots = find_root_seeds(basenames)
    all_edges = build_edges(basenames)
    descriptions = parse_decision_log_descriptions(workspace_dir, basenames)

    trees = {}
    for root in roots:
        tree_nodes = sorted([b for b in basenames if b == root or b.startswith(root)])
        tree_edges = [(p, c) for p, c in all_edges if p in tree_nodes]
        tree_descs = {b: descriptions[b] for b in tree_nodes if b in descriptions}
        objective = load_objective(workspace_dir, root)

        trees[root] = {
            'nodes': tree_nodes,
            'edges': tree_edges,
            'descriptions': tree_descs,
            'objective': objective,
        }

    return trees, roots
