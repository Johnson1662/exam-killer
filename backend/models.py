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


class QuestionUpdate(BaseModel):
    qtype: Optional[str] = None
    content: Optional[str] = None
    options: Optional[str] = None
    answer: Optional[str] = None
    explanation: Optional[str] = None
    knowledge_tags: Optional[str] = None
    difficulty: Optional[int] = None
    chapter_tags: Optional[str] = None

class ReviewGenerateRequest(BaseModel):
    llm_key: str
    llm_endpoint: str
    llm_model: str
    outline: Optional[str] = None


class LLMModelsRequest(BaseModel):
    provider_id: str
    endpoint: str
    api_key: str


class LLMModelItem(BaseModel):
    label: str
    value: str


class LLMModelsResponse(BaseModel):
    models: list[LLMModelItem]
