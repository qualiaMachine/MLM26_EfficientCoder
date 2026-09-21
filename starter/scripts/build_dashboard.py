#!/usr/bin/env python3
"""Build a self-contained HTML dashboard for a Harbor job directory.

Reads a job directory produced by `harbor run` (e.g. `jobs/2026-09-12__21-32-36/`)
and renders every trial's `result.json` -- including the full agent conversation
in `agent_result.metadata.messages` -- into one static HTML file with no external
dependencies, so it can be opened directly via `file://`.

This is a local-only dev tool: transcripts can contain anything the agent `cat`'d
inside the container (see starter/docs/safety.md), so the output is never
uploaded or published anywhere -- just written next to the job data.

Usage
=====
    python starter/scripts/build_dashboard.py jobs/2026-09-12__21-32-36
    python starter/scripts/build_dashboard.py jobs/2026-09-12__21-32-36 -o /tmp/out.html --open
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import webbrowser
from datetime import datetime
from pathlib import Path
from typing import Any

# Mirrors starter/agent/tools.py::CODE_BLOCK_RE
CODE_BLOCK_RE = re.compile(r"```(?:bash|sh|shell)?\s*\n(.*?)```", re.DOTALL)

# Mirrors starter/agent/prompts.py::NUDGE_MESSAGE
NUDGE_MESSAGE = (
    "Your last response contained no action. Respond with exactly one bash code "
    "block to run a command, or TASK_COMPLETE on its own if the task is fully done."
)

OBSERVATION_PREFIX = "Command output:\n"
OBSERVATION_SUFFIX = "\n\nWhat is your next action?"


def parse_iso(ts: str | None) -> datetime | None:
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except ValueError:
        return None


def duration_sec(started_at: str | None, finished_at: str | None) -> float | None:
    start, end = parse_iso(started_at), parse_iso(finished_at)
    if start is None or end is None:
        return None
    return (end - start).total_seconds()


def parse_observation(body: str) -> dict[str, Any]:
    """Split a run_shell()-formatted observation string into its parts."""
    exit_code = None
    stdout = None
    stderr = None

    m = re.search(r"^exit code: (-?\d+)", body)
    if m:
        exit_code = int(m.group(1))

    stdout_idx = body.find("stdout:\n")
    stderr_idx = body.find("stderr:\n")
    if stdout_idx != -1:
        end = stderr_idx if stderr_idx != -1 else len(body)
        stdout = body[stdout_idx + len("stdout:\n") : end].rstrip("\n")
    if stderr_idx != -1:
        stderr = body[stderr_idx + len("stderr:\n") :].rstrip("\n")

    return {"exit_code": exit_code, "stdout": stdout, "stderr": stderr, "raw": body}


def classify_messages(messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Turn the flat OpenAI-format message list into render-ready turn records."""
    turns: list[dict[str, Any]] = []
    seen_task = False

    for msg in messages:
        role = msg.get("role")
        content = msg.get("content") or ""

        if role == "system":
            turns.append({"kind": "system", "text": content})
            continue

        if role == "assistant":
            match = CODE_BLOCK_RE.search(content)
            command = match.group(1).strip() if match else None
            prose = content[: match.start()].strip() if match else content.strip()
            turns.append({"kind": "assistant", "text": prose, "command": command})
            continue

        if role == "user":
            if not seen_task:
                seen_task = True
                turns.append({"kind": "task", "text": content})
                continue

            if content == NUDGE_MESSAGE:
                turns.append({"kind": "nudge", "text": content})
                continue

            if content.startswith(OBSERVATION_PREFIX):
                body = content[len(OBSERVATION_PREFIX) :]
                if body.endswith(OBSERVATION_SUFFIX):
                    body = body[: -len(OBSERVATION_SUFFIX)]
                turns.append({"kind": "observation", **parse_observation(body)})
                continue

            turns.append({"kind": "other", "role": role, "text": content})
            continue

        turns.append({"kind": "other", "role": role, "text": content})

    return turns


