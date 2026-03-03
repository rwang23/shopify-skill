#!/usr/bin/env python3
"""
Execute Shopify Admin GraphQL requests using credentials from project-root .env.

Required .env keys:
- SHOPIFY_SHOP or SHOPIFY_STORE_URL
- SHOPIFY_ADMIN_TOKEN or SHOPIFY_ACCESS_TOKEN
Optional:
- SHOPIFY_API_VERSION (default: 2026-01)
"""

import argparse
import json
import os
import sys
from pathlib import Path
from urllib import request, error


def parse_env(env_path: Path) -> dict:
    data = {}
    if not env_path.exists():
        return data
    for raw in env_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        data[k.strip()] = v.strip().strip('"').strip("'")
    return data


def normalize_shop(value: str) -> str:
    shop = value.strip().rstrip("/")
    shop = shop.replace("https://", "").replace("http://", "")
    if not shop.endswith(".myshopify.com") and "." not in shop:
        shop = f"{shop}.myshopify.com"
    return shop


def build_headers(token: str) -> dict:
    return {
        "Content-Type": "application/json",
        "X-Shopify-Access-Token": token,
    }


def hint_for_error(msg: str) -> str:
    low = msg.lower()
    if "401" in low or "unauthorized" in low:
        return "Invalid token. Update SHOPIFY_ADMIN_TOKEN/SHOPIFY_ACCESS_TOKEN in .env"
    if "403" in low or "forbidden" in low:
        return "Missing scope. Confirm app scopes match this query/mutation"
    if "404" in low:
        return "Invalid store or API version. Check SHOPIFY_SHOP and SHOPIFY_API_VERSION"
    return "Check .env keys, token scopes, and API version"


def main() -> int:
    parser = argparse.ArgumentParser(description="Execute Shopify Admin GraphQL")
    parser.add_argument("--query", required=True, help="GraphQL query or mutation string")
    parser.add_argument("--variables", default="{}", help="JSON object string for GraphQL variables")
    parser.add_argument("--api-version", default=None, help="Admin API version, e.g. 2026-01")
    args = parser.parse_args()

    env = parse_env(Path.cwd() / ".env")
    shop = os.environ.get("SHOPIFY_SHOP") or env.get("SHOPIFY_SHOP") or env.get("SHOPIFY_STORE_URL")
    token = os.environ.get("SHOPIFY_ADMIN_TOKEN") or env.get("SHOPIFY_ADMIN_TOKEN") or env.get("SHOPIFY_ACCESS_TOKEN")
    api_version = args.api_version or os.environ.get("SHOPIFY_API_VERSION") or env.get("SHOPIFY_API_VERSION") or "2026-01"

    if not shop or not token:
        print(json.dumps({
            "error": "Missing credentials",
            "hint": "Set SHOPIFY_SHOP and SHOPIFY_ADMIN_TOKEN in project-root .env",
        }))
        return 1

    try:
        variables = json.loads(args.variables)
        if not isinstance(variables, dict):
            raise ValueError("variables must be JSON object")
    except Exception as exc:
        print(json.dumps({"error": f"Invalid variables JSON: {exc}"}))
        return 1

    shop = normalize_shop(shop)
    url = f"https://{shop}/admin/api/{api_version}/graphql.json"
    payload = json.dumps({"query": args.query, "variables": variables}).encode("utf-8")

    req = request.Request(url=url, method="POST", headers=build_headers(token), data=payload)
    try:
        with request.urlopen(req, timeout=45) as resp:
            body = resp.read().decode("utf-8")
            result = json.loads(body)
    except error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace") if exc.fp else ""
        msg = f"HTTP {exc.code}: {body or exc.reason}"
        print(json.dumps({"error": msg, "hint": hint_for_error(msg)}))
        return 1
    except Exception as exc:
        msg = str(exc)
        print(json.dumps({"error": msg, "hint": hint_for_error(msg)}))
        return 1

    if result.get("errors"):
        print(json.dumps({
            "error": "GraphQL errors",
            "details": result.get("errors"),
            "hint": "Check field names, scopes, and API version",
        }, ensure_ascii=False))
        return 1

    print(json.dumps({
        "ok": True,
        "data": result.get("data", {}),
        "extensions": result.get("extensions", {}),
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())