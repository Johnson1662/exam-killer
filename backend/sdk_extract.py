"""MinerU SDK thin wrapper — extract all documents via v4 API."""

from __future__ import annotations

import logging
from pathlib import Path

from mineru import MinerU

_PDF_EXTENSIONS = {".pdf"}

logger = logging.getLogger(__name__)


def parse_document(token: str, file_path: str, pages: str | None = "1-30", timeout: int | None = None):
    """Run extraction via MinerU SDK.

    PDF → ``model="vlm"`` (vision-based, best quality).
    Office documents (DOCX etc.) → ``flash_extract`` (fast, no token needed,
    good text extraction even for complex layouts).

    Returns ``ExtractResult`` with ``.markdown``, ``.content_list``,
    ``.images`` and ``.save_markdown(path, with_images)``.
    """
    ext = Path(file_path).suffix.lower()
    client = MinerU(token)
    effective_timeout = timeout or 600

    if ext not in _PDF_EXTENSIONS:
        # Office files: use flash API (fast, no auth required, good OCR)
        logger.info("Parsing %s (flash_extract, timeout=%ds)", Path(file_path).name, effective_timeout)
        return client.flash_extract(
            file_path,
            language="ch",
            is_ocr=True,
            timeout=effective_timeout,
        )

    # PDF: use VLM model with optional page range
    kwargs: dict = {"model": "vlm", "timeout": effective_timeout}
    if pages:
        kwargs["pages"] = pages

    logger.info("Parsing %s (model=vlm, timeout=%ds)", Path(file_path).name, effective_timeout)
    return client.extract(source=file_path, **kwargs)
