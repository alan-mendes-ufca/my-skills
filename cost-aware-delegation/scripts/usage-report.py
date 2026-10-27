#!/usr/bin/env python3
"""Resume o uso da skill cost-aware-delegation nos logs locais.

Somente leitura: varre sessoes do Claude Code (~/.claude/projects) e do Codex
CLI (~/.codex/sessions), seleciona as que usaram a skill e informa delegacoes,
verificacao de anuncio (linha com seta mencionando modelo ou tipo, em texto
visivel e nunca em thinking), tokens e escritas da thread principal.

Caveat "parcial": se uma delegacao Claude usou isolation "worktree" e nao ha
transcricao de subagente correspondente, o total dos workers esta subestimado.

Caveat do anuncio no Claude Code: o transcript pode nao gravar o bloco de texto
que precede uma chamada de ferramenta (observado na versao 2.1.311). Por isso o
relatorio diz "nao encontrado", nunca que o anuncio faltou.
"""

from __future__ import annotations

import argparse
import collections
import json
import pathlib
import sys

SKILL = "cost-aware-delegation"
REVIEWER_MODEL = "codex-auto-review"
WRITE_TOOLS = ("Edit", "Write", "MultiEdit")


def load(path):
    rows = []
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                try:
                    row = json.loads(line)
                except ValueError:
                    continue
                if isinstance(row, dict):
                    rows.append(row)
    except OSError:
        pass
    return rows


def announced(texts, aliases):
    aliases = [a.lower() for a in aliases if a]
    for text in texts:
        for line in text.splitlines():
            low = line.lower()
            if "→" in line and any(a in low for a in aliases):
                return True
    return False


def day(ts):
    return (ts or "")[:10]


# ---------------------------------------------------------------- Claude

def text_of(content):
    if isinstance(content, str):
        return content
    parts = []
    for block in content or []:
        if isinstance(block, dict) and block.get("type") == "text":
            parts.append(block.get("text", ""))
    return "\n".join(parts)


def claude_usage(rows):
    seen = {}
    for row in rows:
        if row.get("type") != "assistant":
            continue
        msg = row.get("message") or {}
        usage = msg.get("usage") or {}
        key = msg.get("id") or row.get("uuid")
        seen[key] = (
            msg.get("model") or "?",
            usage.get("output_tokens", 0) or 0,
            sum(usage.get(k, 0) or 0 for k in (
                "input_tokens", "cache_read_input_tokens",
                "cache_creation_input_tokens")),
        )
    agg = {}
    for model, out, inp in seen.values():
        a = agg.setdefault(model, {"messages": 0, "output": 0, "input": 0})
        a["messages"] += 1
        a["output"] += out
        a["input"] += inp
    return agg


def merge_usage(into, other):
    for model, v in other.items():
        a = into.setdefault(model, {"messages": 0, "output": 0, "input": 0})
        for k in a:
            a[k] += v[k]


def claude_session(path, root):
    rows = load(path)
    used = False
    start = cwd = None
    delegations = []
    pending = []
    writes = {"calls": 0, "lines": 0}
    for row in rows:
        start = start or row.get("timestamp")
        cwd = cwd or row.get("cwd")
        msg = row.get("message") or {}
        content = msg.get("content")
        if row.get("type") == "user" and not row.get("isMeta"):
            if isinstance(content, list) and any(
                    isinstance(b, dict) and b.get("type") == "tool_result"
                    for b in content):
                continue
            text = text_of(content)
            if "<command-name>/" + SKILL in text:
                used = True
            pending = []
        elif row.get("type") == "assistant" and isinstance(content, list):
            for block in content:
                if not isinstance(block, dict):
                    continue
                kind = block.get("type")
                inp = block.get("input") or {}
                if kind == "text":
                    pending.append(block.get("text", ""))
                elif kind == "tool_use":
                    name = block.get("name")
                    if name == "Skill" and inp.get("skill") == SKILL:
                        used = True
                    elif name in ("Agent", "Task"):
                        delegations.append({
                            "agent": inp.get("subagent_type"),
                            "model": inp.get("model"),
                            "effort": inp.get("effort"),
                            "isolation": inp.get("isolation"),
                            "background": bool(inp.get("run_in_background")),
                            "announced": announced(
                                pending, [inp.get("model"), inp.get("subagent_type")]),
                        })
                    elif name in WRITE_TOOLS:
                        writes["calls"] += 1
                        writes["lines"] += written_lines(name, inp)
    if not used:
        return None
    sid = path.stem
    sub_files = sorted(root.glob("*/%s/subagents/*.jsonl" % sid))
    workers = {}
    for f in sub_files:
        merge_usage(workers, claude_usage(load(f)))
    worktree = sum(1 for d in delegations if d["isolation"] == "worktree")
    partial = worktree > 0 and len(sub_files) < len(delegations)
    return {
        "runtime": "claude",
        "start": start,
        "project": cwd or path.parent.name,
        "session": sid[:8],
        "delegations": delegations,
        "announced": sum(d["announced"] for d in delegations),
        "tokens": {"main": claude_usage(rows), "workers": workers,
                   "workers_partial": partial, "worker_files": len(sub_files)},
        "main_writes": writes,
    }


