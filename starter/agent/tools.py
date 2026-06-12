"""Action parsing and execution against the Harbor task environment.

The baseline protocol is deliberately simple so small local models can follow
it: the model emits one fenced bash block per turn, or TASK_COMPLETE when
finished. Everything else (file reads, writes, edits) happens through shell
commands inside that block.
"""

import re
from dataclasses import dataclass

from harbor.environments.base import BaseEnvironment

CODE_BLOCK_RE = re.compile(r"```(?:bash|sh|shell)?\s*\n(.*?)```", re.DOTALL)
DONE_MARKER = "TASK_COMPLETE"

# Keep observations bounded so long outputs don't blow the context window.
MAX_OBSERVATION_CHARS = 6000


@dataclass
class Action:
    kind: str  # "shell" | "done" | "none"
    command: str = ""


def parse_action(text: str) -> Action:
    """Extract the action from a model response.

    A code block wins over a stray DONE_MARKER mention, so the model can't
    accidentally terminate by talking about finishing.
    """
    match = CODE_BLOCK_RE.search(text)
    if match:
        command = match.group(1).strip()
        if command:
            return Action("shell", command)
    if DONE_MARKER in text:
        return Action("done")
    return Action("none")


def _truncate(text: str) -> str:
    if len(text) <= MAX_OBSERVATION_CHARS:
        return text
    half = MAX_OBSERVATION_CHARS // 2
    omitted = len(text) - MAX_OBSERVATION_CHARS
    return f"{text[:half]}\n... [{omitted} characters omitted] ...\n{text[-half:]}"


async def run_shell(
    environment: BaseEnvironment, command: str, timeout_sec: int
) -> str:
    """Execute a command in the task container and format the result."""
    try:
        result = await environment.exec(command=command, timeout_sec=timeout_sec)
    except Exception as exc:  # timeout, container error, etc.
        return f"[command did not complete: {exc}]"

    parts = [f"exit code: {result.return_code}"]
    if result.stdout:
        parts.append(f"stdout:\n{_truncate(result.stdout)}")
    if result.stderr:
        parts.append(f"stderr:\n{_truncate(result.stderr)}")
    if not result.stdout and not result.stderr:
        parts.append("(no output)")
    return "\n".join(parts)
