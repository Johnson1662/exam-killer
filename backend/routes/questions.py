from fastapi import APIRouter, HTTPException
from typing import Optional

from backend.db import delete_question, delete_question_from_file, get_chapters, get_course, get_questions, get_question_by_qid, get_knowledge_tags, update_question, update_question_in_file
from backend.models import QuestionUpdate

router = APIRouter(prefix="/api/courses/{course_id}", tags=["questions"])


@router.get("/questions")
async def list_questions(
    course_id: int,
    tag: Optional[str] = None,
    qtype: Optional[str] = None,
    limit: int = 200,
    offset: int = 0,
):
    course = get_course(course_id)
    if not course:
        raise HTTPException(404, "Course not found")
    return get_questions(course_id, tag=tag, qtype=qtype, limit=limit, offset=offset)


@router.get("/questions/{qid}")
async def get_question(course_id: int, qid: str):
    course = get_course(course_id)
    if not course:
        raise HTTPException(404, "Course not found")
    q = get_question_by_qid(course_id, qid)
    if not q:
        raise HTTPException(404, f"Question {qid} not found")
    return q


@router.delete("/questions/{qid}")
async def delete_single_question(course_id: int, qid: str):
    course = get_course(course_id)
    if not course:
        raise HTTPException(404, "Course not found")
    if not delete_question(course_id, qid):
        raise HTTPException(404, f"Question {qid} not found")
    delete_question_from_file(course_id, qid)  # best-effort cleanup
    return {"ok": True}


@router.put("/questions/{qid}")
async def update_single_question(course_id: int, qid: str, body: QuestionUpdate):
    course = get_course(course_id)
    if not course:
        raise HTTPException(404, "Course not found")
    data = body.model_dump(exclude_none=True)
    if not data:
        raise HTTPException(400, "No fields to update")
    if not update_question(course_id, qid, data):
        raise HTTPException(404, f"Question {qid} not found")
    update_question_in_file(course_id, qid, data)  # best-effort
    q = get_question_by_qid(course_id, qid)
    if not q:
        raise HTTPException(500, "Question lost after update")
    return q


@router.get("/tags")
async def list_tags(course_id: int):
    course = get_course(course_id)
    if not course:
        raise HTTPException(404, "Course not found")
    return get_knowledge_tags(course_id)

@router.get("/chapters")
async def list_chapters(course_id: int):
    course = get_course(course_id)
    if not course:
        raise HTTPException(404, "Course not found")
    return get_chapters(course_id)
