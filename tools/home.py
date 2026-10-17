"""Build the home page: one page in the jobs folder showing everything at a glance.

Usage:
    python tools/home.py projects.yaml [--as-at 31/10/2026]

Writes home.html next to the register (open it in any browser, no internet
or server needed). It shows the user's profile, every project with its
position (contract, invoiced, received, outstanding, margin, forecast, time)
and its latest documents, what's waiting in the inbox, and "things you can
say" for their trade, with a copy button on each. It also rebuilds the
dashboard and extracts in out/dashboard/ (tools/dashboard.py), which the
home page links to.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import subprocess
import sys
from datetime import date
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import projects  # noqa: E402
import start  # noqa: E402


def build(reg_path: Path, as_at: str) -> dict:
    ws = reg_path.parent
    out = ws / "out" / "dashboard"
    p = subprocess.run([sys.executable, str(ROOT / "tools" / "dashboard.py"), str(reg_path), "--out", str(out), "--as-at", as_at],
                       capture_output=True, text=True)
    figures, docs, warnings = {}, [], []
    if p.returncode == 0:
        report = json.loads(p.stdout)
        warnings = report.get("warnings", [])
        result = json.loads((out / "receipt.json").read_text())["result"]
        figures = {j["job"]: j for j in result["jobs"]}
        with (out / "documents.csv").open(newline="") as f:
            for d in csv.DictReader(f):
                if not d.get("job"):
                    continue
                link = d["link"]
                if not link.startswith(("http://", "https://")):
                    link = os.path.normpath(os.path.join("out/dashboard", link)).replace(os.sep, "/")
                docs.append({**d, "link": link})
    else:
        warnings = ["The dashboard couldn't be built: " + (p.stderr.strip().splitlines() or ["unknown error"])[-1]]

    reg = projects.load_register(reg_path)
    waiting = projects.inbox(reg_path)
    rows = []
    for e in reg["projects"]:
        code = str(e.get("job"))
        f = figures.get(code, {})
        rows.append({"job": code, "name": e.get("name") or f.get("name", ""), "status": e.get("status", f.get("status", "active")),
                     "tags": e.get("tags") or [], "folder": e.get("folder", ""), "figures": f,
                     "documents": sorted([d for d in docs if d["job"] == code],
                                         key=lambda d: d["modified"].split("/")[::-1], reverse=True),
                     "inbox": [i for i in waiting if i["project"] == code]})
    prof = start.read(ws / "profile.yaml")
    st = start.status(ws)
    cards = start.cards(ws, None)
    return {"as_at": as_at, "profile": prof, "missing": st["missing_profile_fields"], "projects": rows,
            "unassigned": [i for i in waiting if not i["project"]], "cards": cards,
            "dashboard": "out/dashboard/dashboard.html" if (out / "dashboard.html").exists() else "",
            "extracts": "out/dashboard/" if (out / "jobs.csv").exists() else "", "warnings": warnings}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("register", type=Path)
    parser.add_argument("--as-at", default=date.today().strftime("%d/%m/%Y"))
    a = parser.parse_args()
    data = build(a.register.resolve(), a.as_at)
    page = a.register.resolve().parent / "home.html"
    template = (ROOT / "tools" / "home_template.html").read_text()
    page.write_text(template.replace("/*__DATA__*/null", json.dumps(data, default=str).replace("</", "<\\/")))
    print(json.dumps({"home": str(page), "projects": len(data["projects"]),
                      "inbox_waiting": sum(len(p["inbox"]) for p in data["projects"]) + len(data["unassigned"]),
                      "missing_profile_fields": data["missing"], "warnings": data["warnings"]}, indent=2))


if __name__ == "__main__":
    main()
