"""First-run setup: the user's profile, their jobs folder, a demo, and what to say.

Usage:
    python tools/start.py status  [folder]                       # what's set up already
    python tools/start.py setup   [folder] --trade electrician --state QLD --business-name "Bright Sparks" --abn "..." ...
    python tools/start.py demo    [folder]                       # a practice job in folder/demo with sample paperwork
    python tools/start.py cards   [folder] [--trade carpenter]   # "things you can say" for the trade

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


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    for name in ("status", "setup", "demo", "cards"):
        s = sub.add_parser(name)
        s.add_argument("folder", nargs="?", type=Path, default=Path("."))
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
    else:
        out = cards(a.folder, a.trade)
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
