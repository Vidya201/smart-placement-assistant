# Project Report: Smart Placement Preparation Assistant

## 1. Objective
Help students practise Python interview questions, store attempts, view progress and get quick answers from a rule-based chatbot.

## 2. Architecture
Browser (HTML/CSS/JS) -> Fetch API, JSON -> FastAPI (Pydantic validation, question/attempt logic, chatbot) -> SQL -> MySQL.
The frontend only displays data, FastAPI processes requests, `chatbot.py` selects replies, and MySQL stores persistent data.

## 3. Database design
Three tables: `students`, `questions`, `attempts`. `attempts` has foreign keys to both, so one student can have many attempts and one question can be attempted many times. Scores use `DECIMAL(5,2)`.

## 4. Rule-based chatbot vs LLM
Rule-based: keyword -> fixed reply, predictable, free, offline, but cannot handle unseen questions. LLM: generates answers from a trained model, flexible but costs money, needs an API key and can be wrong. Replace `get_reply()` to switch; keep the key on the backend.

## 5. Testing
See the checklist in README.md. Covered: normal use, empty input, invalid IDs, stopped backend, stopped database, persistence after refresh.

## 6. Security
Parameterized SQL, backend validation with Pydantic, secrets in `.env` (git-ignored), generic database error message, sample data only.

## 7. Limitations and future work
No login, text-match scoring (no code execution), fixed chatbot topics. Future: admin page, timed quizzes, topic suggestions from scores, optional LLM.
