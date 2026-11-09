import importlib.util
import json
import pathlib
import tempfile
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


def asst(mid, model="claude-sonnet-5-5", inp=10, content=None):
    return {"type": "assistant", "timestamp": "2026-11-05T10:00:00Z", "cwd": "/x",
            "message": {"id": mid, "model": model,
                        "usage": {"output_tokens": 1, "input_tokens": inp},
                        "content": content or [{"type": "text", "text": "x"}]}}


def agent_call(tid):
    return asst("call-" + tid, inp=0, content=[
        {"type": "tool_use", "id": tid, "name": "Agent",
         "input": {"subagent_type": "implementador-haiku", "model": "haiku"}}])


def write_jsonl(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(r) for r in rows) + "\n")


START = {"type": "user", "timestamp": "2026-11-05T10:00:00Z", "cwd": "/x",
         "message": {"content": "<command-name>/cost-aware-delegation</command-name>"}}


class TmpCase(unittest.TestCase):
    def setUp(self):
        self._t = tempfile.TemporaryDirectory()
        self.addCleanup(self._t.cleanup)
        self.root = pathlib.Path(self._t.name)

    def run_claude(self):
        return list(ur.claude_sessions(self.root))

    def worker(self, proj, sid, name, turns, model="claude-haiku-4-5", inp=10,
               meta=None, ):
        base = self.root / proj / sid / "subagents"
        write_jsonl(base / ("agent-%s.jsonl" % name),
                    [asst("%s-%d" % (name, i), model, inp) for i in range(turns)])
        if meta is not None:
            (base / ("agent-%s.meta.json" % name)).write_text(json.dumps(meta))


class DedupTests(TmpCase):
    def test_two_project_dirs_one_session(self):
        rows = [START, asst("a"), agent_call("t1")]
        write_jsonl(self.root / "p1" / "sid12345.jsonl", rows)
        write_jsonl(self.root / "p2" / "sid12345.jsonl", rows + [asst("b")])
        self.worker("p1", "sid12345", "x", 2, meta={"agentType": "implementador-haiku",
                                                    "toolUseId": "t1"})
        self.worker("p2", "sid12345", "x", 2, meta={"agentType": "implementador-haiku",
                                                    "toolUseId": "t1"})
        self.worker("p2", "sid12345", "y", 1)
        (s,) = self.run_claude()
        self.assertEqual(s["copies"], 2)
        self.assertEqual(s["main_turns"], 3)  # copia maior
        self.assertEqual(len(s["worker_list"]), 2)  # agent-x contado uma vez
        self.assertIn("(2 copias)", ur.render(s))


class WorkerTests(TmpCase):
    def test_skill_worker_and_missing_meta(self):
        write_jsonl(self.root / "p" / "sid12345.jsonl", [START, asst("a"), agent_call("t1")])
        self.worker("p", "sid12345", "a", 1, meta={"agentType": "implementador-haiku",
                                                   "toolUseId": "t1"})
        self.worker("p", "sid12345", "b", 1, meta={
            "agentType": "general-purpose", "isBuiltIn": True,
            "name": "code-review", "toolUseId": "toolu_other"})
        self.worker("p", "sid12345", "c", 1)
        (s,) = self.run_claude()
        by = {w["type"]: w for w in s["worker_list"]}
        self.assertFalse(by["implementador-haiku"]["skill"])
        self.assertTrue(by["code-review"]["skill"])
        self.assertEqual(by["tipo desconhecido"]["turns"], 1)
        self.assertTrue(by["tipo desconhecido"]["skill"])
        self.assertIn("tipo desconhecido", ur.render(s))

    def test_main_metrics_and_ratio(self):
        bash = asst("b", content=[{"type": "tool_use", "id": "bb", "name": "Bash", "input": {}}])
        write_jsonl(self.root / "p" / "sid12345.jsonl", [START, asst("a", inp=100), bash])
        s, = self.run_claude()
        self.assertEqual((s["main_turns"], s["main_bash_calls"]), (2, 1))
        self.assertIsNone(s["input_ratio"])  # sem workers: omitida
        self.assertNotIn("razao", ur.render(s))


class HintTests(TmpCase):
    def hints(self, **kw):
        write_jsonl(self.root / "p" / "sid12345.jsonl",
                    [START, asst("a", inp=kw.pop("main_in", 1)), agent_call("t1")])
        self.worker("p", "sid12345", "w", kw.pop("turns", 1),
                    model=kw.pop("model", "claude-haiku-4-5"), inp=kw.pop("inp", 1),
                    meta={"agentType": "implementador-haiku", "toolUseId": "t1"})
        (s,) = self.run_claude()
        return "\n".join(s["hints"])

    def test_cheap_loop(self):
        self.assertNotIn("laco longo", self.hints(turns=ur.CHEAP_LOOP_TURNS))
        self.assertIn("laco longo", self.hints(turns=ur.CHEAP_LOOP_TURNS + 1))
        self.assertIn("laco longo", self.hints(turns=61, model="luna-1"))
        self.assertNotIn("laco longo", self.hints(turns=61, model="claude-sonnet-5-5"))

    def test_haiku_long_prompt(self):
        lim = ur.HAIKU_LONG_PROMPT_TOKENS
        self.assertNotIn("contexto grande", self.hints(inp=lim))
        self.assertIn("contexto grande", self.hints(inp=lim + 1))

    def test_heavy_main(self):
        self.assertNotIn("principal pesado", self.hints(main_in=1, inp=1))
        self.assertIn("principal pesado", self.hints(main_in=5, inp=1))

    def test_no_hints_section_when_empty(self):
        self.hints()
        (s,) = self.run_claude()
        self.assertNotIn("indicios:", ur.render(s))


class CodexWaitTests(TmpCase):
    def codex(self, sleeps):
        calls = [{"type": "response_item", "payload": {
            "type": "function_call", "name": "sleep", "arguments": "{}"}}] * sleeps
        calls.append({"type": "response_item", "payload": {
            "type": "function_call", "name": "wait_agent", "arguments": "{}"}})
        rows = [{"type": "session_meta", "payload": {
            "id": "codexid1-xxxx", "cwd": "/x", "timestamp": "2026-11-05T10:00:00Z"}},
            {"type": "response_item", "payload": {
                "type": "message", "role": "user",
                "content": [{"type": "input_text", "text": "cost-aware-delegation"}]}}]
        write_jsonl(self.root / "2026" / "11" / "05" / "rollout-a.jsonl", rows + calls)
        return list(ur.codex_sessions(self.root))[0]

    def test_active_wait(self):
        s = self.codex(ur.ACTIVE_WAIT_CALLS)
        self.assertEqual(s["hints"], [])
        s = self.codex(ur.ACTIVE_WAIT_CALLS + 1)
        self.assertEqual((s["sleep_calls"], s["wait_agent_calls"]), (6, 1))
        self.assertIn("indicio", s["hints"][0])
        self.assertIn("sleep=6 wait_agent=1", ur.render(s))


if __name__ == "__main__":
    unittest.main()
