"""Projects: the register of jobs, their folders and tags, and the inbox.

Usage:
    python tools/projects.py new     projects.yaml --job SB-2027-014 --name "Banksia St extension" --tags banksia,citizen
    python tools/projects.py list    projects.yaml
    python tools/projects.py tag     projects.yaml SB-2027-014 --add "42 Banksia St" --remove old_tag
    python tools/projects.py inbox   projects.yaml                      # what's waiting, and which project it looks like
    python tools/projects.py match   projects.yaml --text "Delivery to 42 Banksia St, Merewether"
    python tools/projects.py add     projects.yaml SB-2027-014 --entry bill.json --file inbox/invoice.pdf [--yes]
    python tools/projects.py pay     projects.yaml SB-2027-014 --number HTS-56120 --date 30/10/2026 --amount 42240 [--file ...] [--yes]
    python tools/projects.py file    projects.yaml SB-2027-014 --file inbox/docket.jpg --label "Delivery docket" [--yes]

The register (projects.yaml, see examples/projects_example.yaml) lists every
project with its job number, name, folder, tags and status. `new` makes the
folder:

    SB-2027-014_Banksia_St_extension/
        project.yaml   ledger.yaml   timesheets.csv
        inbox/         drop anything for this job here
        processed/     the brain files what it has read here, renamed
        out/           documents the skills generate

There is also a shared inbox/ next to the register. A file there belongs to
a project if it sits in a subfolder named after the job number or a tag
(inbox/banksia/), if its name contains them, or if what's in it does (the
skill reads it and runs `match`).

`add` and `pay` take what was read off an invoice or a payment screenshot,
check it (arithmetic and GST through the sanctioned maths, ABN checksum,
tax invoice rules, duplicates across every project) and only write when
given --yes: the entry goes into the project's ledger and the source file
moves to processed/ with a clear name, linked from the entry.
"""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import re
import shutil
import sys
from datetime import date, datetime, timedelta
from decimal import Decimal
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import finance  # noqa: E402

_spec = importlib.util.spec_from_file_location("builder_maths", ROOT / "brain/references/computations/builder_maths.py")
builder_maths = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(builder_maths)
maths = finance.maths

INBOX_EXTS = {".pdf", ".png", ".jpg", ".jpeg", ".heic", ".webp", ".gif", ".tif", ".tiff", ".docx", ".xlsx", ".csv", ".txt", ".eml"}
PREFIX = {"bill": "BILL", "supplier_credit": "CREDIT", "invoice": "INV", "credit_note": "CN"}
CENT5 = Decimal("0.05")


# ------------------------------------------------------------------ register

def slug(text: str) -> str:
    return re.sub(r"_+", "_", re.sub(r"[^A-Za-z0-9-]+", "_", text)).strip("_")


def load_register(path: Path) -> dict:
    data = yaml.safe_load(path.read_text()) if path.exists() else None
    data = data or {}
    data.setdefault("projects", data.pop("jobs", None) or [])
    return data


def save_register(path: Path, data: dict) -> None:
    head = []
    if path.exists():
        for line in path.read_text().splitlines():
            if line.startswith("#") or not line.strip():
                head.append(line)
            else:
                break
    body = yaml.safe_dump(data, sort_keys=False, allow_unicode=True, width=120)
    path.write_text("\n".join(head + [body]).rstrip() + "\n")


def project_entry(reg: dict, code: str) -> dict:
    for p in reg["projects"]:
        if str(p.get("job")) == code:
            return p
    raise SystemExit(f"No project {code!r} in the register. Run: python tools/projects.py list <register>")


def folder_of(reg_path: Path, p: dict) -> Path | None:
    return (reg_path.parent / p["folder"]) if p.get("folder") else None


def ledger_path(reg_path: Path, p: dict) -> Path:
    if p.get("ledger"):
        return reg_path.parent / p["ledger"]
    f = folder_of(reg_path, p)
    if not f:
        raise SystemExit(f"{p.get('job')}: no folder or ledger in the register")
    return f / "ledger.yaml"


