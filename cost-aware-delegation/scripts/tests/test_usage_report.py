import importlib.util
import pathlib
import unittest

HERE = pathlib.Path(__file__).resolve().parent
FIX = HERE / "fixtures"
spec = importlib.util.spec_from_file_location(
    "usage_report", HERE.parent / "usage-report.py")
ur = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ur)


class Args:
    def __init__(self, **kw):
        self.runtime = "all"
        self.since = None
        self.session = None
        self.claude_root = str(FIX / "claude")
        self.codex_root = str(FIX / "codex")
        self.__dict__.update(kw)


class ClaudeTests(unittest.TestCase):
    def setUp(self):
        self.s = ur.collect(Args(runtime="claude"))

    def test_only_skill_sessions(self):
        self.assertEqual(len(self.s), 2)

    def test_dedupe_and_workers(self):
        s = next(x for x in self.s if x["session"] == "sess-aaa")
        main = s["tokens"]["main"]["claude-sonnet-5-5"]
        self.assertEqual(main["messages"], 2)
        self.assertEqual(main["output"], 20)
        self.assertEqual(main["input"], 210)
        self.assertEqual(s["tokens"]["workers"]["claude-haiku-4-5"]["output"], 7)
        self.assertEqual(s["main_writes"], {"calls": 1, "lines": 3})

    def test_announce_text_vs_thinking(self):
        s = next(x for x in self.s if x["session"] == "sess-aaa")
        self.assertEqual([d["announced"] for d in s["delegations"]], [True, False])
        self.assertEqual(s["announced"], 1)


class CodexTests(unittest.TestCase):
    def test_aggregation(self):
        (s,) = ur.collect(Args(runtime="codex"))
        t = s["tokens"]
        self.assertEqual(t["main"]["total_tokens"], 2000)
        self.assertEqual(t["workers"]["total_tokens"], 300)
        self.assertEqual(t["auto_review"]["total_tokens"], 50)
        self.assertEqual(s["followups_per_worker"], {"worker1": 1})
        self.assertEqual(s["announced"], 2)  # spawn e followup no mesmo turno
        self.assertEqual(len(s["delegations"]), 2)

    def test_render(self):
        (s,) = ur.collect(Args(runtime="codex"))
        self.assertIn("auto-review", ur.render(s))


class FilterTests(unittest.TestCase):
    def test_since(self):
        self.assertEqual(len(ur.collect(Args(since="2026-10-15"))), 2)
        self.assertEqual(len(ur.collect(Args(since="2026-08-01"))), 3)
        self.assertEqual(ur.collect(Args(since="2026-11-01")), [])


if __name__ == "__main__":
    unittest.main()
