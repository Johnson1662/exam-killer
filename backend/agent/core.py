"""Agent loop — gives an LLM read/write/edit tools via native function calling."""

import json
import time
from pathlib import Path
from typing import Optional

from backend.llm import LLMProvider


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
                "additionalProperties": False,
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
                "additionalProperties": False,
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
                "additionalProperties": False,
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
    try:
        path = _resolve_path(work_dir, raw_path)
    except PermissionError as e:
        return f"ERROR: {e}"

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
        if not content:
            return f"ERROR: no content provided for {raw_path}"
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

    def __init__(self, llm: LLMProvider, system_prompt: str, work_dir: Path):
        self.llm = llm
        self.system = system_prompt
        self.work_dir = work_dir.resolve()

    async def run(self, timeout: int = 300) -> str:
        messages = [{"role": "system", "content": self.system}]
        deadline = time.monotonic() + timeout

        # Stuck detection: same read result 3x
        last_read_result: Optional[str] = None
        stuck_count = 0

        while time.monotonic() < deadline:
            resp = await self.llm.chat(messages, tools=TOOLS)
            content = resp.get("content", "") or ""
            tool_calls = resp.get("tool_calls")

            # No tool calls → final answer
            if not tool_calls:
                return content

            # Append assistant message with tool_calls (required before tool role messages)
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

                result = execute_tool(tool_name, args, self.work_dir)

                # Stuck detection for read
                if tool_name == "read":
                    if last_read_result is not None and result == last_read_result:
                        stuck_count += 1
                    else:
                        stuck_count = 0
                    last_read_result = result
                    if stuck_count >= 3:
                        return "ERROR: Agent appears stuck (same read 3 times)"

                messages.append({
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "content": result,
                })

        return "TIMEOUT"
