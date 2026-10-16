"""Fill a Word or Excel template from a project file plus document-specific values.

Usage:
    python tools/fill_template.py templates/word/Priced_Variation_Notice_TEMPLATE.docx \\
        --project my_project.yaml --spec var_003.yaml \\
        --out out/VAR-003_Priced_Variation_Notice.docx

Word templates take four kinds of value, from the command line or a --spec file:

  set      [PLACEHOLDER] -> value          --set VAR_NUMBER=VAR-003
  replace  literal text -> new text        --replace "[SELECT: 7/14/30 days]=>14 days"
  cell     table cell starting with text   --cell "[Describe the variation=>New text"
           -> whole new cell text (newlines become paragraphs)
  row      table row whose first cell      --row "Labour=$1,413.53"
           starts with a label -> the      --row "Subtotal (excl. GST)#2=$2,811.00|$3,302.93|$491.93"
           next cells, split on |. #2 picks the second matching row.

A --spec file is YAML with the same four keys:

    set: {VAR_NUMBER: VAR-003, DD/MM/YYYY: 16/10/2026}
    replace: {"[SELECT: 7/14/30 days]": "14 days"}
    cell: {"[Describe the variation": "Supply and install ..."}
    row: {"Labour": "$1,413.53", "Subtotal (excl. GST)#2": "$2,811.00|$3,302.93|$491.93"}

Excel: the "Setup" sheet is filled by matching its labels (Business Name:, ABN: ...).

Prints a JSON report: what was filled, placeholders still in the document,
bracketed instructions not yet replaced, and any replace/cell/row that
matched nothing.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).parent))

# Placeholders the fill tool never touches: the user inserts an image.
LEAVE_FOR_USER = {"[LOGO]"}

# Excel Setup sheet label -> project field.
SETUP_LABELS = {
    "business name": "business_name",
    "abn": "abn",
    "builder licence": "licence_number",
    "licence": "licence_number",
    "address": "business_address",
    "phone": "phone",
    "email": "email",
    "project name": "project_name",
    "project address": "project_address",
    "client name": "client_name",
    "contract number": "contract_number",
    "contract type": "contract_type",
    "original contract sum": "contract_sum",
    "contract sum": "contract_sum",
    "contract date": "contract_date",
    "start date": "start_date",
    "completion date": "end_date",
}
NUMERIC_FIELDS = {"contract_sum"}


def load_values(project: Path | None, sets: list[str]) -> dict[str, str]:
    """Flatten the project file to {FIELD: value} and apply --set overrides."""
    values: dict[str, str] = {}
    if project:
        data = yaml.safe_load(project.read_text()) or {}
        stack = [data]
        while stack:
            node = stack.pop()
            for key, val in node.items():
                if isinstance(val, dict):
                    stack.append(val)
                elif val is not None:
                    values[str(key).upper()] = str(val)
    for item in sets:
        key, sep, val = item.partition("=")
        if not sep:
            raise SystemExit(f"--set expects KEY=VALUE, got {item!r}")
        values[key.strip().strip("[]").upper()] = val
    return values


def fill_docx(src: Path, out: Path, values: dict[str, str], replaces: dict[str, str],
              cells: dict[str, str], rows: dict[str, str]) -> dict:
    from docx import Document
    from docx_tools import (cell_text, find_placeholders, iter_cells, iter_paragraphs,
                            replace_in_document, set_cell_text)

    doc = Document(src)
    filled: set[str] = set()
    unmatched: list[str] = []

    # Whole cells first, so their instruction text is gone before other passes.
    for prefix, text in cells.items():
        for row in iter_cells(doc):
            hit = next((c for c in row if cell_text(c).startswith(prefix)), None)
            if hit is not None:
                set_cell_text(hit, text)
                break
        else:
            unmatched.append(f"cell: {prefix}")

    for spec, text in rows.items():
        label, _, nth = spec.partition("#")
        want = int(nth or 1)
        seen = 0
        for row in iter_cells(doc):
            if len(row) > 1 and cell_text(row[0]).strip().startswith(label):
                seen += 1
                if seen == want:
                    for cell, val in zip(row[1:], text.split("|")):
                        set_cell_text(cell, val)
                    break
        else:
            unmatched.append(f"row: {spec}")

    for old, new in replaces.items():
        if not replace_in_document(doc, lambda _m, new=new: new, re.compile(re.escape(old))):
            unmatched.append(f"replace: {old}")

    def placeholder(token: str) -> str | None:
        if token in LEAVE_FOR_USER:
            return None
        val = values.get(token[1:-1])
        if val is not None:
            filled.add(token)
        return val

    replace_in_document(doc, placeholder)
    doc.save(out)

    instructions = set()
    for p in iter_paragraphs(doc):
        for m in re.finditer(r"\[(SELECT:|[A-Z][a-z])[^\]]*\]?", p.text):
            instructions.add(m.group(0)[:60])
    return {"filled": sorted(filled), "remaining": sorted(find_placeholders(doc)),
            "instructions_left": sorted(instructions), "unmatched": unmatched}


def fill_xlsx(src: Path, out: Path, values: dict[str, str]) -> dict:
    import openpyxl

    wb = openpyxl.load_workbook(src)
    filled, unmatched = [], []
    if "Setup" in wb.sheetnames:
        ws = wb["Setup"]
        for row in ws.iter_rows(min_col=1, max_col=2):
            label_cell, value_cell = row
            if not isinstance(label_cell.value, str) or not label_cell.value.strip().endswith(":"):
                continue
            label = re.sub(r"\s*:$", "", label_cell.value.strip()).lower()
            field = SETUP_LABELS.get(label)
            val = values.get(field.upper()) if field else None
            if val is None:
                unmatched.append(label_cell.value.strip())
                continue
            if field in NUMERIC_FIELDS:
                val = float(val.replace(",", "").replace("$", ""))
            value_cell.value = val
            filled.append(label_cell.value.strip())
    wb.save(out)
    return {"filled": filled, "remaining": unmatched}


def pair(item: str, sep: str) -> tuple[str, str]:
    key, found, val = item.partition(sep)
    if not found:
        raise SystemExit(f"expected KEY{sep}VALUE, got {item!r}")
    return key, val


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("template", type=Path)
    parser.add_argument("--project", type=Path, help="project YAML file")
    parser.add_argument("--spec", type=Path, help="YAML file with set/replace/cell/row values")
    parser.add_argument("--set", action="append", default=[], metavar="KEY=VALUE",
                        help="document-specific value, repeatable")
    parser.add_argument("--replace", action="append", default=[], metavar="OLD=>NEW")
    parser.add_argument("--cell", action="append", default=[], metavar="PREFIX=>TEXT")
    parser.add_argument("--row", action="append", default=[], metavar="LABEL[#N]=V1|V2")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    spec = yaml.safe_load(args.spec.read_text()) if args.spec else {}
    spec = spec or {}
    sets = [f"{k}={v}" for k, v in (spec.get("set") or {}).items()] + args.set
    values = load_values(args.project, sets)
    replaces = {str(k): str(v) for k, v in (spec.get("replace") or {}).items()}
    replaces.update(pair(x, "=>") for x in args.replace)
    cells = {str(k): str(v) for k, v in (spec.get("cell") or {}).items()}
    cells.update(pair(x, "=>") for x in args.cell)
    rows = {str(k): str(v) for k, v in (spec.get("row") or {}).items()}
    rows.update(pair(x, "=") for x in args.row)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    suffix = args.template.suffix.lower()
    if suffix == ".docx":
        report = fill_docx(args.template, args.out, values, replaces, cells, rows)
    elif suffix == ".xlsx":
        report = fill_xlsx(args.template, args.out, values)
    else:
        raise SystemExit(f"Can't fill {suffix} files. PDFs in templates/pdf are reference checklists.")
    report["out"] = str(args.out)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
