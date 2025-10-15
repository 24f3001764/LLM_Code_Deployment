from pydantic import BaseModel, Field
from typing import List, Optional


class Attachment(BaseModel):
    """Attachment with data URI"""
    name: str
    url: str  # data URI format


class TaskRequest(BaseModel):
    """Incoming task request from instructors"""
    email: str
    secret: str
    task: str
    round: int = Field(ge=1, le=2)
    nonce: str
    brief: str
    checks: List[str]
    evaluation_url: str
    attachments: Optional[List[Attachment]] = []


class EvaluationPayload(BaseModel):
    """Payload to send to evaluation_url"""
    email: str
    task: str
    round: int
    nonce: str
    repo_url: str
    commit_sha: str
    pages_url: str


class APIResponse(BaseModel):
    """Immediate response to task request"""
    status: str
    message: str
    task: str
    round: int
