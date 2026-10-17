"""First-run setup: the user's profile, their jobs folder, a demo, and what to say.

Usage:
    python tools/start.py status  [folder]                       # what's set up already
    python tools/start.py setup   [folder] --trade electrician --state QLD --business-name "Bright Sparks" --abn "..." ...
    python tools/start.py demo    [folder]                       # a practice job in folder/demo with sample paperwork
    python tools/start.py cards   [folder] [--trade carpenter]   # "things you can say" for the trade
    python tools/start.py brief   [folder] [--hook]              # what Claude should know at the start of a session

`setup` writes, in the folder (the current one by default):

    profile.yaml     who you are: business details, trade, state, GST basis, software, rates
    projects.yaml    the register of jobs (the projects skill keeps it)
    accounts.yaml    the account mapping, for Xero, MYOB or QuickBooks (check it with your bookkeeper)
    inbox/           drop invoices, receipts and photos here

It never overwrites: running it again only fills in what's given. New jobs
made with tools/projects.py copy the business details from profile.yaml.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import profile as trade_profile  # noqa: E402

BUSINESS = ["business_name", "abn", "licence_number", "business_address", "business_address_line_2",
            "phone", "email", "website", "account_name", "bsb", "account_number"]
SETTINGS = ["trade", "state", "region", "gst_registered", "gst_basis", "software", "labour_rate_ex_gst", "target_margin_pct"]


def read(path: Path) -> dict:
    return (yaml.safe_load(path.read_text()) or {}) if path.exists() else {}


def status(folder: Path) -> dict:
    prof = read(folder / "profile.yaml")
    reg = read(folder / "projects.yaml")
    biz = prof.get("business") or {}
    missing = [k for k in ("business_name", "abn", "licence_number", "phone", "email") if not biz.get(k)]
    missing += [k for k in ("trade", "state") if not (prof.get("settings") or {}).get(k)]
    projects = reg.get("projects") or reg.get("jobs") or []
    return {"folder": str(folder), "profile": (folder / "profile.yaml").exists(), "missing_profile_fields": missing,
            "projects_register": (folder / "projects.yaml").exists(), "projects": len(projects),
            "accounts_mapping": (folder / "accounts.yaml").exists(), "inbox": (folder / "inbox").is_dir(),
            "demo": (folder / "demo" / "projects.yaml").exists(),
            "home_page": (folder / "home.html").exists()}


def setup(folder: Path, values: dict) -> dict:
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "profile.yaml"
    prof = read(path)
    prof.setdefault("business", {k: "" for k in BUSINESS})
    prof.setdefault("settings", {"trade": "", "state": "", "region": "metro", "gst_registered": True, "gst_basis": "",
                                 "software": "", "labour_rate_ex_gst": "", "target_margin_pct": ""})
    changed = []
    if values.get("trade"):
        values["trade"] = trade_profile.find_trade(values["trade"])
    if values.get("state"):
        values["state"] = trade_profile.find_state(values["state"])
    for k, v in values.items():
        if v in (None, ""):
            continue
        section = "business" if k in BUSINESS else "settings"
        if prof[section].get(k) != v:
            prof[section][k] = v
            changed.append(k)
    path.write_text("# Your profile. New jobs copy these business details; skills use your trade and state.\n"
                    "# Change anything here, or ask: \"update my profile\".\n"
                    + yaml.safe_dump(prof, sort_keys=False, allow_unicode=True))
    created = []
    if not (folder / "accounts.yaml").exists():
        text = (ROOT / "examples" / "accounts_example.yaml").read_text()
        software = prof["settings"].get("software") or "xero"
        (folder / "accounts.yaml").write_text(text.replace("software: xero ", f"software: {software} ", 1))
        created.append("accounts.yaml")
    if not (folder / "projects.yaml").exists():
        (folder / "projects.yaml").write_text("# Your jobs. The projects skill keeps this up to date.\n"
                                              "accounts: accounts.yaml\nprojects: []\n")
        created.append("projects.yaml")
    if not (folder / "inbox").is_dir():
        (folder / "inbox").mkdir()
        created.append("inbox/")
    return {"profile": str(path), "updated": changed, "created": created, **status(folder)}


def demo(folder: Path) -> dict:
    """A practice job in its own register under folder/demo, so the user's real
    jobs are never touched. The sample invoice and bank screenshot wait in its inbox."""
    import projects

    d = folder / "demo"
    d.mkdir(parents=True, exist_ok=True)
    shutil.copy(ROOT / "examples" / "accounts_example.yaml", d / "accounts.yaml")
    reg = d / "projects.yaml"
    if not reg.exists():
        reg.write_text("# Practice jobs. Delete this folder whenever you like.\naccounts: accounts.yaml\nprojects: []\n")
    if not any(p.get("job") == "DEMO-001" for p in projects.load_register(reg)["projects"]):
        projects.new(reg, "DEMO-001", "Banksia St practice job", ["banksia", "practice"], address="42 Banksia St, Merewether NSW 2291",
                     client="Jo and Sam Citizen", state="NSW", start_date="03/08/2026", project_type="extension")
    inbox = d / "inbox"
    inbox.mkdir(exist_ok=True)
    for f in (ROOT / "examples" / "inbox").iterdir():
        if not (inbox / f.name).exists():
            shutil.copy(f, inbox / f.name)
    return {"demo": str(d), "register": str(reg), "inbox": sorted(p.name for p in inbox.iterdir()),
            "try": ["Process my inbox (in the demo folder)", "Do a variation for the practice job: two extra power points, $640",
                    "Show me the dashboard for the practice job"]}


def cards(folder: Path, trade: str | None) -> dict:
    prof = read(folder / "profile.yaml")
    trade = trade or (prof.get("settings") or {}).get("trade") or "builder"
    state = (prof.get("settings") or {}).get("state") or None
    p = trade_profile.resolve_profile(trade, state)
    data = yaml.safe_load((ROOT / "tools" / "start_cards.yaml").read_text())
    order = ["projects", "estimating", "materials", "contracts", "variations", "claims", "notices", "site", "safety",
             "handover", "financials", "accounts", "ncc"]
    skills = set(p["skills"]) | {"projects", "accounts", "ncc"}
    out = []
    for s in order:
        if s not in skills or s not in data["skills"]:
            continue
        card = dict(data["skills"][s], skill=s)
        if s == "ncc":
            card["say"] = data["ncc_by_trade"].get(p["trade"]) or (data["ncc_by_trade"]["builder"] + card["say"][:1])
        out.append(card)
    return {"trade": p["trade"], "trade_title": p["trade_title"], "state": p["state"], "cards": out}


CODE_MARKERS = (".git", "package.json", "pyproject.toml", "Cargo.toml", "go.mod", "pom.xml", "Gemfile", "requirements.txt", "src")
JOBS_WORDS = ("job", "build", "construct", "project", "work", "trade", "reno", "site", "client")


def _looks_like_new_jobs_folder(folder: Path) -> bool:
    """An empty or near-empty folder, or one named like a jobs folder, that isn't a code project."""
    if (folder / ".claude-plugin" / "plugin.json").exists() or any((folder / m).exists() for m in CODE_MARKERS):
        return False
    visible = [p for p in folder.iterdir() if not p.name.startswith(".")] if folder.is_dir() else []
    return len(visible) <= 5 or any(w in folder.name.lower() for w in JOBS_WORDS)


