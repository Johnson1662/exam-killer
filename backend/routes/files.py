import asyncio
import json
import uuid
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from backend.db import (
    get_course, add_file, get_file, get_files, update_file_status,
    get_unparsed_file_ids, sync_all_questions, get_questions,
    get_chapters, get_db,
)
from backend.config import DATA_DIR, MAX_PAGES, ALLOWED_EXTENSIONS, MAX_UPLOAD_SIZE
from backend.models import ParseRequest, FileUploadResponse
from backend.sse import push_message, event_stream
from backend.sdk_extract import parse_pdf
from backend.llm import LLMProvider
from backend.agent.core import Agent
from backend.agent.prompts.extractor import EXTRACTOR_PROMPT

router = APIRouter(prefix="/api/courses/{course_id}", tags=["files"])


@router.get("/files", response_model=list[dict])
async def list_files(course_id: int):
    course = get_course(course_id)
    if not course:
        raise HTTPException(404, "Course not found")
    return get_files(course_id)


@router.post("/files", response_model=list[FileUploadResponse])
async def upload_files(course_id: int, files: list[UploadFile] = File(...)):
    course = get_course(course_id)
    if not course:
        raise HTTPException(404, "Course not found")

    results = []
    upload_dir = DATA_DIR / course["dir_name"] / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)

    for f in files:
        ext = Path(f.filename).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(400, f"File type '{ext}' not allowed for '{f.filename}'")

        content = await f.read()
        if len(content) > MAX_UPLOAD_SIZE:
            raise HTTPException(400, f"File '{f.filename}' exceeds 200 MB limit")

        file_id = add_file(course_id, f.filename, f.filename)
        dest = upload_dir / f.filename
        dest.write_bytes(content)
        results.append({"file_id": file_id, "filename": f.filename, "status": "pending"})

    return results

@router.post("/parse", status_code=202)
async def trigger_parse(course_id: int, body: ParseRequest):
    course = get_course(course_id)
    if not course:
        raise HTTPException(404, "Course not found")
    if not body.mineru_token:
        raise HTTPException(400, "mineru_token is required")

    task_id = str(uuid.uuid4())[:8]

    # Create background task
    asyncio.create_task(_parse_background(course_id, course["dir_name"], body.mineru_token, body.file_ids))

    return {"task_id": task_id, "message": "Parsing started"}


async def _parse_background(course_id: int, dir_name: str, token: str, file_ids: list[int]):
    """Background task: extract → classify → extract questions → sync."""
    unparsed = get_unparsed_file_ids(course_id, file_ids)
    if not unparsed:
        await push_message(course_id, "没有待解析的文件")
        await push_message(course_id, "done")
        return

    course_dir = DATA_DIR / dir_name

    for fid in unparsed:
        file_info = get_file(fid)
        if not file_info:
            continue

        update_file_status(fid, "extracting")
        await push_message(course_id, f"解析中: {file_info['filename']}")

        upload_path = course_dir / "uploads" / file_info["original_name"]
        if not upload_path.exists():
            update_file_status(fid, "failed", error_msg="Upload file not found")
            await push_message(course_id, f"文件不存在: {file_info['filename']}")
            continue

        try:
            result = await asyncio.to_thread(
                parse_pdf, token, str(upload_path), f"1-{MAX_PAGES}"
            )

            raw_dir = f"raw/{fid}"
            output_dir = course_dir / raw_dir
            output_dir.mkdir(parents=True, exist_ok=True)

            # Save markdown
            result.save_markdown(str(output_dir / "output.md"), with_images=True)

            # Save content_list
            with open(output_dir / "content_list.json", "w", encoding="utf-8") as f:
                json.dump(result.content_list, f, ensure_ascii=False, indent=2)

            update_file_status(fid, "parsed", raw_dir=raw_dir)
            await push_message(course_id, f"解析完成: {file_info['filename']}")
        except Exception as e:
            update_file_status(fid, "failed", error_msg=str(e))
            await push_message(course_id, f"解析失败: {file_info['filename']}: {e}")

    # Classification is skipped in v0.1 — Agent-based classification requires LLM key at parse time,
    # which the user provides separately. For now we mark all as mixed.
    # In a future version we'll route through agent here.
    await push_message(course_id, '解析流程结束。请在课程页面上使用"抽取题目"功能来提取题目。')
    await push_message(course_id, "done")


