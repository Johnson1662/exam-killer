"""OpenAI-compatible LLM provider via httpx — supports native tool calling."""

from typing import Optional
import httpx


class LLMProvider:
    def __init__(self, api_key: str, endpoint: str, model: str):
        base = endpoint.rstrip("/")
        base = base.replace("/chat/completions", "")
        self.client = httpx.AsyncClient(
            base_url=base,
            timeout=httpx.Timeout(120.0, connect=10.0),
        )
        self.endpoint = base
        self.api_key = api_key
        self.model = model

    async def chat(
        self,
        messages: list[dict],
        tools: Optional[list[dict]] = None,
        tool_choice: Optional[str] = None,
    ) -> dict:
        """Call the LLM and return the full response dict.

        Returns ``{"content": ..., "tool_calls": [...]}`` where
        ``tool_calls`` is None unless the model requested tools.
        """
        body = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.1,
            "max_tokens": 8192,
        }
        if tools:
            body["tools"] = tools
        if tool_choice:
            body["tool_choice"] = tool_choice

        resp = await self.client.post(
            "/chat/completions",
            json=body,
            headers={"Authorization": f"Bearer {self.api_key}"},
        )

        if not resp.is_success:
            detail = resp.text[:500]
            raise httpx.HTTPStatusError(
                f"HTTP {resp.status_code}: {detail}",
                request=resp.request,
                response=resp,
            )

        data = resp.json()
        msg = data["choices"][0]["message"]
        return {
            "content": msg.get("content", ""),
            "tool_calls": msg.get("tool_calls", None),
        }

    async def aclose(self):
        await self.client.aclose()