def build_trial_record(task_name: str, trial_name: str, data: dict[str, Any]) -> dict[str, Any]:
    agent_result = data.get("agent_result") or {}
    metadata = agent_result.get("metadata") or {}
    messages = metadata.get("messages") or []
    verifier_result = data.get("verifier_result") or {}
    reward = (verifier_result.get("rewards") or {}).get("reward")
    exception_info = data.get("exception_info")

    timing = {
        block: duration_sec(
            ((data.get(block) or {}).get("started_at")),
            ((data.get(block) or {}).get("finished_at")),
        )
        for block in ("environment_setup", "agent_setup", "agent_execution", "verifier")
    }

    return {
        "status": "ok",
        "task_name": task_name,
        "trial_name": trial_name,
        "reward": reward,
        "passed": reward is not None and reward >= 1.0,
        "finished": metadata.get("finished", False),
        "turns_count": metadata.get("turns"),
        "n_input_tokens": agent_result.get("n_input_tokens"),
        "n_output_tokens": agent_result.get("n_output_tokens"),
        "n_cache_tokens": agent_result.get("n_cache_tokens"),
        "cost_usd": agent_result.get("cost_usd"),
        "exception_type": (exception_info or {}).get("exception_type"),
        "exception_message": (exception_info or {}).get("exception_message"),
        "exception_traceback": (exception_info or {}).get("exception_traceback"),
        "total_duration_sec": duration_sec(data.get("started_at"), data.get("finished_at")),
        "timing": timing,
        "turns": classify_messages(messages),
    }


def load_job(job_dir: Path) -> dict[str, Any]:
    job_result_path = job_dir / "result.json"
    if not job_result_path.exists():
        print(f"warning: no job-level result.json at {job_result_path}", file=sys.stderr)
        job_result = {}
    else:
        job_result = json.loads(job_result_path.read_text())

    trials: list[dict[str, Any]] = []
    for trial_dir in sorted(p for p in job_dir.iterdir() if p.is_dir()):
        if "__" not in trial_dir.name:
            continue
        task_name = trial_dir.name.split("__", 1)[0]
        result_path = trial_dir / "result.json"
        if not result_path.exists():
            trials.append(
                {
                    "status": "no_result",
                    "task_name": task_name,
                    "trial_name": trial_dir.name,
                }
            )
            continue
        try:
            data = json.loads(result_path.read_text())
        except json.JSONDecodeError as exc:
            print(f"warning: could not parse {result_path}: {exc}", file=sys.stderr)
            trials.append(
                {
                    "status": "no_result",
                    "task_name": task_name,
                    "trial_name": trial_dir.name,
                }
            )
            continue
        trials.append(build_trial_record(task_name, trial_dir.name, data))

    if not trials:
        raise SystemExit(f"error: no trial directories with result.json found under {job_dir}")

    return {"job_name": job_dir.name, "job": job_result, "trials": trials}


PAGE_TEMPLATE = """<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>Harbor Dashboard - {job_name}</title>
<style>
{css}
</style>
</head>
<body>
<div id="app"></div>
<script>
const DATA = {data_json};
{js}
</script>
</body>
</html>
"""

