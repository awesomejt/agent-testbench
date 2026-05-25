import textwrap
from pathlib import Path
import pytest
from src.harness.scenario import Scenario, load_all


def write_scenario(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / f"{name}.md"
    p.write_text(textwrap.dedent(content))
    return p


# ── Scenario.load ─────────────────────────────────────────────────────────────

def test_load_valid_model_scenario(tmp_path):
    p = write_scenario(tmp_path, "smoke", """\
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
    assert s.category == "coding"
    assert s.difficulty == "easy"
    assert s.tags == ["smoke"]
    assert "hello world" in s.prompt
    assert s.grading_criteria is None
    assert s.suites == []


def test_load_valid_agent_scenario(tmp_path):
    p = write_scenario(tmp_path, "agent", """\
        ---
        name: refactor
        category: coding
        difficulty: hard
        type: agent
        description: Refactor task
        tags: [refactor, python]
        ---
        Refactor this module.
    """)
    s = Scenario.load(p)
    assert s.type == "agent"
    assert s.tags == ["refactor", "python"]


def test_load_strips_prompt_whitespace(tmp_path):
    p = write_scenario(tmp_path, "ws", """\
        ---
        name: ws
        category: misc
        difficulty: easy
        type: model
        description: Whitespace test
        tags: []
        ---

        Prompt with leading blank line.
    """)
    s = Scenario.load(p)
    assert not s.prompt.startswith("\n")


def test_load_missing_front_matter_raises(tmp_path):
    p = write_scenario(tmp_path, "bad", "Just a plain prompt with no front matter.\n")
    with pytest.raises(ValueError, match="missing YAML front matter"):
        Scenario.load(p)


def test_load_empty_tags(tmp_path):
    p = write_scenario(tmp_path, "notags", """\
        ---
        name: notags
        category: misc
        difficulty: easy
        type: model
        description: No tags
        tags: []
        ---
        Prompt.
    """)
    s = Scenario.load(p)
    assert s.tags == []


# ── load_all ──────────────────────────────────────────────────────────────────

def test_load_all_finds_md_files(tmp_path):
    write_scenario(tmp_path, "a", """\
        ---
        name: a
        category: misc
        difficulty: easy
        type: model
        description: A
        tags: []
        ---
        Prompt A.
    """)
    write_scenario(tmp_path, "b", """\
        ---
        name: b
        category: misc
        difficulty: easy
        type: model
        description: B
        tags: []
        ---
        Prompt B.
    """)
    scenarios = load_all(tmp_path)
    assert len(scenarios) == 2
    assert {s.name for s in scenarios} == {"a", "b"}


def test_load_all_ignores_non_md(tmp_path):
    write_scenario(tmp_path, "valid", """\
        ---
        name: valid
        category: misc
        difficulty: easy
        type: model
        description: Valid
        tags: []
        ---
        Prompt.
    """)
    (tmp_path / "notes.txt").write_text("not a scenario")
    scenarios = load_all(tmp_path)
    assert len(scenarios) == 1


def test_load_all_empty_dir(tmp_path):
    assert load_all(tmp_path) == []


# ── Grading criteria and suite fields ────────────────────────────────────────

def test_load_grading_criteria(tmp_path):
    p = write_scenario(tmp_path, "graded", """\
        ---
        name: graded
        category: math
        difficulty: easy
        type: model
        description: Graded scenario
        tags: []
        grading_criteria: The answer must be exactly 42.
        ---
        What is 6 times 7?
    """)
    s = Scenario.load(p)
    assert s.grading_criteria == "The answer must be exactly 42."


def test_load_single_suite(tmp_path):
    p = write_scenario(tmp_path, "s", """\
        ---
        name: s
        category: math
        difficulty: easy
        type: model
        description: Suite test
        tags: []
        suite: math-exam
        ---
        Prompt.
    """)
    s = Scenario.load(p)
    assert s.suites == ["math-exam"]


def test_load_multiple_suites(tmp_path):
    p = write_scenario(tmp_path, "m", """\
        ---
        name: m
        category: math
        difficulty: easy
        type: model
        description: Multi-suite test
        tags: []
        suite: [math-exam, algebra-basics]
        ---
        Prompt.
    """)
    s = Scenario.load(p)
    assert s.suites == ["math-exam", "algebra-basics"]


def test_load_no_suite_defaults_empty(tmp_path):
    p = write_scenario(tmp_path, "nosuite", """\
        ---
        name: nosuite
        category: misc
        difficulty: easy
        type: model
        description: No suite
        tags: []
        ---
        Prompt.
    """)
    s = Scenario.load(p)
    assert s.suites == []