@router.get("/parse/events")
async def parse_events(course_id: int):
    """SSE endpoint for parse progress."""
    return StreamingResponse(
        event_stream(course_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/extract", status_code=202)
async def trigger_extract(course_id: int, body: dict):
    """Run Agent-based question extraction.

    Request body::
        {"llm_key": "...", "llm_endpoint": "...", "llm_model": "...", "file_ids": [1,2]}
    """
    course = get_course(course_id)
    if not course:
        raise HTTPException(404, "Course not found")

    llm_key = body.get("llm_key")
    llm_endpoint = body.get("llm_endpoint")
    llm_model = body.get("llm_model")
    file_ids = body.get("file_ids", [])
    chapters = body.get("chapters", "")

    if not all([llm_key, llm_endpoint, llm_model]):
        raise HTTPException(400, "llm_key, llm_endpoint, and llm_model are required")

    asyncio.create_task(_run_extract_agents(
        course_id, course, LLMProvider(llm_key, llm_endpoint, llm_model), file_ids, chapters
    ))
    return {"task_id": str(uuid.uuid4())[:8], "message": "Extraction started"}


async def _run_extract_agents(course_id: int, course: dict, llm: LLMProvider, file_ids: list[int], chapters: str = ""):
    course_dir = DATA_DIR / course["dir_name"]

    async def process_one(fid: int):
        file_info = get_file(fid)
        if not file_info or (file_info["status"] != "parsed" and file_info["status"] != "annotated"):
            await push_message(course_id, f"跳过文件 {fid}（状态={file_info.get('status', '?')}）")
            return

        # Already annotated — skip Agent, sync will pick up existing annotations
        if file_info["status"] == "annotated":
            await push_message(course_id, f"跳过 {file_info['filename']}（已标注）")
            return

        # Use course-level chapters if set, otherwise fall back to file-level
        if chapters:
            chapter_context = chapters
        else:
            file_chapters = file_info.get("chapters", "") if file_info else ""
            chapter_context = file_chapters if file_chapters else "(未指定章节，请根据内容判断)"

        prompt = EXTRACTOR_PROMPT.format(
            course_name=course["name"],
            file_id=fid,
            filename=file_info["filename"],
            file_type=file_info.get("file_type", "mixed"),
            paired_info="",
            paired_read_instruction="",
            paired_path="",
            chapter_context=chapter_context,
        )

        agent = Agent(llm, prompt, course_dir)
        try:
            result = await asyncio.wait_for(agent.run(), timeout=600)
        except asyncio.TimeoutError:
            await push_message(course_id, f"超时: {file_info['filename']}")
            return
        except Exception as e:
            await push_message(course_id, f"失败: {file_info['filename']}: {e}")
            return

        await push_message(course_id, f"完成: {file_info['filename']}")
        update_file_status(fid, "annotated")

    # Launch all files concurrently
    tasks = [process_one(fid) for fid in file_ids if fid]
    await push_message(course_id, f"并发标注 {len(tasks)} 个文件...")
    await asyncio.gather(*tasks)

    # Single sync pass after all agents complete
    try:
        count = sync_all_questions(course_id)
        await push_message(course_id, f"题库同步完成，共 {count} 道题")
    except Exception as e:
        await push_message(course_id, f"题库同步失败: {e}")

    await push_message(course_id, "done")
    await llm.aclose()


@router.put("/files/{file_id}/chapters")
async def set_file_chapters(course_id: int, file_id: int, body: dict):
    course = get_course(course_id)
    if not course:
        raise HTTPException(404, "Course not found")
    f = get_file(file_id)
    if not f or f["course_id"] != course_id:
        raise HTTPException(404, "File not found")
    chapters = body.get("chapters", "")
    db.execute("UPDATE files SET chapters=? WHERE id=?", (chapters, file_id))
    db.commit()
    return {"file_id": file_id, "chapters": chapters}

@router.post("/files/auto-chapters")
async def auto_chapters(course_id: int, body: dict):
    """AI-generate chapter list for all parsed files without chapters."""
    course = get_course(course_id)
    if not course:
        raise HTTPException(404, "Course not found")
    llm = LLMProvider(body.get("llm_key", ""), body.get("llm_endpoint", ""), body.get("llm_model", ""))
    course_dir = DATA_DIR / course["dir_name"]
    files = get_files(course_id)
    db = get_db()
    for f in files:
        if f["status"] != "parsed":
            continue
        if f.get("chapters"):
            continue  # already set
        raw_dir = f.get("raw_dir", "")
        if not raw_dir:
            continue
        output_path = course_dir / raw_dir / "output.md"
        if not output_path.exists():
            continue

        content = output_path.read_text("utf-8")[:3000]
        prompt = f"""依据以下试卷内容，用中文生成该试卷所属的章节列表。
要求：
- 只返回章节列表，每行一个章节
- 格式示例：第一章 极限与连续
- 如果无法从内容判断，根据常见高等数学/离散数学教材目录生成合理的章节

试卷内容：
{content}"""

        try:
            resp = await llm.chat([{"role": "user", "content": prompt}])
            chapter_text = (resp.get("content") or "").strip()
            # Take first 5 lines
            lines = [l.strip() for l in chapter_text.split("\n") if l.strip()][:5]
            chapters = ", ".join(lines)
            if chapters:
                db.execute("UPDATE files SET chapters=? WHERE id=?", (chapters, f["id"]))
                db.commit()
                results.append({"file_id": f["id"], "chapters": chapters})
        except Exception as e:
            results.append({"file_id": f["id"], "error": str(e)})

    await llm.aclose()
    return {"results": results}
