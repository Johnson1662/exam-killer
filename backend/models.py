from pydantic import BaseModel
from typing import Optional


class CourseCreate(BaseModel):
    name: str


class CourseResponse(BaseModel):
    id: int
    name: str
    dir_name: str
    chapters: str = ""
    file_count: int = 0
    question_count: int = 0
    created_at: str


class FileUploadResponse(BaseModel):
    file_id: int
    filename: str
    status: str = "pending"


class ParseRequest(BaseModel):
    mineru_token: str
    file_ids: list[int]


class ParseResponse(BaseModel):
    task_id: str
    message: str = "Parsing started"


class QuestionResponse(BaseModel):
    qid: str
    qtype: str
    content: str
    options: Optional[str] = None
    answer: str = ""
    explanation: str = ""
    knowledge_tags: str = ""
    difficulty: int = 1


class ReviewGenerateRequest(BaseModel):
    llm_key: str
    llm_endpoint: str
    llm_model: str
    outline: Optional[str] = None