def written_lines(name, inp):
    if name == "Write":
        return len((inp.get("content") or "").splitlines())
    if name == "Edit":
        return len((inp.get("new_string") or "").splitlines())
    return sum(len((e.get("new_string") or "").splitlines())
               for e in inp.get("edits") or [] if isinstance(e, dict))


def claude_sessions(root):
    for path in sorted(root.glob("*/*.jsonl")):
        try:
            res = claude_session(path, root)
        except Exception as exc:  # log mal formado nao deve derrubar o relatorio
            print("aviso: %s: %s" % (path.name, exc), file=sys.stderr)
            continue
        if res:
            yield res


# ----------------------------------------------------------------- Codex

def codex_parse(path):
    rows = load(path)
    if not rows or rows[0].get("type") != "session_meta":
        return None
    meta = rows[0].get("payload") or {}
    s = {"id": meta.get("id") or path.stem, "cwd": meta.get("cwd"),
         "start": meta.get("timestamp") or rows[0].get("timestamp"),
         "parent": meta.get("parent_thread_id"), "nick": meta.get("agent_nickname"),
         "model": None, "effort": None, "tokens": {}, "used": False,
         "delegations": []}
    pending = []
    for row in rows:
        p = row.get("payload") or {}
        typ, ptype = row.get("type"), p.get("type")
        if typ == "turn_context":
            s["model"] = p.get("model") or s["model"]
            s["effort"] = p.get("effort") or s["effort"]
        elif typ == "event_msg" and ptype == "token_count":
            usage = (p.get("info") or {}).get("total_token_usage")
            if usage:
                s["tokens"] = usage
        elif typ == "response_item" and ptype == "message":
            content = p.get("content") or []
            text = content if isinstance(content, str) else "\n".join(
                x.get("text", "") for x in content if isinstance(x, dict))
            if p.get("role") == "user":
                if SKILL in text:
                    s["used"] = True
                if not text.lstrip().startswith(("<", "# AGENTS")):
                    pending = []
            elif p.get("role") == "assistant":
                pending.append(text)
        elif typ == "response_item" and ptype in ("function_call", "custom_tool_call"):
            raw = p.get("arguments") or p.get("input") or ""
            if not isinstance(raw, str):
                raw = json.dumps(raw)
            if SKILL + "/SKILL.md" in raw:
                s["used"] = True
            if p.get("name") in ("spawn_agent", "followup_task"):
                try:
                    args = json.loads(raw)
                except ValueError:
                    args = {}
                name = args.get("task_name") or args.get("target")
                s["delegations"].append({
                    "kind": "spawn" if p["name"] == "spawn_agent" else "followup",
                    "agent": name,
                    "model": args.get("model"),
                    "effort": args.get("reasoning_effort"),
                    "announced": announced(pending, [args.get("model"), name]),
                })
    return s


