"""Check first-run setup, the practice job, the cards and the home page.

Usage:
    python tools/test_start.py
"""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
failures = 0


def run(tool: str, *args) -> tuple[int, dict]:
    p = subprocess.run([sys.executable, str(ROOT / "tools" / tool), *map(str, args)], capture_output=True, text=True)
    try:
        return p.returncode, json.loads(p.stdout)
    except json.JSONDecodeError:
        return p.returncode, {"stderr": p.stderr}


def expect(name: str, got, want) -> None:
    global failures
    if got == want:
        print(f"OK   {name}")
    else:
        failures += 1
        print(f"FAIL {name}: got {got!r}, want {want!r}")


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        ws = Path(tmp) / "Jobs"
        _, r = run("start.py", "status", ws)
        expect("nothing set up yet", (r["profile"], r["projects_register"]), (False, False))
        _, r = run("start.py", "setup", ws, "--trade", "sparky", "--state", "qld", "--business-name", "Bright Sparks",
                   "--abn", "95 471 173 493", "--software", "myob")
        expect("setup makes the folder", sorted(r["created"]), ["accounts.yaml", "inbox/", "projects.yaml"])
        prof = yaml.safe_load((ws / "profile.yaml").read_text())
        expect("trade alias and state normalised", (prof["settings"]["trade"], prof["settings"]["state"]), ("electrician", "QLD"))
        expect("accounts mapping set to their software", "software: myob" in (ws / "accounts.yaml").read_text(), True)
        expect("missing details listed", r["missing_profile_fields"], ["licence_number", "phone", "email"])
        _, r = run("start.py", "setup", ws, "--phone", "0400 111 222")
        prof = yaml.safe_load((ws / "profile.yaml").read_text())
        expect("running again only adds", (r["updated"], r["created"], prof["business"]["business_name"]), (["phone"], [], "Bright Sparks"))

        _, r = run("start.py", "cards", ws)
        skills = [c["skill"] for c in r["cards"]]
        expect("electrician cards: no contracts or handover", ("contracts" in skills, "handover" in skills, skills[0]), (False, False, "projects"))
        expect("electrician code questions", r["cards"][-1]["say"][0], "Where do smoke alarms have to go in a house?")
        _, r = run("start.py", "cards", ws, "--trade", "builder")
        expect("builder sees every card", len(r["cards"]), 13)

        _, r = run("projects.py", "new", ws / "projects.yaml", "--job", "BS-001", "--name", "Smith house rewire")
        proj = yaml.safe_load((ws / "BS-001_Smith_house_rewire" / "project.yaml").read_text())
        expect("new job takes the profile's details", (proj["business"]["business_name"], proj["business"]["phone"], proj["project"]["state"]),
               ("Bright Sparks", "0400 111 222", "QLD"))

        _, r = run("start.py", "demo", ws)
        expect("demo kept apart, sample paperwork waiting", (r["inbox"], (ws / "demo" / "projects.yaml").exists()),
               (["Coastal_Concrete_Pumping_invoice.pdf", "IMG_4417.png"], True))
        real = yaml.safe_load((ws / "projects.yaml").read_text())
        expect("real register untouched by the demo", [p["job"] for p in real["projects"]], ["BS-001"])
        _, items = run("projects.py", "inbox", ws / "demo" / "projects.yaml")
        expect("demo invoice matched to the practice job", {Path(i["file"]).name: i["project"] for i in items}["Coastal_Concrete_Pumping_invoice.pdf"], "DEMO-001")

        code, r = run("home.py", ws / "projects.yaml", "--as-at", "31/10/2026")
        page = (ws / "home.html").read_text()
        expect("home page built", (code, (ws / "home.html").exists()), (0, True))
        expect("home page has its data", "/*__DATA__*/null" not in page and '"BS-001"' in page and "Bright Sparks" in page, True)
        expect("job without a start date still listed", r["projects"], 1)

        import shutil
        shutil.copytree(ROOT / "examples", Path(tmp) / "ex")
        code, r = run("home.py", Path(tmp) / "ex" / "projects_example.yaml", "--as-at", "31/10/2026")
        data = json.loads((Path(tmp) / "ex" / "home.html").read_text().split("const DATA = ", 1)[1].split(";\n", 1)[0])
        figs = {p["job"]: p["figures"].get("margin_pct") for p in data["projects"]}
        expect("home page shows each job's margin", figs, {"SB-2027-014": "32.6", "SB-2025-031": "12.5", "SB-2026-007": "18.2"})

    import os
    with tempfile.TemporaryDirectory() as tmp:
        empty = Path(tmp) / "Jobs"
        empty.mkdir()
        _, _ = 0, 0
        p = subprocess.run([sys.executable, str(ROOT / "tools" / "start.py"), "brief", str(empty)], capture_output=True, text=True)
        expect("welcome in an empty folder", ("isn't set up yet" in p.stdout, "Run setup once only" in p.stdout), (True, True))
        code_repo = Path(tmp) / "app"
        (code_repo / ".git").mkdir(parents=True)
        p = subprocess.run([sys.executable, str(ROOT / "tools" / "start.py"), "brief", str(code_repo)], capture_output=True, text=True)
        expect("silent in a code project", p.stdout.strip(), "")
        p = subprocess.run([sys.executable, str(ROOT / "tools" / "start.py"), "brief", str(ROOT)], capture_output=True, text=True)
        expect("silent in the brain's own repository", p.stdout.strip(), "")

        ws = Path(tmp) / "Work"
        run("start.py", "setup", ws, "--trade", "carpenter", "--state", "ACT", "--business-name", "Chapman Carpentry")
        run("projects.py", "new", ws / "projects.yaml", "--job", "CC-001", "--name", "Chapman veranda", "--start-date", "01/09/2026")
        ledger = ws / "CC-001_Chapman_veranda" / "ledger.yaml"
        ledger.write_text("job: CC-001\ntransactions:\n- {type: invoice, number: INV-1, date: 01/09/2026, due: 08/09/2026, "
                          "contact: {name: Bill Burr}, lines: [{description: Deposit, amount: 1000, account: contract_income, tax: gst}]}\npayments: []\n")
        (ws / "inbox" / "receipt.jpg").write_bytes(b"x")
        p = subprocess.run([sys.executable, str(ROOT / "tools" / "start.py"), "brief", str(ws)], capture_output=True, text=True)
        expect("briefing names the business and trade", "Chapman Carpentry (carpenter, ACT)" in p.stdout, True)
        expect("briefing flags the overdue invoice with its amount", "invoice INV-1 overdue" in p.stdout and "$1,100.00" in p.stdout, True)
        expect("briefing counts the inbox", "1 file(s) waiting in the inbox" in p.stdout, True)
        env = {k: v for k, v in os.environ.items() if k != "CLAUDE_PLUGIN_DATA"}
        env.update({"CLAUDE_PLUGIN_ROOT": str(ROOT), "CLAUDE_PROJECT_DIR": str(ws)})
        p = subprocess.run([str(ROOT / "hooks" / "session_start.sh")], capture_output=True, text=True, env=env)
        out = json.loads(p.stdout or "{}").get("hookSpecificOutput", {})
        expect("session-start hook prints the briefing as context", (out.get("hookEventName"), "Chapman Carpentry" in out.get("additionalContext", "")),
               ("SessionStart", True))
        env["CLAUDE_PROJECT_DIR"] = str(code_repo)
        p = subprocess.run([str(ROOT / "hooks" / "session_start.sh")], capture_output=True, text=True, env=env)
        expect("session-start hook stays quiet in a code project", p.stdout.strip(), "")

    skills = {d.name for d in (ROOT / "skills").iterdir() if d.is_dir()}
    commands = {}
    for f in sorted((ROOT / "commands").glob("*.md")):
        front = f.read_text().split("---", 2)[1]
        commands[f.stem] = (yaml.safe_load(front) or {}).get("description", "")
    expect("every command has a description", [c for c, d in commands.items() if not d], [])
    expect("no command shares a skill's name", sorted(set(commands) & skills), [])

    print(f"\n{'all start checks passed' if not failures else f'{failures} failed'}")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
