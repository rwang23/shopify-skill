import tempfile
import unittest
from pathlib import Path

import sys
sys.path.insert(0, r"C:\Users\desre\.codex\skills\shopify-skill\scripts")

import admin_graphql_query as mod


class TestHelpers(unittest.TestCase):
    def test_normalize_shop(self):
        self.assertEqual(mod.normalize_shop("my-store"), "my-store.myshopify.com")
        self.assertEqual(mod.normalize_shop("https://abc.myshopify.com/"), "abc.myshopify.com")

    def test_classify_error(self):
        self.assertEqual(mod.classify_error("HTTP 401: Unauthorized"), "auth")
        self.assertEqual(mod.classify_error("HTTP 403: forbidden"), "permission")
        self.assertEqual(mod.classify_error("HTTP 429: rate limit"), "rate_limit")
        self.assertEqual(mod.classify_error("syntax error, unexpected"), "query")

    def test_parse_env(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / ".env"
            p.write_text("SHOPIFY_SHOP=test.myshopify.com\n#X\nSHOPIFY_ADMIN_TOKEN=abc\n", encoding="utf-8")
            env = mod.parse_env(p)
            self.assertEqual(env["SHOPIFY_SHOP"], "test.myshopify.com")
            self.assertEqual(env["SHOPIFY_ADMIN_TOKEN"], "abc")

    def test_audit_run_structure(self):
        with tempfile.TemporaryDirectory() as td:
            cfg = mod.Config(
                shop="test.myshopify.com",
                token="x",
                api_version="2026-01",
                project_root=Path(td),
                output_root=Path(td) / "out",
                timeout_sec=10,
                retries=1,
            )
            run = mod.AuditRun(cfg, "scan-stock")
            self.assertTrue(run.run_dir.exists())
            self.assertIn("-scan-stock-", run.run_dir.name)


if __name__ == "__main__":
    unittest.main()
