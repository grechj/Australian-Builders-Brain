"""Fill every example spec and fail if anything is left unfilled.

Usage:
    python tools/test_examples.py

Each examples/*_spec.yaml names its template on a `template:` line. Every
example must fill with nothing left over except [LOGO], which is for the
user to insert. Run this after changing a template, a spec or the fill tool.
"""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))


def docx_text(path: Path) -> str:
    from docx import Document
    from docx_tools import iter_paragraphs

    return "\n".join(p.text for p in iter_paragraphs(Document(path)))
ALLOWED = {"[LOGO]"}


def main() -> None:
    failures = 0
    specs = sorted((ROOT / "examples").glob("*_spec.yaml"))
    with tempfile.TemporaryDirectory() as tmp:
        for spec in specs:
            template = (yaml.load(spec.read_text(), Loader=yaml.BaseLoader) or {}).get("template")
            if not template:
                print(f"SKIP {spec.name}: no template: line")
                continue
            out = Path(tmp) / (spec.stem + Path(template).suffix)
            run = subprocess.run([sys.executable, str(ROOT / "tools" / "fill_template.py"), str(ROOT / template),
                                  "--project", str(ROOT / "examples" / "project_example.yaml"),
                                  "--spec", str(spec), "--out", str(out)], capture_output=True, text=True)
            if run.returncode:
                failures += 1
                print(f"FAIL {spec.name}: {run.stderr.strip().splitlines()[-1]}")
                continue
            report = json.loads(run.stdout)
            data = yaml.load(spec.read_text(), Loader=yaml.BaseLoader) or {}
            if out.suffix == ".docx":
                text = docx_text(out)
                # Every tick and every row value must actually be in the document.
                missing = [f"tick: {t}" for t in data.get("tick") or [] if f"☒ {t}" not in text]
                for label, vals in (data.get("row") or {}).items():
                    for val in str(vals).split("|"):
                        if val.strip() and val.strip() not in text:
                            missing.append(f"row {label}: {val.strip()!r} not in output")
                report.setdefault("unmatched", []).extend(missing)
            left = [x for x in report.get("remaining", []) if x not in ALLOWED and not str(x).endswith(":")]
            left += report.get("instructions_left", []) + report.get("unmatched", [])
            print(("FAIL " if left else "OK   ") + spec.name + (f": {left}" if left else ""))
            failures += bool(left)
    print(f"{len(specs) - failures}/{len(specs)} examples clean")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
