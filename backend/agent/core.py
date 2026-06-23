"""DEPRECATED for review flow — use PiRpcAgent from pi_rpc.py instead.
Kept for extract pipeline in files.py.
Original: Agent loop that gives an LLM read/write/edit tools via native function calling."""

import json
import time
from pathlib import Path
from typing import Optional

from backend.llm import LLMProvider
import logging
logger = logging.getLogger(__name__)


# ── Tool definitions (OpenAI tool-calling format) ────────────────────

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read",
            "description": "Read the full contents of a file at the given path.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Relative path from work directory"},
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "edit",
            "description": "Replace the first occurrence of old_text with new_text in a file. Errors if old_text not found.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Relative path from work directory"},
                    "old_text": {"type": "string", "description": "Exact text to find"},
                    "new_text": {"type": "string", "description": "Replacement text"},
                },
                "required": ["path", "old_text", "new_text"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write",
            "description": "Create or overwrite a file at the given path.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Relative path from work directory"},
                    "content": {"type": "string", "description": "Full file content to write"},
                },
                "required": ["path", "content"],
            },
        },
    },
]


# ── Tool execution ──────────────────────────────────────────────────

def _resolve_path(work_dir: Path, raw_path: str) -> Path:
    path = (work_dir / raw_path).resolve()
    if not str(path).startswith(str(work_dir.resolve())):
        raise PermissionError(f"Path escapes work directory: {raw_path}")
    return path


def execute_tool(tool_name: str, args: dict, work_dir: Path) -> str:
    """Execute a tool and return the result string to feed back to the LLM."""
    raw_path = args.get("path", "")
    if not raw_path:
        return f"ERROR: empty path for {tool_name} (args keys: {list(args.keys())})"
    try:
        path = _resolve_path(work_dir, raw_path)
    except PermissionError as e:
        return f"ERROR: {e}"

    if path.is_dir():
        return f"ERROR: {tool_name} called on a directory: {raw_path}"
    if tool_name == "read":
        if not path.exists():
            return f"ERROR: file not found: {raw_path}"
        try:
            return path.read_text("utf-8")
        except Exception as e:
            return f"ERROR: reading {raw_path}: {e}"

    elif tool_name == "edit":
        old_text = args.get("old_text", "")
        new_text = args.get("new_text", "")
        if not path.exists():
            return f"ERROR: file not found: {raw_path}"
        try:
            old = path.read_text("utf-8")
            if old_text not in old:
                return f"ERROR: old text not found in {raw_path}"
            new = old.replace(old_text, new_text, 1)
            path.write_text(new, encoding="utf-8")
            return f"OK: edited {raw_path}"
        except Exception as e:
            return f"ERROR: editing {raw_path}: {e}"


    elif tool_name == "write":
        content = args.get("content", "")
        raw_path = args.get("path", "")
        if not content or not raw_path:
            return f"ERROR: write called with missing args (path={raw_path!r}, content_len={len(content)})"
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            return f"OK: wrote {raw_path} ({len(content)} bytes)"
        except Exception as e:
            return f"ERROR: writing {raw_path}: {e}"
    return f"ERROR: unknown tool: {tool_name}"


# ── Agent loop ──────────────────────────────────────────────────────