def _money(x) -> str:
    return f"${x:,.2f}"


def brief(folder: Path) -> str:
    """The facts Claude needs at the start of a session, in plain words."""
    folder = folder.resolve()
    st = status(folder)
    if not st["profile"] and not st["projects_register"]:
        if not _looks_like_new_jobs_folder(folder):
            return ""
        examples = ["Start a new job for the Smiths at 14 Ocean St", "Here's a supplier invoice for that job",
                    "What does the building code say about stair heights?"]
        return ("The Australian Builder's Brain plugin is installed and this folder isn't set up yet. "
                "In your first reply, whatever the user asks: welcome them in one line, say the brain can set up this folder as their jobs folder "
                "in a couple of minutes (the start skill), and give three examples of what they can ask, such as: "
                + "; ".join(f'"{e}"' for e in examples) + ". "
                "Ask only one question per message. If this session isn't in a folder the user chose (for example Cowork without a project), "
                "recommend a Cowork project on a real Jobs folder before setting up, as the start skill describes. "
                "If they're asking for something else, help with that first and offer setup after. "
                "Run setup once only: if setup is already under way in this session or another thread, don't start it again.")
    import projects
    import finance
    from datetime import date, datetime, timedelta

    prof = read(folder / "profile.yaml")
    biz = (prof.get("business") or {}).get("business_name") or "the user"
    s = prof.get("settings") or {}
    lines = [f"The Australian Builder's Brain is set up in this folder for {biz} ({s.get('trade') or 'trade not set'}, {s.get('state') or 'state not set'})."]
    today = date.today()
    facts = []
    try:
        reg_path = folder / "projects.yaml"
        reg = projects.load_register(reg_path) if reg_path.exists() else {"projects": []}
        waiting = projects.inbox(reg_path) if reg_path.exists() else []
        if waiting:
            facts.append(f"{len(waiting)} file(s) waiting in the inbox")
        active = [p for p in reg["projects"] if p.get("status", "active") != "complete"]
        for p in active:
            bits = []
            n_in = sum(1 for i in waiting if i["project"] == p.get("job"))
            if n_in:
                bits.append(f"{n_in} in its inbox")
            lp = projects.ledger_path(reg_path, p) if (p.get("folder") or p.get("ledger")) else None
            if lp and lp.exists():
                ledger = yaml.safe_load(lp.read_text()) or {}
                for t, n in zip(ledger.get("transactions") or [], finance.normalise(ledger, {})):
                    owing = finance.maths._total(n) - sum((finance.Decimal(x["amount"]) for x in n["payments"]), finance.Decimal("0"))
                    if owing <= finance.Decimal("0.05") or not t.get("due"):
                        continue
                    due = datetime.strptime(str(t["due"]), "%d/%m/%Y").date()
                    if t["type"] == "invoice" and due < today:
                        bits.append(f"invoice {t['number']} overdue {(today - due).days} days ({_money(owing)} inc GST)")
                    elif t["type"] == "bill" and due <= today + timedelta(days=7):
                        bits.append(f"bill {t['number']} to {(t.get('contact') or {}).get('name', '')} due {t['due']} ({_money(owing)})")
            facts.append(f"{p.get('name') or p.get('job')} ({p.get('job')}): " + ("; ".join(bits) if bits else "nothing urgent"))
        if not active:
            facts.append("no active jobs yet")
    except Exception as e:  # a briefing must never break a session
        facts.append(f"(couldn't read every job: {str(e)[:80]})")
    if st["missing_profile_fields"]:
        facts.append("profile still missing: " + ", ".join(m.replace("_", " ") for m in st["missing_profile_fields"]))
    lines.append("Facts as at today: " + " | ".join(facts) + ".")
    lines.append("Open your first reply with a two to four line briefing from these facts only (most urgent first), then answer what the user asked. "
                 "Mention home.html if they ask what's going on. Don't repeat the briefing later in the session.")
    return " ".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    for name in ("status", "setup", "demo", "cards", "brief"):
        s = sub.add_parser(name)
        s.add_argument("folder", nargs="?", type=Path, default=Path("."))
        if name == "brief":
            s.add_argument("--hook", action="store_true", help="print as SessionStart hook JSON")
        if name in ("setup", "cards"):
            s.add_argument("--trade")
        if name == "setup":
            s.add_argument("--state")
            for k in BUSINESS + [k for k in SETTINGS if k not in ("trade", "state")]:
                s.add_argument("--" + k.replace("_", "-"), dest=k)
    a = parser.parse_args()
    if a.cmd == "status":
        out = status(a.folder)
    elif a.cmd == "setup":
        values = {k: getattr(a, k) for k in BUSINESS + SETTINGS if getattr(a, k, None) not in (None, "")}
        for k in ("gst_registered",):
            if k in values:
                values[k] = str(values[k]).lower() in ("yes", "true", "y", "1")
        out = setup(a.folder, values)
    elif a.cmd == "demo":
        out = demo(a.folder)
    elif a.cmd == "brief":
        text = brief(a.folder)
        if a.hook:
            if text:
                print(json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": text}}))
        else:
            print(text)
        return
    else:
        out = cards(a.folder, a.trade)
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
