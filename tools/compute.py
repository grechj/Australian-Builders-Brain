"""Run an Attested Computation and print its receipt.

Usage:
    python tools/compute.py gst --param amount_ex_gst=3800
    python tools/compute.py variation_price --param labour=1200 --param materials=1450 \\
        --param subcontractor=0 --param plant=150 --param other=0 --param margin_pct=20

The computation name is a concept in brain/computations/. The receipt (JSON on
stdout) records the code that ran, the parameters and the result. Its
`fields` block plugs straight into tools/fill_template.py as --set values.
Check a receipt with brain/references/attesters/check_receipt.py.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from decimal import Decimal, InvalidOperation
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
BRAIN = ROOT / "brain"


def load_concept(name: str) -> dict:
    path = BRAIN / "computations" / f"{name}.md"
    if not path.exists():
        raise SystemExit(f"No computation concept at {path.relative_to(ROOT)}")
    front = path.read_text().split("---", 2)[1]
    meta = yaml.safe_load(front)
    if meta.get("type") != "Attested Computation":
        raise SystemExit(f"{path.name} is not an Attested Computation")
    return meta


def load_function(meta: dict):
    code_path = BRAIN / meta["computation"].lstrip("/")
    spec = importlib.util.spec_from_file_location("builder_maths", code_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return code_path, getattr(module, meta["entry_point"])


def parse_params(meta: dict, raw: list[str]) -> dict:
    given = {}
    for item in raw:
        key, sep, val = item.partition("=")
        if not sep:
            raise SystemExit(f"--param expects name=value, got {item!r}")
        given[key.strip()] = val.strip()
    declared = {p["name"]: p for p in meta["parameters"]}
    unknown = set(given) - set(declared)
    if unknown:
        raise SystemExit(f"Unknown parameters: {', '.join(sorted(unknown))}")
    params = {}
    for name, spec in declared.items():
        if name not in given:
            if spec.get("required", True):
                raise SystemExit(f"Missing required parameter: {name}")
            given[name] = str(spec.get("default", "0"))
        try:
            params[name] = Decimal(given[name].replace(",", "").replace("$", ""))
        except InvalidOperation:
            raise SystemExit(f"{name} must be a number, got {given[name]!r}")
    return params


def run(name: str, raw_params: list[str]) -> dict:
    meta = load_concept(name)
    code_path, fn = load_function(meta)
    params = parse_params(meta, raw_params)
    output = fn(**params)
    return {
        "computation": f"computations/{name}",
        "entry_point": meta["entry_point"],
        "computation_sha256": hashlib.sha256(code_path.read_bytes()).hexdigest(),
        "parameters": {k: str(v) for k, v in params.items()},
        "result": output["result"],
        "fields": output["fields"],
        # Every result figure formatted for a document, e.g. "1,413.53".
        "display": {k: f"{Decimal(v):,.2f}" for k, v in output["result"].items()},
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("name", help="computation concept, e.g. gst")
    parser.add_argument("--param", action="append", default=[], metavar="NAME=VALUE")
    args = parser.parse_args()
    print(json.dumps(run(args.name, args.param), indent=2))


if __name__ == "__main__":
    main()
