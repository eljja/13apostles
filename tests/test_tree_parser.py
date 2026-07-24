import os
import pytest
from tree_parser import get_organism_basenames, build_edges, find_root_seeds

@pytest.fixture
def temp_workspace(tmp_path):
    d = tmp_path / "workspace"
    d.mkdir()
    
    # Create some mock organism files
    (d / "0.py").write_text("# seed 0")
    (d / "1.py").write_text("# seed 1")
    (d / "01.py").write_text("# child 01")
    (d / "0a.py").write_text("# child 0a")
    (d / "1a.py").write_text("# child 1a")
    
    # Non-organism file
    (d / "app.py").write_text("# framework")
    (d / "README.md").write_text("# readme")
    
    return str(d)

def test_get_organism_basenames(temp_workspace):
    basenames = get_organism_basenames(temp_workspace)
    assert set(basenames) == {"0", "1", "01", "0a", "1a"}
    assert "app" not in basenames

def test_build_edges(temp_workspace):
    basenames = get_organism_basenames(temp_workspace)
    edges = build_edges(basenames)
    
    # "0" -> "01", "0" -> "0a"
    # "1" -> "1a"
    expected = [("0", "01"), ("0", "0a"), ("1", "1a")]
    assert set(edges) == set(expected)

def test_find_root_seeds(temp_workspace):
    basenames = get_organism_basenames(temp_workspace)
    roots = find_root_seeds(basenames)
    
    assert set(roots) == {"0", "1"}
