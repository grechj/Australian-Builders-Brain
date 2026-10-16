"""Look up Bunnings products and prices through the official Bunnings APIs.

Usage:
    python tools/bunnings.py check                               # are the credentials working?
    python tools/bunnings.py stores "Newcastle"                  # find a store's 4-digit location code
    python tools/bunnings.py search "90x45 MGP10 treated pine 4.8m" --store 6401 --limit 5
    python tools/bunnings.py price 0123456 2345678 --store 6401  # prices inc GST at that store

Add --json for machine-readable output.

Credentials: register at https://developer.sandbox.bunnings.com.au, create an
app, and ask Bunnings for access to the Query Item, Query Pricing and Query
Location products (sandbox, then test, then live; Bunnings approves each
step). Then set:

    BUNNINGS_CLIENT_ID      the app's consumer key
    BUNNINGS_CLIENT_SECRET  the app's consumer secret
    BUNNINGS_ENV            live (default), test or sandbox (sandbox returns mock data)

This uses only the APIs. It never reads bunnings.com.au, whose terms allow
personal use only and whose robots.txt disallows automated search.

Built from Bunnings' published OpenAPI specs (Item 1.4, Pricing 1.0,
Location); response parsing is deliberately tolerant. Prices include GST.
Standard library only.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

ENVIRONMENTS = {
    "live": {"token": "https://authorisation.api.bunnings.com.au/connect/token", "api": "api.bunnings.com.au"},
    "test": {"token": "https://authorisation-stg.api.bunnings.com.au/connect/token", "api": "stg.api.bunnings.com.au"},
    "sandbox": {"token": "https://connect.sandbox.api.bunnings.com.au/connect/token", "api": "sandbox.api.bunnings.com.au"},
}
VERSIONS = {"item": "1.4", "pricing": "1.0", "location": "1.0"}
_token: dict = {}


class BunningsError(Exception):
    pass


def env() -> dict:
    name = os.environ.get("BUNNINGS_ENV", "live").lower()
    if name not in ENVIRONMENTS:
        raise BunningsError(f"BUNNINGS_ENV must be one of {', '.join(ENVIRONMENTS)}")
    return {"name": name, **ENVIRONMENTS[name]}


def base(api: str) -> str:
    return f"https://{api}.{env()['api']}/{api}"


def token() -> str:
    if _token.get("value") and _token["expires"] > time.time() + 60:
        return _token["value"]
    cid, secret = os.environ.get("BUNNINGS_CLIENT_ID"), os.environ.get("BUNNINGS_CLIENT_SECRET")
    if not cid or not secret:
        raise BunningsError("Set BUNNINGS_CLIENT_ID and BUNNINGS_CLIENT_SECRET (see the top of tools/bunnings.py for how to get them).")
    body = urllib.parse.urlencode({"client_id": cid, "client_secret": secret, "grant_type": "client_credentials"}).encode()
    req = urllib.request.Request(env()["token"], data=body, headers={"Content-Type": "application/x-www-form-urlencoded"})
    data = _send(req)
    _token.update(value=data["access_token"], expires=time.time() + int(data.get("expires_in", 3600)))
    return _token["value"]


def _send(req: urllib.request.Request, retries: int = 3) -> dict:
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                text = resp.read().decode()
                return json.loads(text) if text else {}
        except urllib.error.HTTPError as e:
            detail = e.read().decode(errors="replace")[:300]
            if e.code == 429 and attempt < retries - 1:   # spike arrest: back off
                time.sleep(2 ** (attempt + 1))
                continue
            if e.code in (401, 403):
                raise BunningsError(f"{e.code}: not authorised. Check the credentials and that Bunnings has approved this API product for your app in the {env()['name']} environment. {detail}")
            raise BunningsError(f"HTTP {e.code} from {req.full_url}: {detail}")
        except urllib.error.URLError as e:
            raise BunningsError(f"Can't reach {req.full_url}: {e.reason}")
    raise BunningsError("Rate limited by Bunnings. Wait and try again.")


def call(api: str, method: str, path: str, params: dict | None = None, body: dict | None = None) -> dict:
    url = base(api) + path + ("?" + urllib.parse.urlencode(params, safe="$,") if params else "")
    headers = {"Authorization": f"Bearer {token()}", "x-version-api": VERSIONS[api], "Accept": "application/json"}
    data = None
    if body is not None:
        data = json.dumps(body).encode()
        headers["Content-Type"] = "application/json"
    return _send(urllib.request.Request(url, data=data, headers=headers, method=method))


def _records(payload) -> list[dict]:
    """Find the list of records in a response, whatever it is wrapped in."""
    if isinstance(payload, list):
        return [x for x in payload if isinstance(x, dict)]
    if isinstance(payload, dict):
        for key in ("results", "data", "items", "locations", "prices", "value"):
            if isinstance(payload.get(key), list):
                return [x for x in payload[key] if isinstance(x, dict)]
    return []


def _pick(record: dict, *keys: str, default=""):
    for k in keys:
        cur = record
        for part in k.split("/"):
            cur = cur.get(part) if isinstance(cur, dict) else None
        if cur not in (None, ""):
            return cur
    return default


def stores(query: str) -> list[dict]:
    found, continuation, q = [], None, query.lower()
    for _ in range(20):                      # page through the store list
        params = {"$top": "100"}
        if continuation:
            params["continuationToken"] = continuation
        payload = call("location", "GET", "/locations", params)
        for loc in _records(payload):
            text = json.dumps(loc).lower()
            if q in text:
                found.append({"location_code": _pick(loc, "locationCode", "code", "id"),
                              "name": _pick(loc, "name", "displayName", "storeName"),
                              "suburb": _pick(loc, "address/suburb", "address/city", "suburb"),
                              "state": _pick(loc, "address/state", "state"),
                              "postcode": _pick(loc, "address/postcode", "address/postCode", "postcode")})
        continuation = _pick(payload, "continuationToken", "_meta/continuationToken") if isinstance(payload, dict) else None
        if not continuation:
            break
    return found


def search(query: str, store: str, limit: int) -> list[dict]:
    body = {"query": query, "sortBy": "relevancy",
            "filters": {"locationCode": store, "availableInStoreAllProducts": {"allProducts": True, "inStoreToday": False}}}
    payload = call("item", "POST", "/search/AU", body=body)
    return [{"item_number": _pick(r, "itemNumber", "_meta/itemNumber"), "title": _pick(r, "title", "name", "description")}
            for r in _records(payload)[:limit]]


def details(item_numbers: list[str]) -> dict[str, dict]:
    payload = call("item", "GET", "/details/AU", {"itemNumbers": ",".join(item_numbers)})
    return {str(_pick(r, "itemNumber")): r for r in _records(payload)}


def prices(item_numbers: list[str], store: str) -> list[dict]:
    body = {"context": {"country": "AU", "location": store}, "items": [{"itemNumber": n} for n in item_numbers]}
    payload = call("pricing", "POST", "/catalog/prices", body=body)
    out = []
    for p in _records(payload):
        out.append({"item_number": str(_pick(p, "itemNumber")), "unit_price_inc_gst": _pick(p, "unitPrice", "lineUnitPrice"),
                    "price_id": _pick(p, "priceId"), "store": store, "priced_on": time.strftime("%d/%m/%Y")})
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--json", action="store_true")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("check")
    p = sub.add_parser("stores"); p.add_argument("query")
    p = sub.add_parser("search"); p.add_argument("query"); p.add_argument("--store", required=True); p.add_argument("--limit", type=int, default=5)
    p = sub.add_parser("price"); p.add_argument("items", nargs="+"); p.add_argument("--store", required=True)
    args = parser.parse_args()
    try:
        if args.cmd == "check":
            token()
            result = {"ok": True, "environment": env()["name"]}
        elif args.cmd == "stores":
            result = stores(args.query)
        elif args.cmd == "search":
            result = search(args.query, args.store, args.limit)
        else:
            result = prices([n.zfill(7) for n in args.items], args.store)
    except BunningsError as e:
        print(f"Bunnings API: {e}", file=sys.stderr)
        sys.exit(2)
    if args.json or args.cmd == "check":
        print(json.dumps(result, indent=2))
    else:
        for row in result:
            print("  ".join(f"{v}" for v in row.values()))


if __name__ == "__main__":
    main()
