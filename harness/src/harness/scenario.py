from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal
import yaml


@dataclass
class Scenario:
    name: str
    category: str
    difficulty: str
    type: Literal["model", "agent"]
    description: str
    tags: list[str]
    prompt: str
    grading_criteria: str | None = None
    suites: list[str] = field(default_factory=list)

    @classmethod
    def load(cls, path: Path) -> "Scenario":
        text = path.read_text()
        if not text.startswith("---"):
            raise ValueError(f"{path}: missing YAML front matter")
        _, front, body = text.split("---", 2)
        meta = yaml.safe_load(front)

        # Normalise suite: "name" or suite: [a, b] → always a list
        raw_suite = meta.pop("suite", None)
        if raw_suite is None:
            meta["suites"] = []
        elif isinstance(raw_suite, list):
            meta["suites"] = raw_suite
        else:
            meta["suites"] = [raw_suite]

        return cls(prompt=body.strip(), **meta)


def load_all(scenarios_dir: Path) -> list[Scenario]:
    return [Scenario.load(p) for p in sorted(scenarios_dir.glob("**/*.md"))]
