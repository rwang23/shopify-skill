#!/usr/bin/env python3
"""
Shopify Skill CLI

Read-only by default. Write operations require explicit --apply.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import random
import sys
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple
from urllib import error, request


DEFAULT_API_VERSION = "2026-01"


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso_utc(dt: datetime | None = None) -> str:
    val = dt or utc_now()
    return val.strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_env(path: Path) -> Dict[str, str]:
    data: Dict[str, str] = {}
    if not path.exists():
        return data
    for raw in path.read_text(encoding="utf-8").splitlines():
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


def classify_error(msg: str) -> str:
    low = msg.lower()
    if "401" in low or "unauthorized" in low:
        return "auth"
    if "403" in low or "forbidden" in low or "access_denied" in low:
        return "permission"
    if "404" in low:
        return "not_found"
    if "429" in low or "throttle" in low or "rate limit" in low:
        return "rate_limit"
    if "undefinedfield" in low or "graphql errors" in low or "syntax error" in low:
        return "query"
    return "unknown"


@dataclass
class Config:
    shop: str
    token: str
    api_version: str
    project_root: Path
    output_root: Path
    timeout_sec: int
    retries: int


class AuditRun:
    def __init__(self, cfg: Config, operation: str):
        now = utc_now()
        run_id = uuid.uuid4().hex[:6]
        date_part = now.strftime("%Y%m%d")
        time_part = now.strftime("%H%M%S")
        self.operation = operation
        self.run_id = run_id
        self.run_dir = cfg.output_root / date_part / f"{time_part}-{operation}-{run_id}"
        self.run_dir.mkdir(parents=True, exist_ok=True)

    def write_json(self, name: str, payload: Any) -> Path:
        p = self.run_dir / name
        with p.open("w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        return p

    def write_csv(self, name: str, rows: List[Dict[str, Any]], fieldnames: List[str]) -> Path:
        p = self.run_dir / name
        with p.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            for r in rows:
                w.writerow(r)
        return p

    def write_text(self, name: str, content: str) -> Path:
        p = self.run_dir / name
        p.write_text(content, encoding="utf-8")
        return p


class ShopifyClient:
    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.url = f"https://{cfg.shop}/admin/api/{cfg.api_version}/graphql.json"

    def _req(self, query: str, variables: Dict[str, Any]) -> Dict[str, Any]:
        headers = {
            "Content-Type": "application/json",
            "X-Shopify-Access-Token": self.cfg.token,
        }
        payload = json.dumps({"query": query, "variables": variables}).encode("utf-8")
        req = request.Request(url=self.url, method="POST", headers=headers, data=payload)
        with request.urlopen(req, timeout=self.cfg.timeout_sec) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def gql(self, query: str, variables: Dict[str, Any] | None = None) -> Dict[str, Any]:
        vars_obj = variables or {}
        attempt = 0
        while True:
            attempt += 1
            try:
                result = self._req(query, vars_obj)
                if result.get("errors"):
                    raise RuntimeError(json.dumps(result["errors"], ensure_ascii=False))
                return result
            except error.HTTPError as exc:
                body = exc.read().decode("utf-8", errors="replace") if exc.fp else ""
                msg = f"HTTP {exc.code}: {body or exc.reason}"
                if classify_error(msg) == "rate_limit" and attempt <= self.cfg.retries:
                    time.sleep(min(8, 2 ** attempt))
                    continue
                raise RuntimeError(msg)
            except Exception as exc:
                msg = str(exc)
                if classify_error(msg) == "rate_limit" and attempt <= self.cfg.retries:
                    time.sleep(min(8, 2 ** attempt))
                    continue
                raise


def load_config(args: argparse.Namespace) -> Config:
    project_root = Path(args.project_root).resolve()
    env = parse_env(project_root / ".env")
    shop = os.environ.get("SHOPIFY_SHOP") or env.get("SHOPIFY_SHOP") or env.get("SHOPIFY_STORE_URL")
    token = os.environ.get("SHOPIFY_ADMIN_TOKEN") or env.get("SHOPIFY_ADMIN_TOKEN") or env.get("SHOPIFY_ACCESS_TOKEN")
    api_version = args.api_version or os.environ.get("SHOPIFY_API_VERSION") or env.get("SHOPIFY_API_VERSION") or DEFAULT_API_VERSION

    if not shop or not token:
        raise ValueError("Missing credentials. Set SHOPIFY_SHOP and SHOPIFY_ADMIN_TOKEN in project-root .env")

    output_root = project_root / args.output_root
    output_root.mkdir(parents=True, exist_ok=True)

    return Config(
        shop=normalize_shop(shop),
        token=token,
        api_version=api_version,
        project_root=project_root,
        output_root=output_root,
        timeout_sec=args.timeout,
        retries=args.retries,
    )


def load_query(args: argparse.Namespace) -> str:
    if args.query and args.query_file:
        raise ValueError("Use either --query or --query-file, not both")
    if args.query_file:
        return Path(args.query_file).read_text(encoding="utf-8").strip()
    if args.query:
        return args.query.strip()
    raise ValueError("Provide --query or --query-file")


def load_variables(args: argparse.Namespace) -> Dict[str, Any]:
    if args.variables and args.variables_file:
        raise ValueError("Use either --variables or --variables-file, not both")
    if args.variables_file:
        data = json.loads(Path(args.variables_file).read_text(encoding="utf-8"))
    else:
        data = json.loads(args.variables or "{}")
    if not isinstance(data, dict):
        raise ValueError("Variables must be a JSON object")
    return data


def fetch_all_variants(client: ShopifyClient, page_size: int = 250) -> List[Dict[str, Any]]:
    query = """
    query Variants($first: Int!, $after: String) {
      productVariants(first: $first, after: $after, sortKey: ID) {
        pageInfo { hasNextPage endCursor }
        nodes {
          id
          sku
          inventoryQuantity
          inventoryPolicy
          product { id title status vendor }
          inventoryItem {
            id
            inventoryLevels(first: 10) {
              nodes {
                location { id name }
                quantities(names: [\"available\"]) { name quantity }
              }
            }
          }
        }
      }
    }
    """
    out: List[Dict[str, Any]] = []
    after = None
    while True:
        data = client.gql(query, {"first": page_size, "after": after})["data"]["productVariants"]
        out.extend(data["nodes"])
        if not data["pageInfo"]["hasNextPage"]:
            break
        after = data["pageInfo"]["endCursor"]
    return out


def get_available_level(variant: Dict[str, Any]) -> Tuple[Dict[str, Any] | None, int | None]:
    levels = (((variant.get("inventoryItem") or {}).get("inventoryLevels") or {}).get("nodes") or [])
    best_level = None
    best_qty = None
    for lv in levels:
        avail = None
        for q in lv.get("quantities") or []:
            if q.get("name") == "available":
                avail = q.get("quantity")
                break
        if avail is None:
            continue
        if best_level is None or int(avail) > int(best_qty):
            best_level = lv
            best_qty = int(avail)
    return best_level, best_qty


def cmd_query(args: argparse.Namespace, cfg: Config, client: ShopifyClient, run: AuditRun) -> int:
    query = load_query(args)
    variables = load_variables(args)
    run.write_json("request.json", {"query": query, "variables": variables})

    result = client.gql(query, variables)
    run.write_json("result.json", result)

    summary = {
        "operation": "query",
        "timestamp_utc": iso_utc(),
        "shop": cfg.shop,
        "api_version": cfg.api_version,
        "run_dir": str(run.run_dir),
        "ok": True,
    }
    run.write_json("summary.json", summary)
    print(json.dumps(summary, ensure_ascii=False))
    print(str(run.run_dir))
    return 0


def cmd_capabilities(args: argparse.Namespace, cfg: Config, client: ShopifyClient, run: AuditRun) -> int:
    run.write_json("request.json", {"operation": "capabilities"})

    checks: Dict[str, Any] = {}

    q_shop = "{ shop { name myshopifyDomain currencyCode plan { displayName partnerDevelopment } } }"
    checks["shop"] = client.gql(q_shop)["data"]["shop"]

    # PII permission probe
    probe = "{ customers(first: 1) { nodes { id email } } }"
    pii_ok = True
    pii_err = None
    try:
        client.gql(probe)
    except Exception as exc:
        pii_ok = False
        pii_err = str(exc)

    checks["customer_pii_access"] = {"ok": pii_ok, "error": pii_err}
    run.write_json("result.json", checks)

    summary = {
        "operation": "capabilities",
        "timestamp_utc": iso_utc(),
        "shop": cfg.shop,
        "api_version": cfg.api_version,
        "customer_pii_access": pii_ok,
        "run_dir": str(run.run_dir),
    }
    run.write_json("summary.json", summary)
    print(json.dumps(summary, ensure_ascii=False))
    print(str(run.run_dir))
    return 0


def cmd_scan_stock(args: argparse.Namespace, cfg: Config, client: ShopifyClient, run: AuditRun) -> int:
    threshold = args.threshold
    variants = fetch_all_variants(client)

    exclude = (args.exclude_product or "").strip().lower()

    out_of_stock: List[Dict[str, Any]] = []
    over_threshold: List[Dict[str, Any]] = []

    for v in variants:
        p = v.get("product") or {}
        title = p.get("title") or ""
        if exclude and title.strip().lower() == exclude:
            continue

        qty = v.get("inventoryQuantity")
        row = {
            "product_title": title,
            "product_status": p.get("status") or "",
            "vendor": p.get("vendor") or "",
            "sku": (v.get("sku") or "").strip(),
            "inventory_quantity": int(qty or 0),
            "variant_id": v.get("id") or "",
        }
        if qty is not None and int(qty) <= 0:
            out_of_stock.append(row)
        if qty is not None and int(qty) > threshold:
            over_threshold.append(row)

    out_of_stock.sort(key=lambda x: (x["product_title"], x["sku"]))
    over_threshold.sort(key=lambda x: (-x["inventory_quantity"], x["product_title"], x["sku"]))

    run.write_json("request.json", {"threshold": threshold, "exclude_product": args.exclude_product})
    run.write_json("result.json", {"out_of_stock": out_of_stock, "over_threshold": over_threshold})
    run.write_csv("out-of-stock.csv", out_of_stock, ["product_title", "sku", "inventory_quantity", "product_status", "vendor", "variant_id"])
    run.write_csv("stock-over-threshold.csv", over_threshold, ["product_title", "sku", "inventory_quantity", "product_status", "vendor", "variant_id"])

    summary = {
        "operation": "scan-stock",
        "timestamp_utc": iso_utc(),
        "shop": cfg.shop,
        "api_version": cfg.api_version,
        "threshold": threshold,
        "variants_scanned": len(variants),
        "out_of_stock_count": len(out_of_stock),
        "over_threshold_count": len(over_threshold),
        "run_dir": str(run.run_dir),
    }
    run.write_json("summary.json", summary)
    print(json.dumps(summary, ensure_ascii=False))
    print(str(run.run_dir))
    return 0


def _adjust_inventory(client: ShopifyClient, change: Dict[str, Any], reference_uri: str) -> Dict[str, Any]:
    mutation = """
    mutation Adjust($input: InventoryAdjustQuantitiesInput!) {
      inventoryAdjustQuantities(input: $input) {
        userErrors { field message }
        inventoryAdjustmentGroup {
          createdAt
          reason
          referenceDocumentUri
          changes { name delta }
        }
      }
    }
    """

    variables = {
        "input": {
            "name": "available",
            "reason": "correction",
            "referenceDocumentUri": reference_uri,
            "changes": [
                {
                    "delta": change["delta"],
                    "inventoryItemId": change["inventory_item_id"],
                    "locationId": change["location_id"],
                }
            ],
        }
    }

    out = client.gql(mutation, variables)["data"]["inventoryAdjustQuantities"]
    if out.get("userErrors"):
        return {"ok": False, "errors": out["userErrors"]}
    return {"ok": True, "payload": out}


def cmd_randomize_stock(args: argparse.Namespace, cfg: Config, client: ShopifyClient, run: AuditRun) -> int:
    random.seed()
    variants = fetch_all_variants(client)

    exclude = (args.exclude_product or "").strip().lower()
    candidates: List[Dict[str, Any]] = []

    for v in variants:
        qty = int(v.get("inventoryQuantity") or 0)
        if qty <= args.threshold:
            continue
        p = v.get("product") or {}
        title = p.get("title") or ""
        if exclude and title.strip().lower() == exclude:
            continue

        level, available = get_available_level(v)
        if level is None or available is None:
            continue

        target = random.randint(args.target_min, args.target_max)
        delta = target - int(available)
        if delta == 0:
            continue

        candidates.append(
            {
                "product_title": title,
                "sku": (v.get("sku") or "").strip(),
                "variant_id": v.get("id") or "",
                "inventory_item_id": ((v.get("inventoryItem") or {}).get("id") or ""),
                "location_id": (level.get("location") or {}).get("id") or "",
                "location_name": (level.get("location") or {}).get("name") or "",
                "available_before": int(available),
                "target": target,
                "delta": delta,
            }
        )

    candidates.sort(key=lambda x: (-x["available_before"], x["product_title"], x["sku"]))

    request_payload = {
        "threshold": args.threshold,
        "target_min": args.target_min,
        "target_max": args.target_max,
        "exclude_product": args.exclude_product,
        "apply": bool(args.apply),
        "max_changes": args.max_changes,
    }
    run.write_json("request.json", request_payload)

    if args.apply and len(candidates) > args.max_changes:
        summary = {
            "operation": "randomize-stock",
            "timestamp_utc": iso_utc(),
            "shop": cfg.shop,
            "api_version": cfg.api_version,
            "apply": True,
            "candidates_count": len(candidates),
            "max_changes": args.max_changes,
            "error": "max_changes_exceeded",
            "run_dir": str(run.run_dir),
        }
        run.write_json("summary.json", summary)
        run.write_json("result.json", {"candidates": candidates})
        print(json.dumps(summary, ensure_ascii=False))
        print(str(run.run_dir))
        return 2

    applied: List[Dict[str, Any]] = []
    failed: List[Dict[str, Any]] = []

    if args.apply:
        for idx, c in enumerate(candidates, start=1):
            ref = f"logistics://shopify-skill/randomize-stock/{utc_now().strftime('%Y%m%d')}/{run.run_id}/{idx}"
            result = _adjust_inventory(client, c, ref)
            row = dict(c)
            row["reference_document_uri"] = ref
            if result["ok"]:
                row["available_after_expected"] = c["target"]
                applied.append(row)
            else:
                row["errors"] = json.dumps(result.get("errors"), ensure_ascii=False)
                failed.append(row)
    else:
        applied = []
        failed = []

    rollback_plan = {
        "operation": "rollback-stock",
        "source_operation": "randomize-stock",
        "generated_at_utc": iso_utc(),
        "shop": cfg.shop,
        "api_version": cfg.api_version,
        "changes": [
            {
                "product_title": a["product_title"],
                "sku": a["sku"],
                "inventory_item_id": a["inventory_item_id"],
                "location_id": a["location_id"],
                "delta": -int(a["delta"]),
            }
            for a in applied
        ],
    }

    result_payload = {
        "candidates": candidates,
        "applied": applied,
        "failed": failed,
        "dry_run_preview": [] if args.apply else candidates,
    }
    run.write_json("result.json", result_payload)

    if args.apply:
        run.write_csv(
            "applied.csv",
            applied,
            [
                "product_title",
                "sku",
                "available_before",
                "target",
                "delta",
                "available_after_expected",
                "location_name",
                "reference_document_uri",
            ],
        )
        run.write_csv(
            "failed.csv",
            failed,
            [
                "product_title",
                "sku",
                "available_before",
                "target",
                "delta",
                "location_name",
                "reference_document_uri",
                "errors",
            ],
        )
        run.write_json("rollback-plan.json", rollback_plan)

    summary = {
        "operation": "randomize-stock",
        "timestamp_utc": iso_utc(),
        "shop": cfg.shop,
        "api_version": cfg.api_version,
        "apply": bool(args.apply),
        "threshold": args.threshold,
        "target_min": args.target_min,
        "target_max": args.target_max,
        "variants_scanned": len(variants),
        "candidates_count": len(candidates),
        "applied_count": len(applied),
        "failed_count": len(failed),
        "run_dir": str(run.run_dir),
    }
    run.write_json("summary.json", summary)

    print(json.dumps(summary, ensure_ascii=False))
    print(str(run.run_dir))
    return 0


def cmd_rollback_stock(args: argparse.Namespace, cfg: Config, client: ShopifyClient, run: AuditRun) -> int:
    plan = json.loads(Path(args.rollback_file).read_text(encoding="utf-8"))
    changes = plan.get("changes") or []

    run.write_json("request.json", {"rollback_file": args.rollback_file, "apply": bool(args.apply), "max_changes": args.max_changes})

    if args.apply and len(changes) > args.max_changes:
        summary = {
            "operation": "rollback-stock",
            "timestamp_utc": iso_utc(),
            "shop": cfg.shop,
            "api_version": cfg.api_version,
            "apply": True,
            "changes_count": len(changes),
            "max_changes": args.max_changes,
            "error": "max_changes_exceeded",
            "run_dir": str(run.run_dir),
        }
        run.write_json("summary.json", summary)
        run.write_json("result.json", {"changes": changes})
        print(json.dumps(summary, ensure_ascii=False))
        print(str(run.run_dir))
        return 2

    applied: List[Dict[str, Any]] = []
    failed: List[Dict[str, Any]] = []

    if args.apply:
        for idx, c in enumerate(changes, start=1):
            row = dict(c)
            ref = f"logistics://shopify-skill/rollback-stock/{utc_now().strftime('%Y%m%d')}/{run.run_id}/{idx}"
            row["reference_document_uri"] = ref
            result = _adjust_inventory(
                client,
                {
                    "delta": int(c["delta"]),
                    "inventory_item_id": c["inventory_item_id"],
                    "location_id": c["location_id"],
                },
                ref,
            )
            if result["ok"]:
                applied.append(row)
            else:
                row["errors"] = json.dumps(result.get("errors"), ensure_ascii=False)
                failed.append(row)

    run.write_json("result.json", {"changes": changes, "applied": applied, "failed": failed, "dry_run_preview": [] if args.apply else changes})

    if args.apply:
        run.write_csv("applied.csv", applied, ["product_title", "sku", "delta", "reference_document_uri"])
        run.write_csv("failed.csv", failed, ["product_title", "sku", "delta", "reference_document_uri", "errors"])

    summary = {
        "operation": "rollback-stock",
        "timestamp_utc": iso_utc(),
        "shop": cfg.shop,
        "api_version": cfg.api_version,
        "apply": bool(args.apply),
        "changes_count": len(changes),
        "applied_count": len(applied),
        "failed_count": len(failed),
        "run_dir": str(run.run_dir),
    }
    run.write_json("summary.json", summary)

    print(json.dumps(summary, ensure_ascii=False))
    print(str(run.run_dir))
    return 0


def _summarize_orders(orders: List[Dict[str, Any]], start: datetime, end: datetime) -> Dict[str, Any]:
    selected = []
    for o in orders:
        dt = datetime.fromisoformat(o["createdAt"].replace("Z", "+00:00"))
        if start <= dt < end:
            selected.append(o)

    revenue = 0.0
    discounts = 0.0
    product_rev: Dict[str, float] = {}
    country: Dict[str, int] = {}
    for o in selected:
        revenue += float(o["currentTotalPriceSet"]["shopMoney"]["amount"])
        discounts += float(o["totalDiscountsSet"]["shopMoney"]["amount"])
        cc = ((o.get("shippingAddress") or {}).get("countryCode") or "UNKNOWN")
        country[cc] = country.get(cc, 0) + 1
        for li in ((o.get("lineItems") or {}).get("nodes") or []):
            p = li.get("product") or {}
            title = p.get("title") or "Unknown product"
            amt = float(li["discountedTotalSet"]["shopMoney"]["amount"])
            product_rev[title] = product_rev.get(title, 0.0) + amt

    aov = revenue / len(selected) if selected else 0.0
    return {
        "orders": len(selected),
        "revenue": revenue,
        "discounts": discounts,
        "aov": aov,
        "country_top": sorted(country.items(), key=lambda x: x[1], reverse=True)[:10],
        "product_rev_top": sorted(product_rev.items(), key=lambda x: x[1], reverse=True)[:10],
    }


def cmd_report_sales(args: argparse.Namespace, cfg: Config, client: ShopifyClient, run: AuditRun) -> int:
    q = """
    query Orders($first: Int!, $after: String) {
      orders(first: $first, after: $after, reverse: true, sortKey: CREATED_AT) {
        pageInfo { hasNextPage endCursor }
        nodes {
          id
          name
          createdAt
          currentTotalPriceSet { shopMoney { amount currencyCode } }
          totalDiscountsSet { shopMoney { amount } }
          shippingAddress { countryCode }
          lineItems(first: 50) {
            nodes {
              quantity
              discountedTotalSet { shopMoney { amount } }
              product { id title }
            }
          }
        }
      }
    }
    """

    orders: List[Dict[str, Any]] = []
    after = None
    pages = 0
    while True:
        pages += 1
        data = client.gql(q, {"first": args.page_size, "after": after})["data"]["orders"]
        orders.extend(data["nodes"])
        if not data["pageInfo"]["hasNextPage"] or pages >= args.max_pages:
            break
        after = data["pageInfo"]["endCursor"]

    now = utc_now()
    last30 = _summarize_orders(orders, now - timedelta(days=30), now)
    prev30 = _summarize_orders(orders, now - timedelta(days=60), now - timedelta(days=30))

    delta = {
        "orders_pct": ((last30["orders"] - prev30["orders"]) / prev30["orders"] * 100.0) if prev30["orders"] else None,
        "revenue_pct": ((last30["revenue"] - prev30["revenue"]) / prev30["revenue"] * 100.0) if prev30["revenue"] else None,
        "aov_pct": ((last30["aov"] - prev30["aov"]) / prev30["aov"] * 100.0) if prev30["aov"] else None,
    }

    result = {
        "sample": {
            "orders_loaded": len(orders),
            "pages_loaded": pages,
            "max_pages": args.max_pages,
        },
        "last30": last30,
        "prev30": prev30,
        "delta": delta,
    }

    md = [
        "# Shopify Sales Report",
        "",
        f"- Generated at (UTC): {iso_utc()}",
        f"- Shop: {cfg.shop}",
        f"- Orders loaded: {len(orders)}",
        "",
        "## KPI",
        f"- Last 30d orders: {last30['orders']}",
        f"- Last 30d revenue: {last30['revenue']:.2f}",
        f"- Last 30d AOV: {last30['aov']:.2f}",
        f"- Revenue delta vs previous 30d: {delta['revenue_pct']:.2f}%" if delta["revenue_pct"] is not None else "- Revenue delta vs previous 30d: n/a",
        "",
        "## Top Products (Last 30d)",
    ]
    for name, val in last30["product_rev_top"]:
        md.append(f"- {name}: {val:.2f}")

    run.write_json("request.json", {"page_size": args.page_size, "max_pages": args.max_pages})
    run.write_json("result.json", result)
    run.write_text("report.md", "\n".join(md) + "\n")

    summary = {
        "operation": "report-sales",
        "timestamp_utc": iso_utc(),
        "shop": cfg.shop,
        "api_version": cfg.api_version,
        "orders_loaded": len(orders),
        "pages_loaded": pages,
        "run_dir": str(run.run_dir),
    }
    run.write_json("summary.json", summary)

    print(json.dumps(summary, ensure_ascii=False))
    print(str(run.run_dir))
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Shopify Skill CLI")
    p.add_argument("--project-root", default=str(Path.cwd()), help="Project root containing .env")
    p.add_argument("--output-root", default="shopify-skill-output", help="Audit output root under project-root")
    p.add_argument("--api-version", default=None, help="Admin API version override")
    p.add_argument("--timeout", type=int, default=45, help="HTTP timeout in seconds")
    p.add_argument("--retries", type=int, default=2, help="Retry count for rate-limit/transient errors")

    sp = p.add_subparsers(dest="command")

    q = sp.add_parser("query", help="Execute GraphQL query/mutation")
    q.add_argument("--query", default=None)
    q.add_argument("--query-file", default=None)
    q.add_argument("--variables", default="{}")
    q.add_argument("--variables-file", default=None)

    c = sp.add_parser("capabilities", help="Check plan/scopes/access limitations")

    ss = sp.add_parser("scan-stock", help="Scan out-of-stock and over-threshold SKUs")
    ss.add_argument("--threshold", type=int, default=50)
    ss.add_argument("--exclude-product", default=None)

    rs = sp.add_parser("randomize-stock", help="Randomize >threshold stock into target range")
    rs.add_argument("--threshold", type=int, default=50)
    rs.add_argument("--target-min", type=int, default=20)
    rs.add_argument("--target-max", type=int, default=35)
    rs.add_argument("--exclude-product", default="Shipment Protection+")
    rs.add_argument("--apply", action="store_true", help="Actually write inventory changes")
    rs.add_argument("--max-changes", type=int, default=20)

    rb = sp.add_parser("rollback-stock", help="Rollback using rollback-plan.json")
    rb.add_argument("--rollback-file", required=True)
    rb.add_argument("--apply", action="store_true", help="Actually write rollback changes")
    rb.add_argument("--max-changes", type=int, default=20)

    rp = sp.add_parser("report-sales", help="Generate 30/30 sales report")
    rp.add_argument("--page-size", type=int, default=100)
    rp.add_argument("--max-pages", type=int, default=10)

    return p


def run_command(args: argparse.Namespace) -> int:
    cfg = load_config(args)
    command = args.command or "query"
    run = AuditRun(cfg, command)
    client = ShopifyClient(cfg)

    try:
        if command == "query":
            return cmd_query(args, cfg, client, run)
        if command == "capabilities":
            return cmd_capabilities(args, cfg, client, run)
        if command == "scan-stock":
            return cmd_scan_stock(args, cfg, client, run)
        if command == "randomize-stock":
            return cmd_randomize_stock(args, cfg, client, run)
        if command == "rollback-stock":
            return cmd_rollback_stock(args, cfg, client, run)
        if command == "report-sales":
            return cmd_report_sales(args, cfg, client, run)

        raise ValueError(f"Unknown command: {command}")
    except Exception as exc:
        summary = {
            "operation": command,
            "timestamp_utc": iso_utc(),
            "shop": cfg.shop,
            "api_version": cfg.api_version,
            "ok": False,
            "error_type": classify_error(str(exc)),
            "error": str(exc),
            "run_dir": str(run.run_dir),
        }
        run.write_json("summary.json", summary)
        run.write_json("result.json", {"error": str(exc)})
        print(json.dumps(summary, ensure_ascii=False))
        print(str(run.run_dir))
        return 1


def main() -> int:
    parser = build_parser()
    # Backward compatibility: allow legacy invocation with only --query and no subcommand
    argv = sys.argv[1:]
    legacy_flags = {"--query", "--query-file", "--variables", "--variables-file"}
    if argv and argv[0] in legacy_flags:
        argv = ["query", *argv]
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 1

    if args.command == "randomize-stock" and args.target_min > args.target_max:
        print(json.dumps({"error": "target-min must be <= target-max"}))
        return 1

    return run_command(args)


if __name__ == "__main__":
    sys.exit(main())
