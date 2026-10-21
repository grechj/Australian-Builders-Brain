"""Check learning from use: the report spots new and rising products and
catalogue gaps, sharing is only offered when it should be, and the shared
summary carries no prices, jobs, clients, addresses or store names.

Usage:
    python tools/test_usage.py
"""

import csv
import json
import subprocess
import sys
import tempfile
import urllib.parse
from datetime import date
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import usage  # noqa: E402

failures = 0


def expect(name, got, want):
    global failures
    if got == want:
        print(f"OK   {name}")
    else:
        failures += 1
        print(f"FAIL {name}: got {got!r}, want {want!r}")


def write_log(path: Path, rows: list[tuple]) -> None:
    with path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(usage.COLUMNS)
        for d, fam, item, prod, supplier, job in rows:
            w.writerow([d, "used", fam, item, prod, supplier, job, "carpenter", "ACT"])


def main() -> None:
    today = date(2026, 10, 21)
    with tempfile.TemporaryDirectory() as tmp:
        ws = Path(tmp)
        (ws / "profile.yaml").write_text(yaml.safe_dump({"business": {"business_name": "Chapman Carpentry"},
                                                          "settings": {"trade": "carpenter", "state": "ACT"}}))
        log = ws / "materials_log.csv"
        old = [("10/03/2026", "decking_screws", "Decking screws", "Class 4 decking screws 10g x 50mm 500 pack", "Bunnings Fyshwick", "CC-001")] * 6
        new = [("01/10/2026", "decking_screws", "Decking screws", "316 stainless decking screws 10g x 50mm 500 pack", "Bunnings Fyshwick", "CC-007")] * 4
        odd = [("05/10/2026", "decking", "Decking boards", "135x19 spotted gum decking", "Canberra Timber Yard", "CC-007"),
               ("06/10/2026", "", "Hidden deck clips", "Hidden deck clip system 100 pack", "Bunnings Fyshwick", "CC-007")]
        write_log(log, old + new + odd)
        rows = usage.read(log)

        r = usage.report(rows, 90, today)
        expect("new products: first used in the last 90 days", [p["product"] for p in r["new_products"]],
               ["316 stainless decking screws 10g x 50mm 500 pack", "135x19 spotted gum decking", "Hidden deck clip system 100 pack"])
        expect("rising: stainless screws took over from class 4", [(x["product"], x["share_now"], x["share_before"]) for x in r["rising"]][:1],
               [("316 stainless decking screws 10g x 50mm 500 pack", 1.0, 0.0)])
        expect("catalogue gap: an item with no family", r["catalogue_gaps"]["unknown_items"], [{"item": "Hidden deck clips", "uses": 1}])
        expect("catalogue gap: a size the catalogue doesn't list", r["catalogue_gaps"]["sizes_not_listed"], {"decking": ["135x19"]})

        st = usage.status(log, today)
        expect("not offered below 20 entries", (st["offer"], st["new_entries"]), (False, 12))
        write_log(log, (old + new + odd) * 2)
        expect("offered at 20 or more", usage.status(log, today)["offer"], True)

        p = subprocess.run([sys.executable, str(ROOT / "tools/usage.py"), "share", "--log", str(log), "--out", str(ws / "out/usage_share.md")],
                           capture_output=True, text=True, cwd=ws)
        out = json.loads(p.stdout)
        body = (ws / "out/usage_share.md").read_text()
        leaks = [x for x in ("CC-001", "CC-007", "Fyshwick", "Canberra Timber Yard", "Chapman", "$") if x in body]
        expect("summary has no jobs, stores, business names or prices", leaks, [])
        expect("summary keeps trade, state and product counts",
               ("carpenter" in body, "ACT" in body, "316 stainless decking screws 10g x 50mm 500 pack (8)" in body), (True, True, True))
        link = out["issue_link"] or ""
        q = urllib.parse.parse_qs(urllib.parse.urlparse(link).query)
        expect("a ready-to-post GitHub issue link (the user submits it)",
               (link.startswith(usage.REPO_ISSUES), q.get("labels"), "Usage summary: carpenter, ACT" in q.get("title", [""])[0]),
               (True, ["usage-report"], True))
        expect("drafting it counts as asking", usage.status(log, today)["offer"], False)

        subprocess.run([sys.executable, str(ROOT / "tools/usage.py"), "decline", "--never", "--log", str(log)], capture_output=True, cwd=ws)
        prof = yaml.safe_load((ws / "profile.yaml").read_text())
        expect("never means never", (prof["sharing"]["choice"], usage.status(log, today)["offer"]), ("never", False))
        expect("the profile keeps its business details", prof["business"]["business_name"], "Chapman Carpentry")

        # Maintainer side: shared summaries become a brain page.
        rep = ws / "r1.json"
        rep.write_text((ws / "out/usage_share.json").read_text())
        page = usage.ingest([rep, rep])
        expect("ingest lists new and spreading products", "- 316 stainless decking screws 10g x 50mm 500 pack (2)" in page, True)
        parsed = usage.parse_issue(body + "\n\nextra text")
        expect("an issue body parses back to the summary", parsed == json.loads((ws / "out/usage_share.json").read_text()), True)
        expect("a non-summary issue is ignored", usage.parse_issue("Bug: the dashboard is blank"), None)
        bad = ws / "bad.json"
        bad.write_text(json.dumps({"trade": "carpenter", "state": "ACT", "families": {"paint": {"[click me](https://spam.example) <script>": 3, "x": "lots"}}}))
        spam = usage.ingest([bad])
        expect("shared reports can't inject links or markup", ("https://" in spam, "<script>" in spam, "[click me]" in spam), (False, False, False))
        expect("ingest page is a brain concept", page.startswith("---\ntype: Reference"), True)

    # Supplier bills filed through the inbox log their materials lines (not delivery or labour), dated by the bill.
    with tempfile.TemporaryDirectory() as tmp:
        ws = Path(tmp)
        run = lambda *a: subprocess.run([sys.executable, *map(str, a)], capture_output=True, text=True, cwd=ws)
        run(ROOT / "tools/start.py", "setup", ws, "--trade", "carpenter", "--state", "ACT")
        run(ROOT / "tools/projects.py", "new", "projects.yaml", "--job", "CC-001", "--name", "Chapman deck")
        (ws / "bill.json").write_text(json.dumps({"type": "bill", "number": "TY-881", "date": "15/10/2026", "due": "14/11/2026",
            "contact": {"name": "Hunter Timber", "abn": "53 004 085 616"},
            "lines": [{"description": "140x45 H3 treated pine 4.8m", "amount": 400, "account": "materials", "tax": "gst"},
                      {"description": "Delivery", "amount": 50, "account": "materials", "tax": "gst"},
                      {"description": "Carpentry labour", "amount": 900, "account": "subcontractors", "tax": "gst"}],
            "stated": {"subtotal": "1350.00", "gst": "135.00", "total": "1485.00"}, "is_tax_invoice": True, "buyer_named": True}))
        run(ROOT / "tools/projects.py", "add", "projects.yaml", "CC-001", "--entry", "bill.json", "--yes")
        rows = usage.read(ws / "materials_log.csv")
        expect("a filed bill logs its materials, dated by the bill",
               [(r["date"], r["event"], r["family"], r["product"], r["job"], r["trade"]) for r in rows],
               [("15/10/2026", "bought", "framing_timber", "140x45 H3 treated pine 4.8m", "CC-001", "carpenter")])

    print(f"\n{'all usage checks passed' if not failures else f'{failures} failed'}")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
