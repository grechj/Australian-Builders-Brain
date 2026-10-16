"""Attester: confirm a receipt from tools/compute.py came from the sanctioned code.

Usage:
    python tools/compute.py gst --param amount_ex_gst=3800 > receipt.json
    python brain/references/attesters/check_receipt.py receipt.json

Deterministic, no LLM. Passes only if:
  1. the code that ran matches the computation_sha256 pinned in the concept, and
  2. re-running that code with the receipt's parameters gives the same result.
Exit code 0 = pass, 1 = fail.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools"))

import compute  # noqa: E402


def check(receipt: dict) -> list[str]:
    name = receipt["computation"].split("/", 1)[1]
    meta = compute.load_concept(name)
    problems = []
    if receipt["computation_sha256"] != meta.get("computation_sha256"):
        problems.append("code that ran does not match the pinned computation_sha256")
    rerun = compute.run(name, [f"{k}={v}" for k, v in receipt["parameters"].items()])
    if rerun["computation_sha256"] != meta.get("computation_sha256"):
        problems.append("sanctioned code on disk has changed since the concept was pinned")
    if rerun["result"] != receipt["result"]:
        problems.append("result differs from a fresh run with the same parameters")
    if rerun["fields"] != receipt["fields"]:
        problems.append("template fields differ from a fresh run")
    return problems


def main() -> None:
    receipt = json.loads(Path(sys.argv[1]).read_text())
    problems = check(receipt)
    if problems:
        print("FAIL: " + "; ".join(problems))
        sys.exit(1)
    print(f"PASS: {receipt['computation']} with {receipt['parameters']}")


if __name__ == "__main__":
    main()