CSS = """
:root {
  color-scheme: light dark;
  --bg: #f7f7f8; --panel: #ffffff; --border: #ddd; --text: #1a1a1a; --muted: #666;
  --accent: #2563eb; --ok: #16a34a; --fail: #dc2626; --warn: #d97706;
  --term-bg: #1e1e1e; --term-fg: #e6e6e6; --action-bg: #eef2ff;
}
@media (prefers-color-scheme: dark) {
  :root { --bg: #16171a; --panel: #1f2023; --border: #333; --text: #eaeaea; --muted: #999;
    --action-bg: #22263a; }
}
[data-theme="dark"] { --bg: #16171a; --panel: #1f2023; --border: #333; --text: #eaeaea; --muted: #999;
  --action-bg: #22263a; }
[data-theme="light"] { --bg: #f7f7f8; --panel: #ffffff; --border: #ddd; --text: #1a1a1a; --muted: #666;
  --action-bg: #eef2ff; }

* { box-sizing: border-box; }
body { margin: 0; background: var(--bg); color: var(--text); font: 14px/1.5 -apple-system, system-ui, sans-serif; }
#app { display: flex; flex-direction: column; height: 100vh; }

header.top { padding: 10px 16px; border-bottom: 1px solid var(--border); background: var(--panel);
  display: flex; flex-wrap: wrap; gap: 8px 20px; align-items: center; }
header.top h1 { font-size: 15px; margin: 0; flex: 1 1 auto; }
.stat { font-size: 12px; color: var(--muted); }
.stat b { color: var(--text); }
.badge { display: inline-block; padding: 1px 7px; border-radius: 10px; font-size: 11px; font-weight: 600; }
.badge.ok { background: rgba(22,163,74,.15); color: var(--ok); }
.badge.fail { background: rgba(220,38,38,.15); color: var(--fail); }
.badge.warn { background: rgba(217,119,6,.15); color: var(--warn); }
button.themeToggle { border: 1px solid var(--border); background: var(--panel); color: var(--text);
  border-radius: 6px; padding: 4px 10px; cursor: pointer; font-size: 12px; }

.body { flex: 1; display: flex; min-height: 0; }
aside { width: 300px; border-right: 1px solid var(--border); background: var(--panel);
  display: flex; flex-direction: column; }
aside .filters { padding: 8px; border-bottom: 1px solid var(--border); display: flex; gap: 6px; }
aside input[type=text] { flex: 1; padding: 5px 8px; border: 1px solid var(--border); border-radius: 6px;
  background: var(--bg); color: var(--text); font-size: 12px; }
aside select { border: 1px solid var(--border); border-radius: 6px; background: var(--bg); color: var(--text); font-size: 12px; }
ul.trialList { list-style: none; margin: 0; padding: 0; overflow-y: auto; flex: 1; }
ul.trialList li { padding: 8px 12px; border-bottom: 1px solid var(--border); cursor: pointer; }
ul.trialList li:hover { background: var(--bg); }
ul.trialList li.selected { background: var(--action-bg); }
ul.trialList li.disabled { opacity: .5; cursor: default; }
.trialName { font-weight: 600; font-size: 12.5px; }
.trialMeta { font-size: 11px; color: var(--muted); margin-top: 2px; display: flex; gap: 8px; flex-wrap: wrap; }

main { flex: 1; overflow-y: auto; padding: 16px 20px; }
.placeholder { color: var(--muted); padding: 40px; text-align: center; }

.cards { display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 16px; }
.card { border: 1px solid var(--border); background: var(--panel); border-radius: 8px;
  padding: 8px 12px; min-width: 100px; }
.card .k { font-size: 10.5px; text-transform: uppercase; color: var(--muted); letter-spacing: .03em; }
.card .v { font-size: 15px; font-weight: 600; margin-top: 2px; }

.exceptionBox { border: 1px solid var(--fail); background: rgba(220,38,38,.06); border-radius: 8px;
  padding: 10px 12px; margin-bottom: 16px; }
.exceptionBox summary { cursor: pointer; font-weight: 600; color: var(--fail); }
.exceptionBox pre { white-space: pre-wrap; font-size: 11.5px; margin-top: 8px; }

.searchBar { margin-bottom: 12px; display: flex; gap: 8px; }
.searchBar input { flex: 1; padding: 7px 10px; border: 1px solid var(--border); border-radius: 6px;
  background: var(--panel); color: var(--text); font-size: 13px; }
.exportBtn { border: 1px solid var(--border); background: var(--panel); color: var(--text);
  border-radius: 6px; padding: 0 12px; cursor: pointer; font-size: 12.5px; white-space: nowrap; }
.exportBtn:hover { background: var(--action-bg); border-color: var(--accent); }

.turn { margin-bottom: 10px; border-radius: 8px; overflow: hidden; }
.turn.system, .turn.task { border: 1px solid var(--border); background: var(--panel); }
.turn.system summary, .turn.task .label { padding: 8px 12px; font-weight: 600; font-size: 12px; color: var(--muted); }
.turn.task .label { border-bottom: 1px solid var(--border); }
.turn.system pre, .turn.task .content { white-space: pre-wrap; padding: 10px 12px; font-size: 12.5px; margin: 0; }
.turn.assistant .prose { padding: 8px 2px; white-space: pre-wrap; font-size: 13px; }
.turn.assistant .action { background: var(--action-bg); border: 1px solid var(--accent);
  border-radius: 6px; padding: 8px 10px; font-family: ui-monospace, monospace; font-size: 12.5px;
  white-space: pre-wrap; }
.turn.assistant .action::before { content: "$ "; color: var(--accent); font-weight: 700; }
.turn.observation { background: var(--term-bg); color: var(--term-fg); border-radius: 8px; padding: 8px 12px; }
.turn.observation .obsHead { display: flex; gap: 8px; align-items: center; margin-bottom: 6px; font-size: 11px; }
.turn.observation pre { white-space: pre-wrap; font-family: ui-monospace, monospace; font-size: 12px; margin: 4px 0; }
.turn.observation .label { color: #9ca3af; font-size: 10.5px; text-transform: uppercase; }
.turn.nudge { color: var(--warn); font-size: 11.5px; font-style: italic; padding: 4px 12px; }
.turn.other { padding: 8px 12px; border: 1px dashed var(--border); font-size: 12.5px; white-space: pre-wrap; }

.showMore { color: var(--accent); cursor: pointer; font-size: 11.5px; margin-top: 4px; display: inline-block; }
mark { background: #fde047; color: #1a1a1a; }
"""