def new(reg_path: Path, code: str, name: str, tags: list[str], **details) -> dict:
    reg = load_register(reg_path)
    if any(str(p.get("job")) == code for p in reg["projects"]):
        raise SystemExit(f"{code} is already in the register")
    folder = reg_path.parent / slug(f"{code}_{name}")
    for sub in ("inbox", "processed", "out"):
        (folder / sub).mkdir(parents=True, exist_ok=True)
    project = {
        "business": {k: "" for k in ("business_name", "abn", "licence_number", "business_address", "business_address_line_2",
                                     "phone", "email", "account_name", "bsb", "account_number")},
        "project": {"project_name": name, "project_address": details.get("address", ""), "state": details.get("state", ""),
                    "trade": details.get("trade", "builder"), "project_type": details.get("project_type", ""),
                    "ncc_edition": "2025", "start_date": details.get("start_date", ""), "end_date": ""},
        "client": {"client_name": details.get("client", ""), "client_address": "", "client_phone": "", "client_email": ""},
        "contract": {"contract_number": code, "contract_sum": "", "contract_sum_ex_gst": "", "retention_pct": 0},
    }
    if not (folder / "project.yaml").exists():
        (folder / "project.yaml").write_text("# Project file. Every key fills the placeholder of the same name in upper case.\n"
                                              + yaml.safe_dump(project, sort_keys=False))
    if not (folder / "ledger.yaml").exists():
        (folder / "ledger.yaml").write_text(f"# Job ledger for {code}. Amounts ex GST. See tools/finance.py.\n"
                                             + yaml.safe_dump({"job": code, "transactions": [], "payments": []}, sort_keys=False))
    if not (folder / "timesheets.csv").exists():
        (folder / "timesheets.csv").write_text("date,worker,role,hours,rate_ex_gst\n")
    entry = {"job": code, "name": name, "folder": folder.relative_to(reg_path.parent).as_posix(),
             "tags": sorted({t.strip() for t in tags if t.strip()}), "status": "active"}
    for k in ("project_type", "state", "start_date"):
        if details.get(k):
            entry[k] = details[k]
    reg["projects"].append(entry)
    (reg_path.parent / "inbox").mkdir(exist_ok=True)
    save_register(reg_path, reg)
    return {"created": str(folder), "entry": entry}


def tag(reg_path: Path, code: str, add: list[str], remove: list[str]) -> dict:
    reg = load_register(reg_path)
    p = project_entry(reg, code)
    tags = set(p.get("tags") or [])
    tags |= {t.strip() for t in add if t.strip()}
    tags -= {t.strip() for t in remove}
    p["tags"] = sorted(tags)
    save_register(reg_path, reg)
    return {"job": code, "tags": p["tags"]}


def keywords(reg_path: Path, p: dict) -> list[tuple[str, int, str]]:
    """(phrase, weight, why) for matching files and text to a project."""
    out = [(str(p["job"]), 100, "job number")]
    out += [(str(t), 30, "tag") for t in p.get("tags") or []]
    out += [(str(a), 30, "alias") for a in p.get("aliases") or []]
    if p.get("name"):
        out.append((p["name"], 25, "project name"))
    f = folder_of(reg_path, p)
    proj = (f / "project.yaml") if f else (reg_path.parent / p["project"] if p.get("project") else None)
    if proj and proj.exists():
        flat = {}
        for section in (yaml.load(proj.read_text(), Loader=yaml.BaseLoader) or {}).values():
            if isinstance(section, dict):
                flat.update(section)
        addr = flat.get("project_address", "")
        if addr:
            out.append((addr.split(",")[0], 40, "site address"))
        if flat.get("client_name"):
            out.append((flat["client_name"], 20, "client"))
    return [(k, w, why) for k, w, why in out if k and len(k) >= 3]


