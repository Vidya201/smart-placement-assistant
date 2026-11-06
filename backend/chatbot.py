"""Rule-based chatbot. It looks for keywords and returns a PREDEFINED answer.
This is NOT Generative AI: there is no model, and it cannot answer anything outside the rules.

To use a real LLM later, replace the body of get_reply() with an API call made on the
backend (keep the API key in .env). The /chat endpoint and the frontend stay unchanged.
"""
import re

# Order matters: specific topics come first, the greeting comes last.
RULES = [
    ("help", [r"help", r"topics", r"what can you do"],
     "I can answer basic questions about: Python, REST APIs, FastAPI, MySQL/databases and "
     "interview preparation. Try: 'What is FastAPI?' or 'How do I prepare for an interview?'"),
    ("fastapi", [r"fastapi"],
     "FastAPI is a modern Python framework for building APIs. You write normal Python functions, "
     "FastAPI turns them into HTTP endpoints, validates data with Pydantic and creates interactive "
     "docs at /docs automatically."),
    ("rest api", [r"rest api", r"api", r"rest", r"endpoint"],
     "A REST API lets programs talk over HTTP using JSON. Common methods: GET (read), POST (create), "
     "PUT/PATCH (update) and DELETE (remove). Each URL, like /questions/3, identifies a resource."),
    ("mysql", [r"mysql", r"database", r"sql", r"table"],
     "MySQL is a relational database. Data lives in tables made of rows and columns, and tables are "
     "linked with keys (for example attempts.student_id points to students.student_id). You query "
     "it with SQL such as SELECT, INSERT, UPDATE and DELETE."),
    ("python", [r"python"],
     "Python is a beginner-friendly, general-purpose programming language used for web backends, "
     "data analysis, automation and AI. Interviews often test strings, lists, dictionaries and functions."),
    ("interview", [r"interview", r"placement", r"prepare", r"practice", r"practise"],
     "To practise: solve a few questions daily, say your approach out loud before coding, test with "
     "small inputs, and review mistakes. Use the Questions page here and track your score on Progress. "
     "Treat my tips as suggestions, not guaranteed interview advice."),
    ("greeting", [r"hello", r"hi", r"hey"],
     "Hello! I'm the placement assistant. Ask me about Python, REST APIs, FastAPI, MySQL or interview "
     "practice. Type 'help' to see all topics."),
]

FALLBACK = ("I don't have a predefined answer for that. I can help with: Python, REST API, FastAPI, "
            "MySQL/database and interview practice. Type 'help' for examples.")


def get_reply(message: str):
    """Returns (reply_text, matched_topic or None)."""
    text = message.lower()
    for topic, patterns, reply in RULES:
        for p in patterns:
            if re.search(rf"\b{p}\b", text):  # whole-word match so 'hi' doesn't match 'this'
                return reply, topic
    return FALLBACK, None