JS = r"""
(function () {
  const state = { selected: null, search: "", filter: "all", nameFilter: "" };

  function esc(s) {
    return (s ?? "").replace(/[&<>]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;"}[c]));
  }

  function highlight(text) {
    const q = state.search.trim();
    const safe = esc(text);
    if (!q) return safe;
    try {
      const re = new RegExp(q.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"), "gi");
      return safe.replace(re, m => `<mark>${m}</mark>`);
    } catch (e) { return safe; }
  }

  function fmtNum(n) {
    return (n === null || n === undefined) ? "-" : n.toLocaleString();
  }
  function fmtSec(n) {
    return (n === null || n === undefined) ? "-" : n.toFixed(1) + "s";
  }

  function jobStats() {
    const trials = DATA.trials.filter(t => t.status === "ok");
    const passed = trials.filter(t => t.passed).length;
    const rewards = trials.map(t => t.reward).filter(r => r !== null && r !== undefined);
    const meanReward = rewards.length ? (rewards.reduce((a,b)=>a+b,0)/rewards.length) : null;
    const totalIn = trials.reduce((a,t)=>a+(t.n_input_tokens||0),0);
    const totalOut = trials.reduce((a,t)=>a+(t.n_output_tokens||0),0);
    const excCounts = {};
    trials.forEach(t => { if (t.exception_type) excCounts[t.exception_type] = (excCounts[t.exception_type]||0)+1; });
    return { total: trials.length, passed, meanReward, totalIn, totalOut, excCounts };
  }

  function renderHeader() {
    const s = jobStats();
    const excBadges = Object.entries(s.excCounts)
      .map(([k,v]) => `<span class="badge fail">${esc(k)}: ${v}</span>`).join(" ");
    return `
      <h1>${esc(DATA.job_name)}</h1>
      <div class="stat">pass rate: <b>${s.total ? Math.round(100*s.passed/s.total) : 0}%</b> (${s.passed}/${s.total})</div>
      <div class="stat">mean reward: <b>${s.meanReward === null ? "-" : s.meanReward.toFixed(2)}</b></div>
      <div class="stat">tokens in/out: <b>${fmtNum(s.totalIn)} / ${fmtNum(s.totalOut)}</b></div>
      ${excBadges}
      <button class="themeToggle" id="themeToggle">theme</button>
    `;
  }

  function trialBadge(t) {
    if (t.status !== "ok") return '<span class="badge warn">no result</span>';
    if (t.exception_type) return `<span class="badge fail">${esc(t.exception_type)}</span>`;
    return t.passed ? '<span class="badge ok">pass</span>' : '<span class="badge fail">fail</span>';
  }

  function matchesFilter(t) {
    if (state.nameFilter && !t.task_name.toLowerCase().includes(state.nameFilter.toLowerCase())) return false;
    if (state.filter === "all") return true;
    if (state.filter === "passed") return t.status === "ok" && t.passed;
    if (state.filter === "failed") return t.status === "ok" && !t.passed && !t.exception_type;
    if (state.filter === "errored") return t.status === "ok" && !!t.exception_type;
    if (state.filter === "no_result") return t.status === "no_result";
    return true;
  }

  function renderSidebar() {
    const items = DATA.trials.filter(matchesFilter).map((t, i) => {
      const idx = DATA.trials.indexOf(t);
      const disabled = t.status !== "ok";
      const sel = idx === state.selected ? "selected" : "";
      const tokens = t.status === "ok" ? `${fmtNum(t.n_input_tokens)} / ${fmtNum(t.n_output_tokens)} tok` : "";
      return `<li class="${disabled ? "disabled" : ""} ${sel}" data-idx="${idx}">
        <div class="trialName">${esc(t.task_name)}</div>
        <div class="trialMeta">${trialBadge(t)} <span>${tokens}</span></div>
      </li>`;
    }).join("");
    return `
      <div class="filters">
        <input type="text" id="nameFilter" placeholder="filter task name..." value="${esc(state.nameFilter)}">
        <select id="statusFilter">
          <option value="all">all</option>
          <option value="passed">passed</option>
          <option value="failed">failed</option>
          <option value="errored">errored</option>
          <option value="no_result">no result</option>
        </select>
      </div>
      <ul class="trialList">${items}</ul>
    `;
  }

  function renderCards(t) {
    const rows = [
      ["reward", t.reward === null || t.reward === undefined ? "-" : t.reward],
      ["finished", t.finished ? "yes" : "no"],
      ["turns", fmtNum(t.turns_count)],
      ["input tok", fmtNum(t.n_input_tokens)],
      ["output tok", fmtNum(t.n_output_tokens)],
      ["cache tok", fmtNum(t.n_cache_tokens)],
      ["cost usd", t.cost_usd === null || t.cost_usd === undefined ? "-" : t.cost_usd],
      ["duration", fmtSec(t.total_duration_sec)],
      ["agent exec", fmtSec(t.timing && t.timing.agent_execution)],
    ];
    return `<div class="cards">${rows.map(([k,v]) =>
      `<div class="card"><div class="k">${k}</div><div class="v">${esc(String(v))}</div></div>`).join("")}</div>`;
  }

  function renderException(t) {
    if (!t.exception_type) return "";
    return `<details class="exceptionBox" open>
      <summary>${esc(t.exception_type)}: ${esc(t.exception_message || "")}</summary>
      <pre>${esc(t.exception_traceback || "")}</pre>
    </details>`;
  }

  function truncated(text, limit) {
    if (!text) return { shown: "", isTruncated: false };
    const lines = text.split("\n");
    if (lines.length <= limit) return { shown: text, isTruncated: false };
    return { shown: lines.slice(0, limit).join("\n"), isTruncated: true, full: text };
  }

  function renderTurn(turn, i) {
    if (turn.kind === "system") {
      return `<details class="turn system"><summary>System prompt</summary><pre>${highlight(turn.text)}</pre></details>`;
    }
    if (turn.kind === "task") {
      return `<div class="turn task"><div class="label">Task instruction</div><div class="content">${highlight(turn.text)}</div></div>`;
    }
    if (turn.kind === "nudge") {
      return `<div class="turn nudge">protocol nudge: no action found in previous response</div>`;
    }
    if (turn.kind === "assistant") {
      const prose = turn.text ? `<div class="prose">${highlight(turn.text)}</div>` : "";
      const action = turn.command ? `<div class="action">${highlight(turn.command)}</div>` : "";
      return `<div class="turn assistant">${prose}${action}</div>`;
    }
    if (turn.kind === "observation") {
      const codeBadge = turn.exit_code === 0
        ? '<span class="badge ok">exit 0</span>'
        : `<span class="badge fail">exit ${esc(String(turn.exit_code ?? "?"))}</span>`;
      const parts = [];
      if (turn.stdout) {
        const tr = truncated(turn.stdout, 20);
        parts.push(`<div class="label">stdout</div><pre id="obs-out-${i}">${highlight(tr.shown)}</pre>${
          tr.isTruncated ? `<span class="showMore" data-full-id="obs-out-${i}">show more</span>` : ""}`);
        if (tr.isTruncated) window.__full = window.__full || {}, window.__full[`obs-out-${i}`] = tr.full;
      }
      if (turn.stderr) {
        const tr = truncated(turn.stderr, 20);
        parts.push(`<div class="label">stderr</div><pre id="obs-err-${i}">${highlight(tr.shown)}</pre>${
          tr.isTruncated ? `<span class="showMore" data-full-id="obs-err-${i}">show more</span>` : ""}`);
        if (tr.isTruncated) window.__full = window.__full || {}, window.__full[`obs-err-${i}`] = tr.full;
      }
      if (!turn.stdout && !turn.stderr) parts.push(`<pre>(no output)</pre>`);
      return `<div class="turn observation"><div class="obsHead">${codeBadge}</div>${parts.join("")}</div>`;
    }
    return `<div class="turn other">${highlight(turn.text || "")}</div>`;
  }

  function safeFilename(t, ext) {
    return `${t.trial_name}`.replace(/[^A-Za-z0-9._-]/g, "_") + "." + ext;
  }

  function conversationToText(t, format) {
    const isMd = format === "md";
    const fence = (body, lang) => isMd ? "```" + (lang || "") + "\n" + body + "\n```" : body;
    const h = (level, text) => isMd ? `${"#".repeat(level)} ${text}` : `${text}\n${"=".repeat(text.length)}`;
    const lines = [];

    lines.push(h(1, `Conversation: ${t.task_name} (${t.trial_name})`));
    lines.push("");
    const meta = [
      `Reward: ${t.reward === null || t.reward === undefined ? "-" : t.reward}`,
      `Turns: ${t.turns_count ?? "-"}`,
      `Finished: ${t.finished}`,
      `Tokens in/out: ${t.n_input_tokens ?? "-"}/${t.n_output_tokens ?? "-"}`,
    ];
    if (t.exception_type) meta.push(`Exception: ${t.exception_type}`);
    lines.push(meta.join(" | "));
    lines.push("");

    let turnNum = 0;
    t.turns.forEach(turn => {
      if (turn.kind === "system") {
        lines.push(h(2, "System Prompt"));
        lines.push(fence(turn.text || ""));
        lines.push("");
      } else if (turn.kind === "task") {
        lines.push(h(2, "Task Instruction"));
        lines.push(turn.text || "");
        lines.push("");
      } else if (turn.kind === "assistant") {
        turnNum += 1;
        lines.push(h(2, `Turn ${turnNum} — Assistant`));
        if (turn.text) { lines.push(turn.text); lines.push(""); }
        if (turn.command) {
          lines.push(isMd ? "Command:" : "Command:");
          lines.push(fence(turn.command, "bash"));
          lines.push("");
        }
      } else if (turn.kind === "observation") {
        lines.push(h(3, `Turn ${turnNum} — Command Output (exit code ${turn.exit_code === null || turn.exit_code === undefined ? "?" : turn.exit_code})`));
        if (turn.stdout) { lines.push("stdout:"); lines.push(fence(turn.stdout)); }
        if (turn.stderr) { lines.push("stderr:"); lines.push(fence(turn.stderr)); }
        if (!turn.stdout && !turn.stderr) lines.push("(no output)");
        lines.push("");
      } else if (turn.kind === "nudge") {
        lines.push("[protocol nudge: no action found in previous response]");
        lines.push("");
      } else {
        lines.push(h(3, `Turn (role: ${turn.role || turn.kind})`));
        lines.push(turn.text || "");
        lines.push("");
      }
    });

    if (t.exception_type) {
      lines.push(h(2, "Exception"));
      lines.push(`${t.exception_type}: ${t.exception_message || ""}`);
      lines.push(fence(t.exception_traceback || ""));
      lines.push("");
    }

    return lines.join("\n");
  }

  function downloadText(filename, text) {
    const blob = new Blob([text], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }

  function renderMain() {
    if (state.selected === null) return `<div class="placeholder">Select a trial from the left to view its conversation.</div>`;
    const t = DATA.trials[state.selected];
    if (t.status !== "ok") return `<div class="placeholder">No result.json for this trial (still running or crashed before writing results).</div>`;
    const turnsHtml = t.turns.map(renderTurn).join("");
    return `
      <div class="searchBar">
        <input type="text" id="searchBox" placeholder="search conversation..." value="${esc(state.search)}">
        <button class="exportBtn" id="exportMd">Export .md</button>
        <button class="exportBtn" id="exportTxt">Export .txt</button>
      </div>
      ${renderCards(t)}
      ${renderException(t)}
      ${turnsHtml}
    `;
  }

  function render() {
    document.querySelector("header.top").innerHTML = renderHeader();
    document.querySelector("aside").innerHTML = renderSidebar();
    document.querySelector("main").innerHTML = renderMain();
    bind();
  }

  function bind() {
    document.getElementById("themeToggle").onclick = () => {
      const root = document.documentElement;
      let prefersDark = false;
      try { prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches; } catch (e) {}
      const current = root.getAttribute("data-theme") || (prefersDark ? "dark" : "light");
      const next = current === "dark" ? "light" : "dark";
      root.setAttribute("data-theme", next);
      try { localStorage.setItem("dashboardTheme", next); } catch (e) {}
    };
    document.querySelectorAll("ul.trialList li:not(.disabled)").forEach(li => {
      li.onclick = () => { state.selected = parseInt(li.dataset.idx, 10); render(); };
    });
    const nameFilter = document.getElementById("nameFilter");
    if (nameFilter) nameFilter.oninput = (e) => { state.nameFilter = e.target.value; render(); nameFilter.focus(); nameFilter.setSelectionRange(nameFilter.value.length, nameFilter.value.length); };
    const statusFilter = document.getElementById("statusFilter");
    if (statusFilter) { statusFilter.value = state.filter; statusFilter.onchange = (e) => { state.filter = e.target.value; render(); }; }
    const searchBox = document.getElementById("searchBox");
    if (searchBox) searchBox.oninput = (e) => { state.search = e.target.value; render(); searchBox.focus(); searchBox.setSelectionRange(searchBox.value.length, searchBox.value.length); };
    const exportMd = document.getElementById("exportMd");
    if (exportMd) exportMd.onclick = () => {
      const t = DATA.trials[state.selected];
      downloadText(safeFilename(t, "md"), conversationToText(t, "md"));
    };
    const exportTxt = document.getElementById("exportTxt");
    if (exportTxt) exportTxt.onclick = () => {
      const t = DATA.trials[state.selected];
      downloadText(safeFilename(t, "txt"), conversationToText(t, "txt"));
    };
    document.querySelectorAll(".showMore").forEach(el => {
      el.onclick = () => {
        const id = el.dataset.fullId;
        const full = (window.__full || {})[id];
        if (full !== undefined) {
          document.getElementById(id).innerHTML = highlight(full);
          el.remove();
        }
      };
    });
  }

  try {
    const savedTheme = localStorage.getItem("dashboardTheme");
    if (savedTheme) document.documentElement.setAttribute("data-theme", savedTheme);
  } catch (e) {}

  document.getElementById("app").innerHTML = `
    <header class="top"></header>
    <div class="body"><aside></aside><main></main></div>
  `;
  render();
})();
"""


def render_html(payload: dict[str, Any]) -> str:
    data_json = json.dumps(payload).replace("</script>", "<\\/script>")
    return PAGE_TEMPLATE.format(
        job_name=payload["job_name"], css=CSS, data_json=data_json, js=JS
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("job_dir", type=Path, help="Path to a harbor job directory")
    parser.add_argument("-o", "--output", type=Path, default=None, help="Output HTML path")
    parser.add_argument("--open", action="store_true", help="Open the dashboard in a browser")
    args = parser.parse_args()

    job_dir = args.job_dir
    if not job_dir.exists() or not job_dir.is_dir():
        raise SystemExit(f"error: job directory not found: {job_dir}")

    payload = load_job(job_dir)
    output = args.output or (job_dir / "dashboard.html")
    output.write_text(render_html(payload))
    print(f"wrote {output}")

    if args.open:
        webbrowser.open(output.resolve().as_uri())


if __name__ == "__main__":
    main()
