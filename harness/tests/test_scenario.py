import textwrap
from pathlib import Path
import pytest
from src.harness.scenario import Scenario


def write_scenario(tmp_path: Path, content: str) -> Path:
    p = tmp_path / "test.md"
    p.write_text(textwrap.dedent(content))
    return p


def test_load_valid_scenario(tmp_path):
    p = write_scenario(tmp_path, """\
        ---
        name: smoke
        category: coding
        difficulty: easy
        type: model
        description: Simple smoke test
        tags: [smoke]
        ---
        Write hello world in Python.
    """)
    s = Scenario.load(p)
    assert s.name == "smoke"
    assert s.type == "model"
    assert "hello world" in s.prompt


def test_load_missing_front_matter_raises(tmp_path):
    p = write_scenario(tmp_path, "Just a plain prompt with no front matter.\n")
    with pytest.raises(ValueError, match="missing YAML front matter"):
        Scenario.load(p)
