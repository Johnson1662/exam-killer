import asyncio
import json
import logging
import os
import queue
import shutil
import subprocess
import threading
import time
from pathlib import Path
from typing import Any, Callable, Coroutine, Optional
from uuid import uuid4

logger = logging.getLogger(__name__)

ToolCallback = Optional[Callable[[str, str, str, str], Coroutine[Any, Any, None]]]


class PiRpcAgent:
    """Agent that delegates prompt + tool execution to Pi's RPC mode.

    Spawns ``pi --mode rpc`` as a subprocess and drives it via
    newline-delimited JSON over stdin/stdout.  Pi's built-in read/write/bash
    tools handle all file operations, so the caller only sends the system
    prompt and reads back the final assistant message.
    """

    def __init__(
        self,
        system_prompt: str,
        work_dir: str,
        api_key: str,
        endpoint: str,
        model: str,
        on_tool: ToolCallback = None,
        task_label: str = "",
    ):
        self.system = system_prompt
        self.work_dir = work_dir
        self.on_tool = on_tool
        self.task_label = task_label or f"pi-{id(self):x}"
        self._closed = False
        self._log_prefix = f"[{self.task_label}]"
        self._ext_path: Optional[Path] = None

        from urllib.parse import urlparse

        parsed = urlparse(endpoint)
        hostname = parsed.hostname or ""

        extra_flags: list[str] = []
        env = os.environ.copy()
        pi_args: list[str] = [
            "--mode", "rpc",
            "--no-session",
        ]

        if "opencode.ai" in hostname:
            # Pi has native opencode providers — use them directly.
            if "/zen/go" in parsed.path:
                provider = "opencode-go"
            else:
                provider = "opencode"
            env["OPENCODE_API_KEY"] = api_key
            base = endpoint

        elif "api.openai.com" in hostname:
            provider = "openai"
            env["OPENAI_API_KEY"] = api_key
            base = endpoint

        else:
            # Arbitrary OpenAI-compatible endpoint — register a temporary
            # Pi extension that creates a custom provider with the right
            # base URL, so Pi actually sends requests there.
            provider = "custom-opencode"  # arbitrary name
            base = endpoint.rstrip("/")
            base_clean = base.replace("/chat/completions", "")

            ext_dir = Path(work_dir) / ".pi-ext"
            ext_dir.mkdir(parents=True, exist_ok=True)
            ext_id = f"ext-{uuid4().hex[:12]}"
            ext_path = ext_dir / f"{ext_id}.js"

            ext_src = f"""\
export default function(pi) {{
  pi.registerProvider("{provider}", {{
    baseUrl: {json.dumps(base_clean)},
    apiKey: "$CUSTOM_OPENAI_KEY",
    api: "openai-completions",
    models: [{{
      id: {json.dumps(model)},
      name: "Custom Model",
      reasoning: false,
      input: ["text"],
      cost: {{ input: 0, output: 0 }},
      contextWindow: 128000,
      maxTokens: 16384,
    }}],
  }});
}}
"""
            ext_path.write_text(ext_src, encoding="utf-8")
            self._ext_path = ext_path  # for cleanup in aclose()

            env["CUSTOM_OPENAI_KEY"] = api_key
            extra_flags.extend(["--extension", str(ext_path)])
            logger.info(
                "%s created temp extension for custom endpoint: %s",
                self._log_prefix, ext_path,
            )

        pi_exe = _find_pi()
        if pi_exe is None:
            raise RuntimeError(
                "pi CLI not found. Install it: npm install -g @earendil-works/pi-coding-agent"
            )

        self._proc = subprocess.Popen(
            [
                pi_exe,
                "--mode", "rpc",
                "--no-session",
                "--provider", provider,
                "--model", model,
                *extra_flags,
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=work_dir,
            env=env,
            text=True,
        )

        logger.info(
            "%s PiRpcAgent started | model=%s | endpoint=%s | workdir=%s",
            self._log_prefix,
            model,
            base,
            work_dir,
        )

        # Background thread to drain stderr into logs
        self._stderr_thread = threading.Thread(
            target=_drain_stderr,
            args=(self._proc.stderr, self._log_prefix),
            daemon=True,
        )
        self._stderr_thread.start()

    async def run(self, timeout: int = 300) -> str:
        """Send the system prompt, stream events, return final assistant text."""
        self._write_line({"type": "prompt", "message": self.system})

        accumulated = ""
        tool_name_current: Optional[str] = None
        api_error: Optional[str] = None

        deadline = time.monotonic() + timeout
        try:
            async for line in self._read_lines(deadline):
                event = json.loads(line)
                et = event.get("type")

                if et == "message_update":
                    inner = event.get("assistantMessageEvent", {})
                    if inner.get("type") == "text_delta":
                        delta = inner["delta"]
                        if not accumulated and delta.strip():
                            # First meaningful text -> signal "thinking"
                            if self.on_tool:
                                await self.on_tool("llm", "", "thinking", "")
                        accumulated += delta

                elif et == "tool_execution_start":
                    tool_name_current = event.get("toolName", "")
                    args = event.get("args", {})
                    path = args.get("path", "")
                    if self.on_tool:
                        await self.on_tool(tool_name_current, path, "running", "")

                elif et == "tool_execution_end":
                    tn = event.get("toolName", tool_name_current or "")
                    args = event.get("args", {})
                    path = args.get("path", "")
                    status = "error" if event.get("isError") else "done"
                    detail = ""
                    result = event.get("result")
                    if result:
                        content_blocks = result.get("content", [])
                        text_parts = [
                            b.get("text", "")
                            for b in content_blocks
                            if isinstance(b, dict) and b.get("type") == "text"
                        ]
                        detail = "".join(text_parts)[:200]
                    if self.on_tool:
                        await self.on_tool(tn, path, status, detail)
                    tool_name_current = None

                elif et == "message_end":
                    msg = event.get("message", {})
                    if msg.get("role") == "assistant":
                        sr = msg.get("stopReason", "")
                        if sr == "error":
                            api_error = msg.get("errorMessage", "Unknown API error")
                            logger.warning("%s API error: %s", self._log_prefix, api_error)

                elif et == "agent_end":
                    # If a known API error occurred, surface it
                    if api_error:
                        return f"ERROR: API error: {api_error}"
                    msgs = event.get("messages", [])
                    for msg in reversed(msgs):
                        if msg.get("role") == "assistant":
                            text = _extract_text(msg.get("content", ""))
                            if text:
                                logger.info(
                                    "%s agent_end -> text len=%d (from messages)",
                                    self._log_prefix,
                                    len(text),
                                )
                                return text
                    logger.info(
                        "%s agent_end -> returning accumulated text len=%d",
                        self._log_prefix,
                        len(accumulated),
                    )
                    return accumulated

        except asyncio.TimeoutError:
            logger.warning("%s timeout after %ds", self._log_prefix, timeout)
            self._abort()
            return "TIMEOUT"

        logger.info(
            "%s finished, accumulated len=%d",
            self._log_prefix,
            len(accumulated),
        )
        return accumulated

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _write_line(self, obj: dict) -> None:
        line = json.dumps(obj, ensure_ascii=False) + "\n"
        self._proc.stdin.write(line)
        self._proc.stdin.flush()

    def _abort(self) -> None:
        try:
            self._write_line({"type": "abort"})
        except Exception:
            pass

    async def _read_lines(self, deadline: float):
        """Async generator yielding parsed JSON lines from stdout."""
        q: queue.Queue = queue.Queue()
        sentinel = object()

        def reader():
            try:
                for raw in self._proc.stdout:
                    raw = raw.rstrip("\r\n")
                    if raw:
                        q.put(raw)
            except ValueError:
                pass
            finally:
                q.put(sentinel)

        thread = threading.Thread(target=reader, daemon=True)
        thread.start()

        while time.monotonic() < deadline:
            try:
                line = q.get(timeout=0.1)
                if line is sentinel:
                    break
                yield line
            except queue.Empty:
                continue

        if time.monotonic() >= deadline:
            raise asyncio.TimeoutError()

    async def aclose(self) -> None:
        if self._closed:
            return
        self._closed = True
        self._abort()
        try:
            self._proc.stdin.close()
        except Exception:
            pass
        try:
            self._proc.terminate()
            self._proc.wait(timeout=5)
        except Exception:
            self._proc.kill()
            self._proc.wait(timeout=2)
        # Clean up temp extension file if one was created
        ext = getattr(self, "_ext_path", None)
        if ext:
            try:
                ext.unlink(missing_ok=True)
            except Exception:
                pass
        logger.info("%s PiRpcAgent closed", self._log_prefix)


# ------------------------------------------------------------------
# Module-level helpers
# ------------------------------------------------------------------


def _extract_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = [
            b.get("text", "")
            for b in content
            if isinstance(b, dict) and b.get("type") == "text"
        ]
        return "\n".join(parts)
    return ""


def _drain_stderr(pipe, log_prefix: str) -> None:
    """Read stderr lines and forward them to the Python logger."""
    try:
        for line in pipe:
            line = line.rstrip("\r\n")
            if line:
                logger.debug("%s pi-stderr: %s", log_prefix, line)
    except ValueError:
        pass


def _find_pi() -> Optional[str]:
    """Locate the ``pi`` CLI executable in PATH or npm global bin."""
    # 1. Check PATH
    exe = shutil.which("pi")
    if exe:
        return exe
    exe = shutil.which("pi.cmd")
    if exe:
        return exe
    # 2. Check npm global install dir (Windows)
    npm_global = Path(os.environ.get("APPDATA", "")) / "npm" / "pi.cmd"
    if npm_global.exists():
        return str(npm_global)
    npm_global = Path(os.environ.get("APPDATA", "")) / "npm" / "pi"
    if npm_global.exists():
        return str(npm_global)
    # 3. Check npm global on Unix
    npm_root = os.environ.get("NPM_CONFIG_PREFIX") or "/usr/local"
    for name in ("pi", "pi.cmd"):
        p = Path(npm_root) / "bin" / name
        if p.exists():
            return str(p)
    return None
