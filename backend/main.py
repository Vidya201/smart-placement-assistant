"""FastAPI app. Run from the backend folder:  uvicorn main:app --reload
Interactive docs: http://127.0.0.1:8000/docs"""
import re
from pathlib import Path
from typing import List, Optional

import mysql.connector
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

import models
from chatbot import get_reply
from schemas import (AttemptCreate, AttemptResult, ChatRequest, ChatResponse,
                     Progress, Question, QuestionCreate, QuestionSummary)

app = FastAPI(title="Smart Placement Preparation Assistant", version="1.0")

# CORS lets a browser page served from another port (or file://) call this API.
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@app.exception_handler(mysql.connector.Error)
async def database_error_handler(request, exc):
    # Do not leak connection details to the browser.
    return JSONResponse(status_code=503, content={"detail": "Database is unavailable. Check that MySQL is running and .env is correct."})


@app.get("/")
def root():
    return {"status": "ok", "message": "Smart Placement Preparation Assistant API is running"}


@app.get("/questions", response_model=List[QuestionSummary])
def list_questions(category: Optional[str] = Query(None), difficulty: Optional[str] = Query(None)):
    return models.list_questions(category, difficulty)


@app.get("/questions/{question_id}", response_model=Question)
def get_question(question_id: int):
    question = models.get_question(question_id)
    if question is None:
        raise HTTPException(status_code=404, detail=f"Question {question_id} was not found.")
    return question


@app.post("/questions", response_model=Question, status_code=201)
def add_question(payload: QuestionCreate):
    new_id = models.create_question(payload)
    return models.get_question(new_id)


def _normalise(text: str) -> str:
    """Ignore case and extra spaces when comparing answers."""
    return re.sub(r"\s+", " ", text.strip().lower())


@app.post("/attempts", response_model=AttemptResult, status_code=201)
def create_attempt(payload: AttemptCreate):
    if payload.submitted_answer is None and not payload.completed:
        raise HTTPException(status_code=422, detail="Enter an answer or mark the question as completed.")
    if models.get_student(payload.student_id) is None:
        raise HTTPException(status_code=404, detail=f"Student {payload.student_id} was not found.")
    question = models.get_question(payload.question_id)
    if question is None:
        raise HTTPException(status_code=404, detail=f"Question {payload.question_id} was not found.")

    # Scoring rule: a typed answer is compared with the expected output (100 or 0).
    # Marking "completed" with no answer is self-reported and scores 100.
    if payload.submitted_answer is not None:
        correct = _normalise(payload.submitted_answer) == _normalise(question["expected_output"] or "")
        score, completed = (100.0, True) if correct else (0.0, False)
        message = "Correct! Well done." if correct else "Not quite. Check your output against the sample input and try again."
    else:
        score, completed = 100.0, True
        message = "Marked as completed."

    attempt_id = models.save_attempt(payload.student_id, payload.question_id, payload.submitted_answer, score, completed)
    return AttemptResult(attempt_id=attempt_id, score=score, completed=completed, message=message)


@app.get("/students/{student_id}/progress", response_model=Progress)
def student_progress(student_id: int):
    student = models.get_student(student_id)
    if student is None:
        raise HTTPException(status_code=404, detail=f"Student {student_id} was not found.")
    data = models.get_progress(student_id)
    return Progress(student_id=student_id, full_name=student["full_name"], **data)


@app.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest):
    reply, topic = get_reply(payload.message)
    return ChatResponse(reply=reply, matched_topic=topic)


# Optional convenience: also serve the frontend at http://127.0.0.1:8000/app/
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
if FRONTEND_DIR.is_dir():
    app.mount("/app", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