def norm(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def match(reg_path: Path, text: str) -> list[dict]:
    reg = load_register(reg_path)
    hay = " " + norm(text) + " "
    scores = []
    for p in reg["projects"]:
        score, why = 0, []
        for phrase, weight, reason in keywords(reg_path, p):
            if " " + norm(phrase) + " " in hay:
                score += weight
                why.append(f"{reason}: {phrase}")
        if score:
            scores.append({"job": p["job"], "name": p.get("name", ""), "score": score, "because": why,
                           "status": p.get("status", "active")})
    return sorted(scores, key=lambda s: (-s["score"], s["status"] != "active"))


# ------------------------------------------------------------------ inbox

def guess_kind(name: str) -> str:
    n = name.lower()
    for words, kind in ((("remit", "payment", "receipt", "transfer", "paid"), "payment record"),
                        (("credit",), "credit note"), (("invoice", "inv", "bill", "tax"), "invoice or bill"),
                        (("claim",), "payment claim"), (("docket", "delivery", "dn"), "delivery docket"),
                        (("timesheet", "hours"), "timesheet"), (("quote", "quotation"), "quote")):
        if any(re.search(rf"(^|[^a-z]){w}([^a-z]|$)", n) for w in words):
            return kind
    if Path(n).suffix in (".jpg", ".jpeg", ".heic", ".png") and not re.search(r"[a-z]{4,}", Path(n).stem.replace("img", "")):
        return "photo"
    return "unknown"


def pdf_info(path: Path) -> dict:
    try:
        import pdfplumber  # optional: Claude can also read the PDF directly
    except ImportError:
        return {}
    try:
        with pdfplumber.open(path) as pdf:
            text = "\n".join((pg.extract_text() or "") for pg in pdf.pages[:3])
            return {"pages": len(pdf.pages), "has_text": bool(text.strip()), "text": text[:2000]}
    except Exception as e:  # a damaged or encrypted PDF: let the skill look at it
        return {"pdf_error": str(e)[:200]}


def inbox(reg_path: Path) -> list[dict]:
    reg = load_register(reg_path)
    items = []
    places = [(reg_path.parent / "inbox", None)]
    places += [(folder_of(reg_path, p) / "inbox", p["job"]) for p in reg["projects"] if folder_of(reg_path, p)]
    for place, owner in places:
        if not place.is_dir():
            continue
        for f in sorted(place.rglob("*")):
            if not f.is_file() or f.name.startswith((".", "~$")) or f.suffix.lower() not in INBOX_EXTS:
                continue
            rel = f.relative_to(place)
            if owner:
                suggestion = [{"job": owner, "score": 1000, "because": ["in the project's own inbox"]}]
            else:
                suggestion = match(reg_path, " ".join(rel.parts[:-1]) + " " + f.stem.replace("_", " "))
            item = {"file": str(f.relative_to(reg_path.parent)), "kind": guess_kind(f.name), "size_kb": round(f.stat().st_size / 1024, 1),
                    "received": datetime.fromtimestamp(f.stat().st_mtime).strftime("%d/%m/%Y"),
                    "project": suggestion[0]["job"] if suggestion and (owner or len(suggestion) == 1 or suggestion[0]["score"] > suggestion[1]["score"]) else None,
                    "candidates": suggestion[:3]}
            if f.suffix.lower() == ".pdf":
                item.update(pdf_info(f))
                if not item["project"] and item.get("text"):
                    by_text = match(reg_path, item["text"])
                    if by_text and (len(by_text) == 1 or by_text[0]["score"] > by_text[1]["score"]):
                        item["project"] = by_text[0]["job"]
                    item["candidates"] = [{**c, "because": c["because"] + ["(from the document's text)"]} for c in by_text[:3]]
            items.append(item)
    return items


# ------------------------------------------------------------------ checks

def all_ledgers(reg_path: Path) -> list[tuple[str, dict]]:
    reg = load_register(reg_path)
    out = []
    for p in reg["projects"]:
        lp = ledger_path(reg_path, p)
        if lp.exists():
            out.append((str(p["job"]), yaml.safe_load(lp.read_text()) or {}))
    return out


def to_ledger_entry(raw: dict) -> dict:
    """The extraction as a ledger transaction: lines ex GST (an inc-GST line
    is converted with the sanctioned ex_gst computation)."""
    lines = []
    for line in raw.get("lines") or []:
        l = {k: v for k, v in line.items() if k not in ("amount_inc", "amount_inc_gst")}
        inc = line.get("amount_inc", line.get("amount_inc_gst"))
        if "amount" not in line and inc is not None:
            if line.get("tax", "gst") in maths.GST_CODES:
                l["amount"] = float(builder_maths.ex_gst(Decimal(str(inc)))["result"]["amount_ex_gst"].replace(",", ""))
            else:
                l["amount"] = float(Decimal(str(inc)))
        l.setdefault("tax", "gst")
        lines.append(l)
    entry = {"type": raw.get("type", "bill"), "number": str(raw.get("number", "")).strip(), "date": raw.get("date", ""),
             "due": raw.get("due") or raw.get("date", ""), "reference": raw.get("reference", ""),
             "contact": {k: v for k, v in (raw.get("contact") or {}).items() if v}, "lines": lines}
    if raw.get("tpar") is not None:
        entry["tpar"] = bool(raw["tpar"])
    return {k: v for k, v in entry.items() if v not in ("", None, {})}


def check_entry(reg_path: Path, code: str, raw: dict, accounts: dict) -> dict:
    entry = to_ledger_entry(raw)
    errors, warnings = [], []
    base = finance.check({"transactions": [entry]}, accounts)
    errors += base["errors"]
    warnings += base["warnings"]
    for f in ("number", "date"):
        if not entry.get(f):
            errors.append(f"{f} is missing: read it off the document, or ask")
    if errors:
        return {"ok": False, "entry": entry, "errors": errors, "warnings": warnings}
    n = finance.normalise({"transactions": [entry]}, accounts)[0]
    lines = maths._lines(n)
    ex = sum((a for a, _, _ in lines), Decimal("0"))
    gst = sum((g for _, g, _ in lines), Decimal("0"))
    total = ex + gst
    stated = raw.get("stated") or {}
    if stated.get("total_inc") is not None and abs(Decimal(str(stated["total_inc"])) - total) > CENT5:
        errors.append(f"lines add up to ${total:,.2f} inc GST but the document says ${Decimal(str(stated['total_inc'])):,.2f}: "
                      "re-read the lines (a missed line, freight, or a discount)")
    if stated.get("gst") is not None and abs(Decimal(str(stated["gst"])) - gst) > CENT5:
        warnings.append(f"GST on the document is ${Decimal(str(stated['gst'])):,.2f}, but 10% of the taxable lines is ${gst:,.2f}: "
                        "check which lines are GST-free")
    if stated.get("subtotal_ex") is not None and abs(Decimal(str(stated["subtotal_ex"])) - ex) > CENT5:
        warnings.append(f"subtotal on the document is ${Decimal(str(stated['subtotal_ex'])):,.2f}, the lines make ${ex:,.2f}")
    purchase = entry["type"] in ("bill", "supplier_credit")
    if purchase and total >= Decimal("82.50") and raw.get("is_tax_invoice") is False:
        warnings.append("over $82.50 and not marked as a tax invoice: you can't claim the GST without one. Ask the supplier for a tax invoice")
    if purchase and total >= Decimal("1000") and raw.get("buyer_named") is False:
        warnings.append("$1,000 or more and your business isn't named on it: a tax invoice that size must show the buyer's identity or ABN")
    if purchase and not entry.get("contact", {}).get("abn"):
        warnings.append("no ABN on the invoice: check ABN Lookup before paying; without an ABN you may need to withhold 47%")
    when = datetime.strptime(entry["date"], "%d/%m/%Y").date()
    if when > date.today() + timedelta(days=1):
        warnings.append(f"dated in the future ({entry['date']}): check the date")
    if when < date.today() - timedelta(days=548):
        warnings.append(f"more than 18 months old ({entry['date']}): check the date and whether it's already in your books")
    name = norm(entry.get("contact", {}).get("name", ""))
    for job, ledger in all_ledgers(reg_path):
        for t in ledger.get("transactions") or []:
            same_contact = norm((t.get("contact") or {}).get("name", "")) == name
            if same_contact and str(t.get("number")) == entry["number"] and t.get("type", "bill") == entry["type"]:
                errors.append(f"already in {job}'s ledger: {t['number']} from {t['contact']['name']} dated {t['date']}")
            elif same_contact and t.get("type") == entry["type"]:
                try:
                    other = finance.normalise({"transactions": [t]}, accounts)[0]
                    other_total = maths._total(other)
                    gap = abs((datetime.strptime(str(t["date"]), "%d/%m/%Y").date() - when).days)
                except (KeyError, ValueError):
                    continue
                if abs(other_total - total) <= CENT5 and gap <= 7:
                    warnings.append(f"possible duplicate: {t['number']} in {job} is the same amount from the same supplier {gap} days apart")
    summary = {"ex_gst": f"{ex:.2f}", "gst": f"{gst:.2f}", "inc_gst": f"{total:.2f}"}
    return {"ok": not errors, "job": code, "entry": entry, "computed": summary, "errors": errors, "warnings": warnings}


# ------------------------------------------------------------------ writing

def write_ledger(path: Path, ledger: dict) -> None:
    head = []
    if path.exists():
        for line in path.read_text().splitlines():
            if line.startswith("#") or not line.strip():
                head.append(line)
            else:
                break
    path.write_text("\n".join(head + [yaml.safe_dump(ledger, sort_keys=False, allow_unicode=True, width=120)]).rstrip() + "\n")


def file_source(reg_path: Path, p: dict, src: Path, name: str) -> str:
    folder = folder_of(reg_path, p)
    dest_dir = (folder / "processed") if folder else (reg_path.parent / "processed" / str(p["job"]))
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / (slug(name) + src.suffix.lower())
    i = 2
    while dest.exists():
        dest = dest_dir / f"{slug(name)}_{i}{src.suffix.lower()}"
        i += 1
    shutil.move(str(src), dest)
    base = folder if folder else reg_path.parent
    return dest.relative_to(base).as_posix()


def accounts_for(reg_path: Path, reg: dict) -> dict:
    return yaml.safe_load((reg_path.parent / reg["accounts"]).read_text()) if reg.get("accounts") else {}


def add(reg_path: Path, code: str, raw: dict, src: Path | None, yes: bool) -> dict:
    reg = load_register(reg_path)
    p = project_entry(reg, code)
    report = check_entry(reg_path, code, raw, accounts_for(reg_path, reg))
    if not report["ok"] or not yes:
        report["written"] = False
        return report
    entry = report["entry"]
    if src:
        who = entry.get("contact", {}).get("name", "unknown")
        entry["source"] = file_source(reg_path, p, src, f"{PREFIX.get(entry['type'], 'DOC')}_{who}_{entry['number']}")
    lp = ledger_path(reg_path, p)
    ledger = yaml.safe_load(lp.read_text()) if lp.exists() else {"job": code}
    ledger = ledger or {"job": code}
    ledger.setdefault("transactions", []).append(entry)
    write_ledger(lp, ledger)
    report["written"] = True
    report["ledger"] = str(lp)
    return report


def pay(reg_path: Path, code: str, number: str, when: str, amount: str, contact: str | None, src: Path | None, yes: bool) -> dict:
    reg = load_register(reg_path)
    p = project_entry(reg, code)
    accounts = accounts_for(reg_path, reg)
    lp = ledger_path(reg_path, p)
    ledger = yaml.safe_load(lp.read_text()) or {}
    errors, warnings = [], []
    try:
        datetime.strptime(when, "%d/%m/%Y")
    except ValueError:
        errors.append(f"date must be DD/MM/YYYY, got {when!r}")
    found = [t for t in ledger.get("transactions") or [] if str(t.get("number")) == number
             and (not contact or norm((t.get("contact") or {}).get("name", "")) == norm(contact))]
    if not found:
        errors.append(f"no transaction {number} in {code}'s ledger" + (f" from {contact}" if contact else "") + ": add the invoice or bill first")
    elif len(found) > 1:
        errors.append(f"{number} matches more than one transaction: give --contact")
    outstanding = None
    if not errors:
        n = finance.normalise({"transactions": found, "payments": ledger.get("payments") or []}, accounts)[0]
        total = maths._total(n)
        paid = sum((Decimal(x["amount"]) for x in n["payments"]), Decimal("0"))
        outstanding = total - paid
        if Decimal(str(amount)) > outstanding + CENT5:
            errors.append(f"${Decimal(str(amount)):,.2f} is more than the ${outstanding:,.2f} still owing on {number}")
        elif abs(Decimal(str(amount)) - outstanding) > CENT5:
            warnings.append(f"part payment: ${outstanding - Decimal(str(amount)):,.2f} will still be owing on {number}")
    record = {"number": number, "date": when, "amount": float(Decimal(str(amount)))}
    if contact:
        record["contact"] = contact
    report = {"ok": not errors, "job": code, "payment": record,
              "outstanding_before": f"{outstanding:.2f}" if outstanding is not None else "", "errors": errors, "warnings": warnings}
    if errors or not yes:
        report["written"] = False
        return report
    if src:
        record["source"] = file_source(reg_path, p, src, f"PAY_{number}_{when.replace('/', '-')}")
    ledger.setdefault("payments", []).append(record)
    write_ledger(lp, ledger)
    report["written"] = True
    return report


def file_doc(reg_path: Path, code: str, src: Path, label: str, yes: bool) -> dict:
    reg = load_register(reg_path)
    p = project_entry(reg, code)
    if not yes:
        return {"job": code, "file": str(src), "label": label, "written": False}
    stamp = date.today().strftime("%Y-%m-%d")
    return {"job": code, "label": label, "written": True,
            "filed_as": file_source(reg_path, p, src, f"{label}_{stamp}_{src.stem}")}


def list_projects(reg_path: Path) -> list[dict]:
    reg = load_register(reg_path)
    waiting = {}
    for item in inbox(reg_path):
        waiting[item["project"] or "unassigned"] = waiting.get(item["project"] or "unassigned", 0) + 1
    rows = [{"job": p["job"], "name": p.get("name", ""), "status": p.get("status", "active"), "tags": p.get("tags") or [],
             "folder": p.get("folder", ""), "inbox": waiting.get(p["job"], 0)} for p in reg["projects"]]
    if waiting.get("unassigned"):
        rows.append({"job": "(unassigned)", "name": "shared inbox, project not yet known", "inbox": waiting["unassigned"]})
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("new"); p.add_argument("register", type=Path); p.add_argument("--job", required=True)
    p.add_argument("--name", required=True); p.add_argument("--tags", default="")
    for k in ("address", "client", "state", "project_type", "start_date", "trade"):
        p.add_argument("--" + k.replace("_", "-"), dest=k)
    p = sub.add_parser("list"); p.add_argument("register", type=Path)
    p = sub.add_parser("tag"); p.add_argument("register", type=Path); p.add_argument("job")
    p.add_argument("--add", default=""); p.add_argument("--remove", default="")
    p = sub.add_parser("inbox"); p.add_argument("register", type=Path)
    p = sub.add_parser("match"); p.add_argument("register", type=Path); p.add_argument("--text", required=True)
    p = sub.add_parser("add"); p.add_argument("register", type=Path); p.add_argument("job")
    p.add_argument("--entry", type=Path, required=True, help="JSON of what was read off the document")
    p.add_argument("--file", type=Path); p.add_argument("--yes", action="store_true")
    p = sub.add_parser("pay"); p.add_argument("register", type=Path); p.add_argument("job")
    p.add_argument("--number", required=True); p.add_argument("--date", required=True); p.add_argument("--amount", required=True)
    p.add_argument("--contact"); p.add_argument("--file", type=Path); p.add_argument("--yes", action="store_true")
    p = sub.add_parser("file"); p.add_argument("register", type=Path); p.add_argument("job")
    p.add_argument("--file", type=Path, required=True); p.add_argument("--label", required=True); p.add_argument("--yes", action="store_true")
    a = parser.parse_args()

    if a.cmd == "new":
        details = {k: getattr(a, k) for k in ("address", "client", "state", "project_type", "start_date", "trade") if getattr(a, k)}
        out = new(a.register, a.job, a.name, a.tags.split(","), **details)
    elif a.cmd == "list":
        out = list_projects(a.register)
    elif a.cmd == "tag":
        out = tag(a.register, a.job, a.add.split(","), a.remove.split(",") if a.remove else [])
    elif a.cmd == "inbox":
        out = inbox(a.register)
    elif a.cmd == "match":
        out = match(a.register, a.text)
    elif a.cmd == "add":
        out = add(a.register, a.job, json.loads(a.entry.read_text()), a.file, a.yes)
    elif a.cmd == "pay":
        out = pay(a.register, a.job, a.number, a.date, a.amount, a.contact, a.file, a.yes)
    else:
        out = file_doc(a.register, a.job, a.file, a.label, a.yes)
    print(json.dumps(out, indent=2, default=str))
    if isinstance(out, dict) and out.get("ok") is False:
        sys.exit(1)


if __name__ == "__main__":
    main()
