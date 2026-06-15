import asyncio
import uuid

from fastapi import APIRouter, HTTPException
from typing import Optional
import re
from backend.db import get_course
from backend.config import DATA_DIR
from backend.models import ReviewGenerateRequest
from backend.sse import push_message
from backend.llm import LLMProvider
from backend.agent.core import Agent
from backend.agent.prompts.review import OUTLINE_PROMPT, CHAPTER_PROMPT


def _parse_outline_lines(text: str) -> list[str]:
    """Parse user-provided outline into chapter title list.

    Strips common numbering prefixes:
      第一章 极限与连续  → 极限与连续
      1. 极限与连续       → 极限与连续
      1、极限与连续       → 极限与连续
      极限与连续          → 极限与连续  (unchanged)
    """
    chapters = []
    for line in text.strip().split("\n"):
        line = line.strip()
        if not line:
            continue
        # Strip numbering: "第X章[：: ]", "N[.、 ]" (Chinese/Arabic)
        stripped = re.sub(r'^(?:第[一二三四五六七八九十百千]+[章节篇]?[：:\s]*|\d+[.、\s])', '', line).strip()
        if stripped:
            chapters.append(stripped)
    return chapters
router = APIRouter(prefix="/api/courses/{course_id}", tags=["review"])


@router.post("/generate-review", status_code=202)
async def generate_review(course_id: int, body: ReviewGenerateRequest):
    course = get_course(course_id)
    if not course:
        raise HTTPException(404, "Course not found")

    if not all([body.llm_key, body.llm_endpoint, body.llm_model]):
        raise HTTPException(400, "llm_key, llm_endpoint, and llm_model are required")

    llm = LLMProvider(body.llm_key, body.llm_endpoint, body.llm_model)
    asyncio.create_task(_generate_review_background(course_id, course, llm, body.outline))
    return {"task_id": str(uuid.uuid4())[:8], "message": "Review generation started"}


