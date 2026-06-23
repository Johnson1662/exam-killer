"""FastAPI entry-point."""

import io
import os
import zipfile
from pathlib import Path
import logging

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.staticfiles import StaticFiles

from backend.config import DATA_DIR, DB_PATH, DEFAULT_LLM_ENDPOINT, DEFAULT_LLM_MODEL
from backend.db import init_db, get_course
from backend.routes.courses import router as courses_router
from backend.routes.files import router as files_router
from backend.routes.questions import router as questions_router
from backend.routes.review import router as review_router

from backend.routes.llm_models import router as llm_models_router

app = FastAPI(title="Exam-Killer", version="0.1.0")

# ── Read-only mode ───────────────────────────────────────────────────
READ_ONLY = os.environ.get("EXAM_READ_ONLY", "").lower() in ("1", "true", "yes")


@app.middleware("http")
async def read_only_middleware(request: Request, call_next):
    if READ_ONLY and request.method in ("POST", "PUT", "DELETE"):
        return Response(status_code=403, content='{"detail":"Read-only mode"}')
    return await call_next(request)


# ── Lifecycle ────────────────────────────────────────────────────────


@app.on_event("startup")
async def startup():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    init_db()


# ── Mount routes ─────────────────────────────────────────────────────

app.include_router(courses_router)
app.include_router(files_router)
app.include_router(questions_router)
app.include_router(llm_models_router)
app.include_router(review_router)

# ── Client config ────────────────────────────────────────────────────


@app.get("/api/config")
async def client_config():
    return {
        "llm_endpoint": DEFAULT_LLM_ENDPOINT if not READ_ONLY else "",
        "llm_model": DEFAULT_LLM_MODEL if not READ_ONLY else "",
        "llm_key_configured": False,
        "read_only": READ_ONLY,
    }


# ── Static file proxy for assets and frontend ────────────────────────


@app.get("/api/assets/{dir_name}/images/{filename}")
async def serve_asset(dir_name: str, filename: str):
    """Serve asset images, falling back to raw/ images if not yet copied."""
    # Primary: assets dir
    asset_path = DATA_DIR / dir_name / "assets" / filename
    if asset_path.exists():
        return Response(
            content=asset_path.read_bytes(), media_type=_infer_mime(filename)
        )

    # Fallback: search raw/{id}/images/
    raw_base = DATA_DIR / dir_name / "raw"
    if raw_base.exists():
        for raw_dir in sorted(raw_base.iterdir()):
            img = raw_dir / "images" / filename
            if img.exists():
                return Response(
                    content=img.read_bytes(), media_type=_infer_mime(filename)
                )

    raise HTTPException(404, "Image not found")


def _infer_mime(name: str) -> str:
    ext = Path(name).suffix.lower()
    return {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".webp": "image/webp",
    }.get(ext, "application/octet-stream")


# ── Export endpoints ─────────────────────────────────────────────────


@app.get("/api/courses/{course_id}/export/md")
async def export_md(course_id: int, scope: str = "review-guide"):
    """Export review-guide chapters as MD/zip."""
    course = get_course(course_id)
    if not course:
        raise HTTPException(404, "Course not found")
    course_dir = DATA_DIR / course["dir_name"]
    if scope == "review-guide":
        guide_dir = course_dir / "review-guide"
        if not guide_dir.exists():
            raise HTTPException(404, "Review guide not found")

        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            for md_file in sorted(guide_dir.iterdir()):
                if md_file.suffix == ".md":
                    zf.writestr(md_file.name, md_file.read_text("utf-8"))
        buf.seek(0)
        safe_name = "review-guide.zip"
        return Response(
            content=buf.getvalue(),
            media_type="application/zip",
            headers={"Content-Disposition": f'attachment; filename="{safe_name}"'},
        )

    raise HTTPException(400, f"Unknown scope: {scope}")


# ── Frontend SPA (serve index.html for all non-API routes) ───────────

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"


@app.get("/")
@app.get("/{path:path}")
async def serve_frontend(path: str = ""):
    """Serve static SPA files, falling back to index.html for hash routes."""
    if path.startswith("api/") or path.startswith("api"):
        raise HTTPException(404, "API endpoint not found")

    file_path = (FRONTEND_DIR / path).resolve()
    # Prevent directory traversal outside FRONTEND_DIR
    if not str(file_path).startswith(str(FRONTEND_DIR.resolve())):
        raise HTTPException(404, "Not found")

    if file_path.exists() and file_path.is_file():
        return Response(
            content=file_path.read_bytes(), media_type=_mime_from_ext(file_path.suffix)
        )

    # Fallback to index.html for SPA
    index_path = FRONTEND_DIR / "index.html"
    if index_path.exists():
        return Response(content=index_path.read_bytes(), media_type="text/html")

    raise HTTPException(404, "Not found")


def _mime_from_ext(suffix: str) -> str:
    return {
        ".html": "text/html",
        ".js": "application/javascript",
        ".css": "text/css",
        ".json": "application/json",
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".svg": "image/svg+xml",
        ".ico": "image/x-icon",
    }.get(suffix.lower(), "application/octet-stream")
