"""Learn from use: which products a user picks, what's new, and (only if they say yes) share it.

Usage (in the user's jobs folder):
    python tools/usage.py report   [--log materials_log.csv] [--days 90]   # what you use, what's new, catalogue gaps
    python tools/usage.py status   [--log materials_log.csv]               # should Claude offer to share now?
    python tools/usage.py share    [--log materials_log.csv] [--out out/usage_share.md]   # draft the anonymous summary
    python tools/usage.py decline  [--never]                               # not now (asks again in 90 days), or never

For the brain's maintainer, from reports people chose to share:
    python tools/usage.py collect                                          # save new usage-report issues to raw/usage_reports/ (needs gh)
    python tools/usage.py ingest raw/usage_reports/*.json                  # rewrites brain/references/product_usage.md

How it works. tools/price_list.py writes a line to materials_log.csv (next
to the price list) whenever a product is saved or used to price a job: the
date, the product family, the takeoff item, the product name, the supplier
and the job. Never a price. The log stays in the user's folder.

`share` turns the log into a summary with no prices, no jobs, no clients,
no addresses and no store names: product names and how often each was
used, by family, with the user's trade and state. The user reads it, and
only if they say yes does Claude give them a link to post it as an issue
on the brain's GitHub repository, which they submit themselves. Nothing is
ever sent automatically.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import urllib.parse
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import catalogue  # noqa: E402

COLUMNS = ["date", "event", "family", "item", "product", "supplier", "job", "trade", "state"]
REPO_ISSUES = "https://github.com/grechj/Australian-Builders-Brain/issues/new"
OFFER_EVERY_DAYS = 90
OFFER_AFTER_ENTRIES = 20
SUMMARY_VERSION = 1


def _profile(folder: Path) -> dict:
    p = folder / "profile.yaml"
    return (yaml.safe_load(p.read_text()) or {}) if p.exists() else {}


def log_path_for(prices: Path) -> Path:
    return prices.resolve().parent / "materials_log.csv"


NOT_PRODUCTS = re.compile(r"\b(delivery|freight|cartage|fuel|surcharge|discount|rounding|labour|hire|credit|deposit|fee)\b", re.I)


def record(log: Path, event: str, item: str, product: str, supplier: str, job: str = "", family: str | None = None,
           when: str | None = None) -> None:
    """Add one line to the user's materials log. Called by price_list.py and the inbox; never records a price.
    Charges that aren't products (delivery, freight, labour, discounts) are skipped."""
    if not (product or "").strip() or NOT_PRODUCTS.search(product):
        return
    prof = _profile(log.parent)
    s = prof.get("settings") or {}
    new = not log.exists()
    with log.open("a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        if new:
            w.writeheader()
        w.writerow({"date": when or date.today().strftime("%d/%m/%Y"), "event": event,
                    "family": family or catalogue.family_of(f"{item} {product}") or "",
                    "item": item, "product": _clean(product), "supplier": supplier, "job": job,
                    "trade": s.get("trade", ""), "state": s.get("state", "")})


def _clean(product: str) -> str:
    """The product name without an item number in brackets."""
    return re.sub(r"\s*\(\d{5,8}\)\s*", " ", product or "").strip()


def read(log: Path) -> list[dict]:
    if not log.exists():
        return []
    with log.open(newline="") as f:
        return list(csv.DictReader(f))


def _d(s: str) -> date:
    return datetime.strptime(s, "%d/%m/%Y").date()


def _sizes(text: str) -> set[str]:
    return set(re.findall(r"\b\d+x\d+\b", text.lower().replace(" x ", "x")))


def report(rows: list[dict], days: int = 90, today: date | None = None) -> dict:
    """What the user uses most in each family, what's new (first used in the last `days`),
    what's rising, and gaps in the catalogue (unknown families, sizes it doesn't list)."""
    today = today or date.today()
    cut = today - timedelta(days=days)
    fams = catalogue.load()
    first_seen: dict[str, date] = {}
    by_family: dict[str, Counter] = defaultdict(Counter)
    recent: dict[str, Counter] = defaultdict(Counter)
    earlier: dict[str, Counter] = defaultdict(Counter)
    unknown, new_sizes = Counter(), defaultdict(set)
    for r in rows:
        d, prod, fam = _d(r["date"]), r["product"], r["family"] or "unknown"
        first_seen[prod] = min(first_seen.get(prod, d), d)
        by_family[fam][prod] += 1
        (recent if d >= cut else earlier)[fam][prod] += 1
        if fam == "unknown":
            unknown[r["item"] or prod] += 1
        elif fam in fams and fams[fam].get("sizes"):
            listed = {str(x).lower() for x in fams[fam]["sizes"]}
            for size in _sizes(prod) - listed:
                new_sizes[fam].add(size)
    new = sorted((p for p, d in first_seen.items() if d >= cut), key=lambda p: first_seen[p])
    rising = []
    for fam, c in recent.items():
        total_r, total_e = sum(c.values()), sum(earlier[fam].values())
        for prod, n in c.items():
            share_r = n / total_r
            share_e = earlier[fam][prod] / total_e if total_e else 0
            if total_e and total_r >= 3 and share_r - share_e >= 0.25:
                rising.append({"family": fam, "product": prod, "share_now": round(share_r, 2), "share_before": round(share_e, 2)})
    return {
        "entries": len(rows), "window_days": days,
        "top_by_family": {f: [{"product": p, "uses": n} for p, n in c.most_common(3)] for f, c in sorted(by_family.items())},
        "new_products": [{"product": p, "first_used": first_seen[p].strftime("%d/%m/%Y"),
                          "family": next((r["family"] for r in rows if r["product"] == p), "")} for p in new],
        "rising": sorted(rising, key=lambda x: -(x["share_now"] - x["share_before"])),
        "catalogue_gaps": {"unknown_items": [{"item": i, "uses": n} for i, n in unknown.most_common(10)],
                           "sizes_not_listed": {f: sorted(s) for f, s in new_sizes.items()}},
    }


def _sharing(folder: Path) -> dict:
    return (_profile(folder).get("sharing") or {})


def _set_sharing(folder: Path, **values) -> None:
    p = folder / "profile.yaml"
    if not p.exists():
        return
    text = p.read_text()
    head = "".join(line + "\n" for line in text.splitlines() if line.startswith("#"))
    prof = yaml.safe_load(text) or {}
    prof.setdefault("sharing", {}).update(values)
    p.write_text(head + yaml.safe_dump(prof, sort_keys=False, allow_unicode=True))


def status(log: Path, today: date | None = None) -> dict:
    """Whether to offer sharing now: enough new entries since the last share, not asked recently, not 'never'."""
    today = today or date.today()
    s = _sharing(log.parent)
    rows = read(log)
    since = _d(s["last_shared"]) if s.get("last_shared") else None
    fresh = [r for r in rows if not since or _d(r["date"]) > since]
    asked = _d(s["last_offered"]) if s.get("last_offered") else None
    if s.get("choice") == "never":
        offer, why = False, "the user said never"
    elif len(fresh) < OFFER_AFTER_ENTRIES:
        offer, why = False, f"{len(fresh)} entries since the last share; offer from {OFFER_AFTER_ENTRIES}"
    elif asked and (today - asked).days < OFFER_EVERY_DAYS:
        offer, why = False, f"asked {(today - asked).days} days ago; ask at most every {OFFER_EVERY_DAYS} days"
    else:
        offer, why = True, f"{len(fresh)} entries since the last share"
    return {"offer": offer, "why": why, "entries": len(rows), "new_entries": len(fresh), "choice": s.get("choice", "ask")}


def summary(rows: list[dict], trade: str, state: str) -> dict:
    """The anonymous summary: product names and counts by family, the trade and state. Nothing else."""
    counts: dict[str, Counter] = defaultdict(Counter)
    suppliers = Counter()
    for r in rows:
        counts[r["family"] or "unknown"][r["product"]] += 1
        suppliers["Bunnings" if (r.get("supplier") or "").lower().startswith("bunnings") else "other supplier"] += 1
    dates = sorted(_d(r["date"]) for r in rows)
    return {"version": SUMMARY_VERSION, "trade": trade or "not set", "state": state or "not set",
            "period": f"{dates[0]:%m/%Y} to {dates[-1]:%m/%Y}" if dates else "",
            "entries": len(rows), "suppliers": dict(suppliers),
            "families": {f: dict(c.most_common()) for f, c in sorted(counts.items())},
            "new_products": [p["product"] for p in report(rows)["new_products"]]}


def summary_markdown(s: dict) -> str:
    lines = [f"**Builder's Brain usage summary** (shared by a user, v{s['version']})", "",
             f"- Trade: {s['trade']}; state: {s['state']}; period: {s['period']}; {s['entries']} products saved or used",
             f"- Suppliers: " + ", ".join(f"{k} {v}" for k, v in s["suppliers"].items()), ""]
    for fam, prods in s["families"].items():
        lines.append(f"**{fam.replace('_', ' ')}**: " + "; ".join(f"{p} ({n})" for p, n in prods.items()))
    if s["new_products"]:
        lines += ["", "New in the last 90 days: " + "; ".join(s["new_products"])]
    lines += ["", "<details><summary>Data</summary>", "", "```json", json.dumps(s, indent=1), "```", "</details>", "",
              "No prices, jobs, clients, addresses or store names are included."]
    return "\n".join(lines)


def _safe(text) -> str:
    """Shared reports come from the public: keep product names to plain words, short, with no markup or links."""
    s = re.sub(r"https?://\S+", "", str(text))
    s = re.sub(r"[\[\]()<>|`*_#!\\{}]", " ", s)
    return re.sub(r"\s+", " ", s).strip()[:80]


def ingest(paths: list[Path]) -> str:
    """Combine shared summaries into brain/references/product_usage.md (maintainer only)."""
    totals: dict[str, Counter] = defaultdict(Counter)
    trades, states, newest = Counter(), Counter(), Counter()
    n = 0
    for p in paths:
        s = json.loads(p.read_text())
        n += 1
        trades[_safe(s.get("trade", "not set"))] += 1
        states[_safe(s.get("state", "not set"))] += 1
        for fam, prods in s.get("families", {}).items():
            for prod, c in prods.items():
                if isinstance(c, int) and 0 < c < 10000:
                    totals[_safe(fam)][_safe(prod)] += c
        for prod in s.get("new_products", [])[:50]:
            newest[_safe(prod)] += 1
    out = ["---", "type: Reference", "title: What products trades are using",
           "description: Products that Builder's Brain users chose to share, by family, and the ones that are new and spreading. Shared by opt-in only; no prices.",
           "tags: [materials, usage, products, catalogue]", "status: draft",
           "generated: { by: tool:usage.py, at: " + date.today().strftime("%Y-%m-%dT00:00:00Z") + " }", "---", "",
           "> **Generated** by `python tools/usage.py ingest` from summaries users chose to share (kept in `raw/usage_reports/`).",
           "> It shows what's popular among those users, not the whole market.", "",
           f"From {n} shared summaries. Trades: " + ", ".join(f"{t} {c}" for t, c in trades.most_common()) +
           ". States: " + ", ".join(f"{t} {c}" for t, c in states.most_common()) + ".", ""]
    if newest:
        out += ["# New and spreading", "", "Products users flagged as new to them, by how many users:", ""]
        out += [f"- {p} ({c})" for p, c in newest.most_common(15)] + [""]
    out += ["# Most used, by family", "", "| Family | Products (uses) |", "|---|---|"]
    for fam, c in sorted(totals.items()):
        out.append(f"| {fam.replace('_', ' ')} | " + "; ".join(f"{p} ({u})" for p, u in c.most_common(5)) + " |")
    out += ["", "Use it to add sizes and families to `tools/catalogue.yaml`, and products to the material guides."]
    return "\n".join(out) + "\n"


def parse_issue(body: str) -> dict | None:
    """The summary data from a usage-report issue body, or None if it isn't one."""
    if "Builder's Brain usage summary" not in body:
        return None
    m = re.search(r"```json\n(.*?)\n```", body, re.S)
    try:
        data = json.loads(m.group(1)) if m else None
    except json.JSONDecodeError:
        return None
    if not isinstance(data, dict) or not isinstance(data.get("families"), dict):
        return None
    # Keep only the fields a summary has, so nothing else can ride along into the repo.
    keep = ("version", "trade", "state", "period", "entries", "suppliers", "families", "new_products")
    return {k: data[k] for k in keep if k in data}


def collect(out_dir: Path, repo: str = "grechj/Australian-Builders-Brain") -> list[str]:
    """Save the JSON from each usage-report issue as raw/usage_reports/issue_<n>.json (maintainer, needs the gh CLI)."""
    import subprocess

    p = subprocess.run(["gh", "api", f"repos/{repo}/issues?state=all&per_page=100", "--paginate"], capture_output=True, text=True)
    if p.returncode:
        raise SystemExit("gh couldn't list the issues: " + p.stderr.strip())
    saved = []
    out_dir.mkdir(parents=True, exist_ok=True)
    for issue in json.loads(p.stdout.replace("][", ",")):
        data = parse_issue(issue.get("body") or "") if "pull_request" not in issue else None
        if data is None:
            continue
        dest = out_dir / f"issue_{issue['number']}.json"
        if not dest.exists():
            dest.write_text(json.dumps(data, indent=2))
            saved.append(dest.name)
    return saved


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    for name in ("report", "status", "share", "decline"):
        p = sub.add_parser(name)
        p.add_argument("--log", type=Path, default=Path("materials_log.csv"))
    sub.choices["report"].add_argument("--days", type=int, default=90)
    sub.choices["share"].add_argument("--out", type=Path, default=Path("out/usage_share.md"))
    sub.choices["share"].add_argument("--shared", action="store_true", help="the user posted it: record the date")
    sub.choices["decline"].add_argument("--never", action="store_true")
    p = sub.add_parser("collect"); p.add_argument("--out", type=Path, default=ROOT / "raw" / "usage_reports")
    p = sub.add_parser("ingest"); p.add_argument("reports", nargs="+", type=Path)
    p.add_argument("--out", type=Path, default=ROOT / "brain" / "references" / "product_usage.md")
    a = parser.parse_args()

    if a.cmd == "collect":
        print(json.dumps({"saved": collect(a.out)}, indent=2))
        return
    if a.cmd == "ingest":
        a.out.write_text(ingest(a.reports))
        print(f"wrote {a.out}")
        return
    log = a.log.resolve()
    folder = log.parent
    if a.cmd == "report":
        print(json.dumps(report(read(log), a.days), indent=2))
    elif a.cmd == "status":
        print(json.dumps(status(log), indent=2))
    elif a.cmd == "decline":
        _set_sharing(folder, choice="never" if a.never else "ask", last_offered=date.today().strftime("%d/%m/%Y"))
        print(json.dumps({"choice": "never" if a.never else "ask", "next_offer": "never" if a.never else f"in {OFFER_EVERY_DAYS} days"}))
    else:
        if a.shared:
            _set_sharing(folder, choice="ask", last_shared=date.today().strftime("%d/%m/%Y"),
                         last_offered=date.today().strftime("%d/%m/%Y"))
            print(json.dumps({"recorded": "shared", "on": date.today().strftime("%d/%m/%Y")}))
            return
        prof = _profile(folder)
        s = prof.get("settings") or {}
        sh = _sharing(folder)
        rows = read(log)
        if sh.get("last_shared"):
            rows = [r for r in rows if _d(r["date"]) > _d(sh["last_shared"])]
        if not rows:
            raise SystemExit("Nothing new in the materials log to share.")
        summ = summary(rows, s.get("trade", ""), s.get("state", ""))
        body = summary_markdown(summ)
        a.out.parent.mkdir(parents=True, exist_ok=True)
        a.out.write_text(body)
        (a.out.with_suffix(".json")).write_text(json.dumps(summ, indent=2))
        title = f"Usage summary: {summ['trade']}, {summ['state']}, {summ['period']}"
        link = REPO_ISSUES + "?" + urllib.parse.urlencode({"title": title, "body": body, "labels": "usage-report"})
        _set_sharing(folder, last_offered=date.today().strftime("%d/%m/%Y"))
        print(json.dumps({"summary_file": str(a.out), "entries": summ["entries"], "families": len(summ["families"]),
                          "issue_link": link if len(link) < 7500 else None,
                          "too_long_for_link": len(link) >= 7500}, indent=2))


if __name__ == "__main__":
    main()