def codex_sessions(root):
    parsed = []
    for path in sorted(root.rglob("rollout-*.jsonl")):
        try:
            s = codex_parse(path)
        except Exception as exc:
            print("aviso: %s: %s" % (path.name, exc), file=sys.stderr)
            continue
        if s:
            parsed.append(s)
    kids = collections.defaultdict(list)
    for s in parsed:
        if s["parent"]:
            kids[s["parent"]].append(s)
    for s in parsed:
        children = kids.get(s["id"], [])
        if s["parent"] or not (s["used"] or any(c["used"] for c in children)):
            continue
        workers = [c for c in children if c["model"] != REVIEWER_MODEL]
        reviewers = [c for c in children if c["model"] == REVIEWER_MODEL]
        followups = collections.Counter(
            d["agent"] for d in s["delegations"] if d["kind"] == "followup")
        yield {
            "runtime": "codex",
            "start": s["start"],
            "project": s["cwd"],
            "session": s["id"][:8],
            "model": s["model"],
            "delegations": s["delegations"],
            "announced": sum(d["announced"] for d in s["delegations"]),
            "followups_per_worker": dict(followups),
            "tokens": {"main": codex_tokens([s]), "workers": codex_tokens(workers),
                       "auto_review": codex_tokens(reviewers),
                       "worker_count": len(workers), "review_count": len(reviewers)},
        }


def codex_tokens(sessions):
    total = {"total_tokens": 0, "output_tokens": 0}
    for s in sessions:
        for k in total:
            total[k] += s["tokens"].get(k, 0) or 0
    return total


# ---------------------------------------------------------------- saida

def collect(args):
    out = []
    if args.runtime in ("claude", "all"):
        out += claude_sessions(pathlib.Path(args.claude_root).expanduser())
    if args.runtime in ("codex", "all"):
        out += codex_sessions(pathlib.Path(args.codex_root).expanduser())
    if args.since:
        out = [s for s in out if day(s["start"]) >= args.since]
    if args.session:
        out = [s for s in out if s["session"].startswith(args.session[:8])]
    return sorted(out, key=lambda s: s["start"] or "")


def fmt_usage(usage):
    if not usage:
        return "-"
    return ", ".join("%s out=%d in=%d" % (m, v["output"], v["input"])
                     for m, v in sorted(usage.items()))


def render(s):
    lines = ["%s  %s  %s  [%s]" % (s["runtime"], (s["start"] or "?")[:19],
                                   s["project"], s["session"])]
    n = len(s["delegations"])
    lines.append("  delegacoes: %d  anuncios encontrados: %d/%d" % (n, s["announced"], n))
    for d in s["delegations"]:
        kind = d.get("kind") or ("bg" if d.get("background") else "agent")
        extra = " worktree" if d.get("isolation") == "worktree" else ""
        lines.append("    - %s %s model=%s effort=%s anuncio=%s%s" % (
            kind, d["agent"], d["model"], d["effort"],
            "sim" if d["announced"] else "nao encontrado", extra))
    t = s["tokens"]
    if s["runtime"] == "claude":
        lines.append("  tokens main:    " + fmt_usage(t["main"]))
        mark = " (parcial)" if t["workers_partial"] else ""
        lines.append("  tokens workers: %s%s" % (fmt_usage(t["workers"]), mark))
        w = s["main_writes"]
        lines.append("  escritas da main: %d chamadas, %d linhas" % (w["calls"], w["lines"]))
    else:
        for label, key in (("main", "main"), ("workers", "workers"),
                           ("auto-review", "auto_review")):
            lines.append("  tokens %s: total=%d output=%d" % (
                label, t[key]["total_tokens"], t[key]["output_tokens"]))
        if s["followups_per_worker"]:
            lines.append("  followups por worker: " + ", ".join(
                "%s=%d" % kv for kv in sorted(s["followups_per_worker"].items())))
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Uso da skill cost-aware-delegation")
    ap.add_argument("--runtime", choices=("claude", "codex", "all"), default="all")
    ap.add_argument("--since", help="YYYY-MM-DD")
    ap.add_argument("--session", help="prefixo do id da sessao")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--claude-root", default="~/.claude/projects")
    ap.add_argument("--codex-root", default="~/.codex/sessions")
    args = ap.parse_args(argv)
    sessions = collect(args)
    if args.json:
        print(json.dumps(sessions, ensure_ascii=False, indent=2))
    elif sessions:
        print("\n\n".join(render(s) for s in sessions))
    else:
        print("Nenhuma sessao com a skill encontrada.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
