from fastapi import APIRouter, HTTPException
from pathlib import Path

from backend.llm import LLMProvider
from backend.db import get_db, get_files
from backend.config import DATA_DIR

from backend.db import add_course, get_courses, get_course, delete_course
from backend.config import DATA_DIR, sanitize_dirname
from backend.models import CourseCreate, CourseResponse

router = APIRouter(prefix="/api/courses", tags=["courses"])


@router.get("", response_model=list[CourseResponse])
async def list_courses():
    return get_courses()


@router.post("", response_model=CourseResponse, status_code=201)
async def create_course(body: CourseCreate):
    name = body.name.strip()
    if not name:
        raise HTTPException(400, "Course name cannot be empty")
    dir_name = sanitize_dirname(name)
    if not dir_name:
        raise HTTPException(400, "Course name contains only invalid characters")

    # Check for existing name
    existing = get_courses()
    for c in existing:
        if c["name"] == name:
            raise HTTPException(409, f"Course '{name}' already exists")

    # Ensure unique dir_name by appending suffix if needed
    orig_dir = dir_name
    suffix = 1
    while any(c["dir_name"] == dir_name for c in existing):
        dir_name = f"{orig_dir}_{suffix}"
        suffix += 1

    # Create directory structure
    course_dir = DATA_DIR / dir_name
    (course_dir / "uploads").mkdir(parents=True, exist_ok=True)
    (course_dir / "raw").mkdir(exist_ok=True)
    (course_dir / "review-guide").mkdir(exist_ok=True)

    course_id = add_course(name, dir_name)
    return {
        "id": course_id,
        "name": name,
        "dir_name": dir_name,
        "file_count": 0,
        "question_count": 0,
        "created_at": "",
    }


@router.delete("/{course_id}")
async def remove_course(course_id: int):
    course = get_course(course_id)
    if not course:
        raise HTTPException(404, "Course not found")

    # Delete files recursively
    import shutil
    course_dir = DATA_DIR / course["dir_name"]
    if course_dir.exists():
        shutil.rmtree(course_dir)

    delete_course(course_id)
    return {"ok": True}


@router.put("/{course_id}/chapters")
async def update_chapters(course_id: int, body: dict):
    course = get_course(course_id)
    if not course:
        raise HTTPException(404, "Course not found")
    from backend.db import get_db
    db = get_db()
    db.execute("UPDATE courses SET chapters=? WHERE id=?", (body.get("chapters", ""), course_id))
    db.commit()
    return {"ok": True}


@router.post("/{course_id}/auto-chapters")
async def auto_chapters(course_id: int, body: dict):
    """AI-generate chapter list from parsed file content."""
    course = get_course(course_id)
    if not course:
        raise HTTPException(404, "Course not found")

    llm_key = body.get("llm_key", "")
    llm_endpoint = body.get("llm_endpoint", "")
    llm_model = body.get("llm_model", "")
    if not all([llm_key, llm_endpoint, llm_model]):
        raise HTTPException(400, "llm_key, llm_endpoint, llm_model required")

    llm = LLMProvider(llm_key, llm_endpoint, llm_model)
    course_dir = DATA_DIR / course["dir_name"]
    files = get_files(course_id)

    # Collect content from parsed files
    contents = []
    for f in files:
        if f["status"] != "parsed":
            continue
        raw_dir = f.get("raw_dir", "")
        if not raw_dir:
            continue
        output_path = course_dir / raw_dir / "output.md"
        if not output_path.exists():
            continue
        text = output_path.read_text("utf-8")[:2000]
        contents.append(f"--- {f['filename']} ---\n{text}")

    if not contents:
        await llm.aclose()
        return {"chapters": ""}

    prompt = (
        "以下是某门课程的试卷内容片段。请根据这些内容，推断这门课程可能包含哪些章节。\n"
        "要求：\n"
        "- 只返回章节列表，每行一个章节\n"
        "- 格式示例：第一章 极限与连续\n"
        "- 尽可能从内容中推断具体的章节名\n"
        "- 返回 3-8 个章节\n\n"
        + "\n\n".join(contents)
    )

    try:
        resp = await llm.chat([{"role": "user", "content": prompt}])
        chapters = (resp.get("content") or "").strip()
    except Exception:
        chapters = ""

    await llm.aclose()
    return {"chapters": chapters}
