"""Pydantic models: they validate incoming JSON and define response shapes."""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class QuestionSummary(BaseModel):
    question_id: int
    title: str
    category: str
    difficulty: str


class Question(QuestionSummary):
    description: str
    sample_input: Optional[str] = None
    expected_output: Optional[str] = None


class QuestionCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    category: str = Field(min_length=1, max_length=60)
    difficulty: str = Field(default="Beginner", pattern="^(Beginner|Intermediate|Advanced)$")
    description: str = Field(min_length=1)
    sample_input: Optional[str] = None
    expected_output: Optional[str] = None


class AttemptCreate(BaseModel):
    student_id: int = Field(gt=0)
    question_id: int = Field(gt=0)
    submitted_answer: Optional[str] = Field(default=None, max_length=5000)
    completed: bool = False  # True = student marks it done without typing an answer

    @field_validator("submitted_answer")
    @classmethod
    def blank_to_none(cls, v):
        v = (v or "").strip()
        return v or None


class AttemptResult(BaseModel):
    attempt_id: int
    score: float
    completed: bool
    message: str


class RecentAttempt(BaseModel):
    attempt_id: int
    title: str
    score: float
    completed: bool
    attempted_at: datetime


class Progress(BaseModel):
    student_id: int
    full_name: str
    total_questions: int
    questions_attempted: int
    questions_completed: int
    total_attempts: int
    average_score: float
    recent_attempts: List[RecentAttempt]


class ChatRequest(BaseModel):
    message: str = Field(max_length=500)

    @field_validator("message")
    @classmethod
    def not_empty(cls, v):
        v = v.strip()
        if not v:
            raise ValueError("Message cannot be empty.")
        return v


class ChatResponse(BaseModel):
    reply: str
    matched_topic: Optional[str] = None