async def _generate_review_background(course_id: int, course: dict, llm: LLMProvider, outline: Optional[str]):
    course_dir = DATA_DIR / course["dir_name"]

    # Ensure review-guide dir exists

    # Export current questions to a file the Agent can read
    from backend.db import get_questions, get_knowledge_tags
    questions_export = course_dir / "_questions_export.md"
    qs = get_questions(course_id)
    tags = get_knowledge_tags(course_id)
    if qs:
        lines = [f"# 题库：{course['name']}", "", f"知识点标签：{', '.join(tags)}", ""]
        for q in qs:
            lines.append(f"### {q['qid']}")
            lines.append(f"题型：{q['qtype']} | 难度：{q['difficulty']}")
            lines.append(f"知识点：{q['knowledge_tags']}")
            lines.append("")
            lines.append(q['content'] or '')
            if q.get('answer'):
                lines.append(f"答案：{q['answer']}")
            if q.get('explanation'):
                lines.append(f"解析：{q['explanation']}")
            lines.append("")
        questions_export.write_text("\n".join(lines), encoding="utf-8")
    else:
        questions_export.write_text(f"# 题库：{course['name']}\n\n（暂无题目）\n", encoding="utf-8")
    (course_dir / "review-guide").mkdir(exist_ok=True)

    # Step 1: Determine chapter outline
    outline = (outline or "").strip()
    if outline:
        # Use user-provided outline directly, skip Agent
        chapters = _parse_outline_lines(outline)
        if not chapters:
            await push_message(course_id, "无法解析用户提供的大纲")
            await push_message(course_id, "done")
            return
        await push_message(course_id, f"使用用户提供的大纲，共 {len(chapters)} 个章节")
    else:
        # Generate outline via Agent
        await push_message(course_id, "正在分析题库知识点，生成章节大纲...")
        agent = Agent(llm, OUTLINE_PROMPT.format(outline_extra=""), course_dir)
        try:
            outline_result = await asyncio.wait_for(agent.run(), timeout=300)
        except asyncio.TimeoutError:
            await push_message(course_id, "大纲生成超时")
            await push_message(course_id, "done")
            return

        chapters = [ln.strip() for ln in outline_result.split("\n") if ln.strip() and not ln.startswith("DONE")]
        if not chapters:
            await push_message(course_id, "未能生成章节大纲")
            await push_message(course_id, "done")
            return

        await push_message(course_id, f"生成 {len(chapters)} 个章节: {', '.join(chapters)}")

        # Save generated outline to course
        from backend.db import get_db
        db = get_db()
        db.execute("UPDATE courses SET chapters=? WHERE id=?", ("\n".join(chapters), course_id))
        db.commit()

    # Build per-chapter question bank files
    from collections import defaultdict
    bank_dir = course_dir / "question_bank"
    bank_dir.mkdir(exist_ok=True)
    qs_by_chapter = defaultdict(list)
    for q in qs:
        chapter_tag = q.get("chapter_tags", "") or ""
        qs_by_chapter[chapter_tag].append(q)

    def _sanitize_filename(name: str) -> str:
        return re.sub(r'[\\/:*?"<>|]', '_', name)

    for chapter_title in chapters if chapters else []:
        matched = []
        for tag, qlist in qs_by_chapter.items():
            if chapter_title in tag:
                matched.extend(qlist)
        if not matched:
            continue
        ch_file = bank_dir / f"{_sanitize_filename(chapter_title)}.md"
        ch_lines = [f"# {chapter_title}", ""]
        for q in matched:
            ch_lines.append(f"## {q['qid']}")
            ch_lines.append(f"**题型**：{q['qtype']} | **难度**：{q['difficulty']} | **知识点**：{q['knowledge_tags']}")
            ch_lines.append("")
            ch_lines.append(q["content"] or "")
            if q.get("answer"):
                ch_lines.append(f"\n**答案**：{q['answer']}")
            if q.get("explanation"):
                ch_lines.append(f"\n**解析**：{q['explanation']}")
            ch_lines.append("")
        ch_file.write_text("\n".join(ch_lines), encoding="utf-8")


    # Step 2: Generate each chapter serially
    previous_summaries = []
    for i, chapter_title in enumerate(chapters, 1):
        await push_message(course_id, f"正在生成第 {i} 章: {chapter_title}")

        prompt = CHAPTER_PROMPT.format(
            course_name=course["name"],
            chapter_title=chapter_title,
            chapter_index=i,
            chapter_file=_sanitize_filename(chapter_title) + ".md",
            previous_chapters_summary="\n".join(previous_summaries) if previous_summaries else "（尚无已完成的章节）",
        )

        agent = Agent(llm, prompt, course_dir)
        chapter_content = ""
        try:
            chapter_content = await asyncio.wait_for(agent.run(), timeout=600)
        except asyncio.TimeoutError:
            await push_message(course_id, f"第 {i} 章生成超时，跳过")
            continue

        # If the Agent didn't write the file (edit/write failed), write result directly
        chapter_file = course_dir / "review-guide" / f"{i:02d}-{_sanitize_filename(chapter_title)}.md"
        if not chapter_file.exists() and chapter_content:
            chapter_file.write_text(chapter_content, encoding="utf-8")

        # Extract first paragraph for summary context
        text = chapter_file.read_text("utf-8") if chapter_file.exists() else chapter_content
        first_para = text.split("\n\n")[0] if "\n\n" in text else text[:200]
        previous_summaries.append(f"{chapter_title}: {first_para[:100]}")

        await push_message(course_id, f"完成第 {i} 章: {chapter_title}")


    await push_message(course_id, "复习手册生成完毕")
    await push_message(course_id, "done")
    await llm.aclose()


@router.get("/review/chapters")
async def list_chapters(course_id: int):
    course = get_course(course_id)
    if not course:
        raise HTTPException(404, "Course not found")

    guide_dir = DATA_DIR / course["dir_name"] / "review-guide"
    if not guide_dir.exists():
        return []

    chapters = []
    for f in sorted(guide_dir.iterdir()):
        if f.suffix == ".md":
            chapters.append({
                "filename": f.name,
                "title": f.stem[3:] if f.stem[:2].isdigit() else f.stem,
                "size": f.stat().st_size,
            })
    return chapters


@router.get("/review/chapters/{filename:path}")
async def get_chapter(course_id: int, filename: str):
    course = get_course(course_id)
    if not course:
        raise HTTPException(404, "Course not found")

    path = DATA_DIR / course["dir_name"] / "review-guide" / filename
    if not path.exists() or not path.suffix == ".md":
        raise HTTPException(404, "Chapter not found")

    return {"filename": filename, "content": path.read_text("utf-8")}



@router.get("/review/chapter-questions")
async def list_chapter_questions(course_id: int):
    """Return each chapter's title and the QIDs it references."""
    course = get_course(course_id)
    if not course:
        raise HTTPException(404, "Course not found")

    guide_dir = DATA_DIR / course["dir_name"] / "review-guide"
    if not guide_dir.exists():
        return []

    result = []
    qid_re = re.compile(r'\[(Q\d+)\]')
    for f in sorted(guide_dir.iterdir()):
        if f.suffix != ".md":
            continue
        content = f.read_text("utf-8")
        qids = sorted(set(qid_re.findall(content)))
        result.append({
            "filename": f.name,
            "title": f.stem[3:] if f.stem[:2].isdigit() else f.stem,
            "qids": qids,
        })
    return result