class Agent:
    """ReAct agent with native tool-calling (read/write/edit).

    Usage::
        agent = Agent(llm, system_prompt, work_dir)
        result = await agent.run()
    """
    def __init__(self, llm: LLMProvider, system_prompt: str, work_dir: Path, on_tool=None, task_label: str = ""):
        self.llm = llm
        self.system = system_prompt
        self.work_dir = work_dir.resolve()
        self.on_tool = on_tool
        self.task_label = task_label or f"agent-{id(self):x}"
        self._empty_retries = 3
        logger.info("Agent started: %s | model=%s | endpoint=%s", self.task_label, llm.model, llm.endpoint)

    async def run(self, timeout: int = 300) -> str:
        messages = [{"role": "system", "content": self.system}]
        deadline = time.monotonic() + timeout
        t_start = time.monotonic()
        round_num = 0

        # Stuck detection: same read result 3x
        last_read_result: Optional[str] = None
        stuck_count = 0

        while time.monotonic() < deadline:
            round_num += 1
            if self.on_tool:
                await self.on_tool("llm", "", "thinking", "")
            try:
                resp = await self.llm.chat(messages, tools=TOOLS)
            except Exception as e:
                logger.error("Agent %s: LLM call failed: %s", self.task_label, e)
                return f"ERROR: LLM call failed: {e}"
            content = resp.get("content", "") or ""
            tool_calls = resp.get("tool_calls")
            logger.info("%s — Round %d: content_len=%d, tool_calls=%d",
                         self.task_label, round_num, len(content), len(tool_calls or []))

            # No tool calls → final answer
            if not tool_calls:
                # Empty content retry
                if not content.strip() and self._empty_retries > 0:
                    self._empty_retries -= 1
                    logger.warning("%s: empty response (round %d), retrying (%d left)",
                                  self.task_label, round_num, self._empty_retries)
                    messages.append({"role": "user", "content": "没有收到你的回答，请重新生成。"})
                    continue
                elapsed = time.monotonic() - t_start
                logger.info("%s — done: rounds=%d, duration=%.1fs, result_len=%d",
                             self.task_label, round_num, elapsed, len(content))
                return content

            # Append assistant message with tool_calls
            messages.append({
                "role": "assistant",
                "content": content or None,
                "tool_calls": [
                    {"id": tc["id"], "type": "function", "function": tc["function"]}
                    for tc in tool_calls
                ],
            })
            # Process each tool call
            for tc in tool_calls:
                if tc["type"] != "function":
                    continue

                func = tc["function"]
                tool_name = func["name"]
                try:
                    args = json.loads(func["arguments"])
                except json.JSONDecodeError:
                    args = {}

                if tool_name == "done":
                    return content

                raw_path = args.get("path", "")
                t_tool = time.perf_counter()
                result = execute_tool(tool_name, args, self.work_dir)
                tool_ms = (time.perf_counter() - t_tool) * 1000

                if self.on_tool:
                    status = "done" if not result.startswith("ERROR") else "error"
                    await self.on_tool(tool_name, raw_path, status, result[:200])

                logger.info("  %s: %s %s → %s (%.0fms, %d chars)",
                             self.task_label, tool_name, raw_path,
                             "ok" if not result.startswith("ERROR") else "error",
                             tool_ms, len(result))

                # Stuck detection for read
                if tool_name == "read":
                    if last_read_result is not None and result == last_read_result:
                        stuck_count += 1
                    else:
                        stuck_count = 0
                    last_read_result = result
                    if stuck_count >= 3:
                        logger.warning("%s: stuck — same read 3x", self.task_label)
                        return "ERROR: Agent appears stuck (same read 3 times)"

                messages.append({
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "content": result,
                })

            # Retry if ALL tool calls had validation errors (malformed args from model)
            all_bad = True
            for tc in tool_calls:
                if tc["type"] != "function":
                    continue
                args_raw = {}
                try:
                    args_raw = json.loads(tc.get("function", {}).get("arguments", "{}"))
                except json.JSONDecodeError:
                    pass
                fn = tc.get("function", {}).get("name", "")
                has_path = bool(args_raw.get("path"))
                has_content = fn != "write" or bool(args_raw.get("content"))
                if has_path and has_content:
                    all_bad = False
                    break

            if all_bad and len(tool_calls) > 0:
                for _ in range(len(tool_calls) + 1):
                    messages.pop()
                logger.warning("%s: round %d had empty args, retrying", self.task_label, round_num)
                continue


        elapsed = time.monotonic() - t_start
        logger.warning("%s — timeout after %.1fs, rounds=%d", self.task_label, elapsed, round_num)
        return "TIMEOUT"
