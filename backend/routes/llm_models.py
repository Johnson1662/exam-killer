"""POST /api/llm/models — proxy model-list requests to LLM providers."""

import logging

import httpx
from fastapi import APIRouter, HTTPException

from backend.models import LLMModelsRequest, LLMModelsResponse, LLMModelItem

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/llm", tags=["llm"])


def _normalize_endpoint(endpoint: str) -> str:
    """Strip trailing slash and /chat/completions suffix."""
    ep = endpoint.rstrip("/")
    if ep.endswith("/chat/completions"):
        ep = ep[: -len("/chat/completions")]
    return ep


def _parse_models(data: dict) -> list[LLMModelItem]:
    """Parse model list from either OpenAI or Ollama response format."""
    models: list[LLMModelItem] = []

    # OpenAI-style: { data: [{ id, object, ... }] }
    raw = data.get("data")
    if isinstance(raw, list):
        for item in raw:
            model_id = item.get("id") or item.get("name") or item.get("model")
            if model_id:
                models.append(LLMModelItem(label=model_id, value=model_id))

    # Ollama-style: { models: [{ name, ... }] }
    raw = data.get("models")
    if isinstance(raw, list):
        for item in raw:
            model_id = item.get("name") or item.get("model") or item.get("id")
            if model_id:
                models.append(LLMModelItem(label=model_id, value=model_id))

    return models


@router.post("/models", response_model=LLMModelsResponse)
async def list_models(body: LLMModelsRequest):
    """Proxy model-list query to the configured LLM provider."""
    endpoint = _normalize_endpoint(body.endpoint)
    is_ollama = body.provider_id == "ollama"

    if is_ollama:
        url = f"{endpoint}/api/tags"
        headers = {}
    else:
        url = f"{endpoint}/models"
        headers = {"Authorization": f"Bearer {body.api_key}"}

    logger.info("Fetching models from %s", url)

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(url, headers=headers)
    except httpx.RequestError as exc:
        raise HTTPException(
            502,
            f"Failed to connect to provider: {exc}",
        )

    if resp.status_code != 200:
        snippet = resp.text[:200]
        raise HTTPException(
            502 if resp.status_code >= 500 else 400,
            f"Provider returned HTTP {resp.status_code}: {snippet}",
        )

    try:
        payload = resp.json()
    except Exception as exc:
        raise HTTPException(502, f"Invalid JSON response from provider: {exc}")

    models = _parse_models(payload)
    if not models:
        raise HTTPException(502, "Provider returned empty model list")

    return LLMModelsResponse(models=models)
