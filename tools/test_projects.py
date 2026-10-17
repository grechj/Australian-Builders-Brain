"""Check the project register, tags and inbox from start to finish.

Usage:
    python tools/test_projects.py

In a temporary workspace: make two projects, drop the sample invoice PDF and
bank screenshot into the shared inbox, match the invoice to its project by
the site address in its text, add it (checked, then written), refuse it a
second time, record the payment from the screenshot, refuse an overpayment,
and build the dashboard, which must list the filed documents and link the
bill to its source PDF. The sample invoice is $1,025.00 ex GST + $102.50 GST
= $1,127.50.
"""

import csv
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOL = ROOT / "tools" / "projects.py"
failures = 0


def run(*args, cwd: Path) -> tuple[int, object]:
    p = subprocess.run([sys.executable, str(TOOL), *args], capture_output=True, text=True, cwd=cwd)
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
        ws = Path(tmp)
        shutil.copy(ROOT / "examples" / "accounts_example.yaml", ws / "accounts.yaml")
        (ws / "projects.yaml").write_text("accounts: accounts.yaml\nprojects: []\n")
        code, r = run("new", "projects.yaml", "--job", "SB-2027-014", "--name", "Banksia St extension", "--tags", "banksia,citizen",
                      "--address", "42 Banksia St, Merewether NSW 2291", "--client", "Jo and Sam Citizen",
                      "--start-date", "03/08/2026", "--project-type", "extension", cwd=ws)
        folder = ws / "SB-2027-014_Banksia_St_extension"
        expect("new project folder", sorted(p.name for p in folder.iterdir()),
               ["inbox", "ledger.yaml", "out", "processed", "project.yaml", "timesheets.csv"])
        run("new", "projects.yaml", "--job", "SB-2027-020", "--name", "Ocean St deck", "--tags", "ocean", cwd=ws)
        code, r = run("tag", "projects.yaml", "SB-2027-020", "--add", "Hunter,deck", "--remove", "ocean", cwd=ws)
        expect("tags added and removed", r["tags"], ["Hunter", "deck"])

        for f in (ROOT / "examples" / "inbox").iterdir():
            shutil.copy(f, ws / "inbox" / f.name)
        (ws / "inbox" / "ocean").mkdir()
        (ws / "inbox" / "ocean" / "docket.jpg").write_bytes(b"x")
        (ws / "inbox" / "SB-2027-020_quote.pdf").write_bytes(b"%PDF-1.4 not really")
        _, items = run("inbox", "projects.yaml", cwd=ws)
        by = {Path(i["file"]).name: i for i in items}
        expect("invoice matched by the site address in its text", by["Coastal_Concrete_Pumping_invoice.pdf"]["project"], "SB-2027-014")
        expect("file named with a job number matched", by["SB-2027-020_quote.pdf"]["project"], "SB-2027-020")
        expect("screenshot waits for the skill to read it", by["IMG_4417.png"]["project"], None)
        expect("subfolder named for an old tag is not matched", by["docket.jpg"]["project"], None)

        code, r = run("match", "projects.yaml", "--text", "Delivery to 42 Banksia St Merewether", cwd=ws)
        expect("match by address", r[0]["job"], "SB-2027-014")

        entry = ROOT / "examples" / "inbox_entry_example.json"
        code, r = run("add", "projects.yaml", "SB-2027-014", "--entry", str(entry), "--file", "inbox/Coastal_Concrete_Pumping_invoice.pdf", cwd=ws)
        expect("dry run checks without writing", (code, r["ok"], r["written"], r["computed"]["inc_gst"]), (0, True, False, "1127.50"))
        code, r = run("add", "projects.yaml", "SB-2027-014", "--entry", str(entry), "--file", "inbox/Coastal_Concrete_Pumping_invoice.pdf", "--yes", cwd=ws)
        expect("added and filed", (r["written"], r["entry"]["source"]), (True, "processed/BILL_Coastal_Concrete_Pumping_Pty_Ltd_CCP-2207.pdf"))
        expect("source moved out of the inbox", (ws / "inbox" / "Coastal_Concrete_Pumping_invoice.pdf").exists(), False)
        code, r = run("add", "projects.yaml", "SB-2027-020", "--entry", str(entry), cwd=ws)
        expect("duplicate refused, even in another project", (code, any("already in SB-2027-014" in e for e in r["errors"])), (1, True))

        bad = json.loads(entry.read_text())
        bad.update({"number": "CCP-2299", "stated": {"total_inc": 1200.00}, "buyer_named": False})
        bad["contact"] = {"name": "Coastal Concrete Pumping Pty Ltd"}
        (ws / "bad.json").write_text(json.dumps(bad))
        code, r = run("add", "projects.yaml", "SB-2027-014", "--entry", "bad.json", cwd=ws)
        expect("misread total refused", any("document says $1,200.00" in e for e in r["errors"]), True)
        expect("missing ABN and buyer warned", (any("no ABN" in w for w in r["warnings"]), any("buyer" in w for w in r["warnings"])), (True, True))

        inc = json.loads(entry.read_text())
        inc.update({"number": "CCP-2301", "stated": {"total_inc": 330.00}})
        inc["lines"] = [{"description": "Pump hire (inc GST)", "amount_inc": 330.00, "account": "plant_hire", "tax": "gst"}]
        (ws / "inc.json").write_text(json.dumps(inc))
        code, r = run("add", "projects.yaml", "SB-2027-014", "--entry", "inc.json", cwd=ws)
        expect("GST-inclusive line converted with the ex GST computation", (r["entry"]["lines"][0]["amount"], r["computed"]["gst"]), (300.0, "30.00"))

        code, r = run("pay", "projects.yaml", "SB-2027-014", "--number", "CCP-2207", "--date", "16/10/2026", "--amount", "1127.50",
                      "--file", "inbox/IMG_4417.png", "--yes", cwd=ws)
        expect("payment from the screenshot recorded", (r["written"], r["payment"]["source"]), (True, "processed/PAY_CCP-2207_16-10-2026.png"))
        code, r = run("pay", "projects.yaml", "SB-2027-014", "--number", "CCP-2207", "--date", "17/10/2026", "--amount", "10", cwd=ws)
        expect("overpayment refused", (code, r["ok"]), (1, False))
        code, r = run("file", "projects.yaml", "SB-2027-020", "--file", "inbox/ocean/docket.jpg", "--label", "Delivery docket", "--yes", cwd=ws)
        expect("other documents filed with a label", r["filed_as"].startswith("processed/Delivery_docket_"), True)

        out = ws / "out" / "dashboard"
        p = subprocess.run([sys.executable, str(ROOT / "tools" / "dashboard.py"), str(ws / "projects.yaml"), "--as-at", "31/10/2026",
                            "--out", str(out)], capture_output=True, text=True)
        expect("dashboard builds from project folders", p.returncode, 0)
        report = json.loads(p.stdout)
        expect("project with no start date is listed as skipped", any("SB-2027-020: no start date" in w for w in report["warnings"]), True)
        txns = {r["number"]: r for r in csv.DictReader((out / "transactions.csv").open(newline=""))}
        expect("bill paid in full on the dashboard", (txns["CCP-2207"]["paid_inc_gst"], txns["CCP-2207"]["outstanding_inc_gst"]), ("1127.50", "0.00"))
        expect("bill links to its source PDF", txns["CCP-2207"]["source_link"],
               "../../SB-2027-014_Banksia_St_extension/processed/BILL_Coastal_Concrete_Pumping_Pty_Ltd_CCP-2207.pdf")
        docs = {d["file"]: d["document"] for d in csv.DictReader((out / "documents.csv").open(newline=""))}
        expect("received documents listed", (docs.get("processed/BILL_Coastal_Concrete_Pumping_Pty_Ltd_CCP-2207.pdf"),
                                             docs.get("processed/PAY_CCP-2207_16-10-2026.png")),
               ("Supplier bill (received)", "Payment record (received)"))

    print(f"\n{'all project checks passed' if not failures else f'{failures} failed'}")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
