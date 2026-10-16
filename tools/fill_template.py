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

For Excel templates, `cell` keys are cell addresses and values go into input
cells only: --cell "Claims!C6=>100%" (a trailing % is stored as a fraction).

Two more keys work in a --spec file only (Word):

  add_row     insert new rows after the row whose first cell starts with a label,
              copying its formatting: {"Description": ["Deposit|$22,045.45|100%|$22,045.45|$0.00"]}
  delete_row  remove rows by label: ["Fixing Stage"]
  tick        tick check boxes by their label: ["Inclement weather"] turns "☐ Inclement weather" into "☒ ..."

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
    "contract sum (incl gst)": "contract_sum",
    "contract sum (excl gst)": "contract_sum_ex_gst",
    "original contract sum (excl gst)": "contract_sum_ex_gst",
    "retention %": "retention_pct",
    "client phone": "client_phone",
    "client email": "client_email",
    "client address": "client_address",
    "contract date": "contract_date",
    "start date": "start_date",
    "end date": "end_date",
    "completion date": "end_date",
    "pc date": "pc_date",
    "dlp end date": "dlp_end_date",
    "site supervisor": "site_supervisor",
    "quote number": "quote_number",
    "quote date": "quote_date",
}
NUMERIC_FIELDS = {"contract_sum", "contract_sum_ex_gst"}
# Entered as a whole percentage (5), stored by Excel as a fraction (0.05).
PERCENT_FIELDS = {"retention_pct"}


def load_values(project: Path | None, sets: list[str]) -> dict[str, str]:
    """Flatten the project file to {FIELD: value} and apply --set overrides."""
    values: dict[str, str] = {}
    if project:
        data = yaml.load(project.read_text(), Loader=yaml.BaseLoader) or {}  # every value as typed, e.g. "565.00"
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
              cells: dict[str, str], rows: dict[str, str],
              add_rows: dict[str, list[str]] | None = None,
              delete_rows: list[str] | None = None,
              ticks: list[str] | None = None) -> dict:
    from docx import Document
    from copy import deepcopy

    from docx.oxml.ns import qn
    from docx.table import _Cell
    from docx_tools import (cell_text, find_placeholders, iter_cells, iter_paragraphs,
                            replace_in_document, set_cell_text)

    doc = Document(src)
    filled: set[str] = set()
    unmatched: list[str] = []

    def find_row(spec: str):
        label, _, nth = spec.partition("#")
        want, seen = int(nth or 1), 0
        for row in iter_cells(doc):
            if cell_text(row[0]).strip().startswith(label):
                seen += 1
                if seen == want:
                    return row
        return None

    # New rows first: copy the matched row (keeping its formatting) and fill
    # the copy, so a 7-stage schedule fits a template drawn with 5 stages.
    for spec, new_rows in (add_rows or {}).items():
        anchor = find_row(spec)
        if anchor is None:
            unmatched.append(f"add_row: {spec}")
            continue
        tr = anchor[0]._tc.getparent()
        for text in new_rows:
            copy = deepcopy(tr)
            tr.addnext(copy)
            tr = copy
            new_cells = []
            for tc in copy.findall(qn("w:tc")):
                new_cells.append(_Cell(tc, anchor[0]._parent))
            for cell, val in zip(new_cells, str(text).split("|")):
                set_cell_text(cell, val)

    for spec in delete_rows or []:
        row = find_row(spec)
        if row is None:
            unmatched.append(f"delete_row: {spec}")
            continue
        tr = row[0]._tc.getparent()
        tr.getparent().remove(tr)

    # Whole cells next, so their instruction text is gone before other passes.
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

    for option in ticks or []:
        if not replace_in_document(doc, lambda _m: "☒ " + option, re.compile("☐ " + re.escape(option))):
            unmatched.append(f"tick: {option}")

    def placeholder(token: str) -> str | None:
        if token in LEAVE_FOR_USER:
            return None
        val = values.get(token[1:-1])
        if val is not None:
            filled.add(token)
        return val

    replace_in_document(doc, placeholder)
    doc.save(out)

    # Bracketed prompts for a person ("[SELECT: ...]", "[Describe ...]",
    # "[VAR_NUMBER or N/A]"): anything in brackets with a lower-case letter.
    instructions = set()
    for p in iter_paragraphs(doc):
        for m in re.finditer(r"\[[^\[\]]*[a-z][^\[\]]*\]?", p.text):
            instructions.add(m.group(0)[:60])
    return {"filled": sorted(filled), "remaining": sorted(find_placeholders(doc)),
            "instructions_left": sorted(instructions), "unmatched": unmatched}


def fill_xlsx(src: Path, out: Path, values: dict[str, str], cells: dict[str, str]) -> dict:
    import openpyxl

    wb = openpyxl.load_workbook(src)
    filled, unmatched = [], []
    # Input cells by address ("Claims!B6": "66136.36"). Formula cells are refused.
    for address, raw in cells.items():
        sheet, _, ref = address.rpartition("!")
        if sheet not in wb.sheetnames:
            unmatched.append(f"cell: {address} (no sheet {sheet!r})")
            continue
        cell = wb[sheet][ref]
        if isinstance(cell.value, str) and cell.value.startswith("="):
            unmatched.append(f"cell: {address} is a formula, not an input")
            continue
        text = str(raw).strip()
        number = text.replace(",", "").replace("$", "")
        if text.endswith("%"):
            cell.value = float(number[:-1]) / 100
        else:
            try:
                cell.value = float(number) if number else None
            except ValueError:
                cell.value = text
        filled.append(address)
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
            elif field in PERCENT_FIELDS:
                val = float(val.replace("%", "")) / 100
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

    spec = yaml.load(args.spec.read_text(), Loader=yaml.BaseLoader) if args.spec else {}
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
        add_rows = {str(k): [str(x) for x in (v if isinstance(v, list) else [v])]
                    for k, v in (spec.get("add_row") or {}).items()}
        delete_rows = [str(x) for x in (spec.get("delete_row") or [])]
        ticks = [str(x) for x in (spec.get("tick") or [])]
        report = fill_docx(args.template, args.out, values, replaces, cells, rows, add_rows, delete_rows, ticks)
    elif suffix == ".xlsx":
        report = fill_xlsx(args.template, args.out, values, cells)
    else:
        raise SystemExit(f"Can't fill {suffix} files. PDFs in templates/pdf are reference checklists.")
    report["out"] = str(args.out)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
