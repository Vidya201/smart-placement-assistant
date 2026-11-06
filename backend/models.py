"""Database functions. All SQL uses %s placeholders (parameterized queries) so user
input is never glued into the SQL string, which prevents SQL injection."""
from database import get_cursor


def list_questions(category=None, difficulty=None):
    sql = "SELECT question_id, title, category, difficulty FROM questions WHERE 1=1"
    params = []
    if category:
        sql += " AND category = %s"
        params.append(category)
    if difficulty:
        sql += " AND difficulty = %s"
        params.append(difficulty)
    sql += " ORDER BY question_id"
    with get_cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchall()


def get_question(question_id):
    with get_cursor() as cur:
        cur.execute("SELECT * FROM questions WHERE question_id = %s", (question_id,))
        return cur.fetchone()


def create_question(q):
    with get_cursor() as cur:
        cur.execute(
            "INSERT INTO questions (title, category, difficulty, description, sample_input, expected_output) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (q.title, q.category, q.difficulty, q.description, q.sample_input, q.expected_output),
        )
        return cur.lastrowid


def get_student(student_id):
    with get_cursor() as cur:
        cur.execute("SELECT * FROM students WHERE student_id = %s", (student_id,))
        return cur.fetchone()


def save_attempt(student_id, question_id, answer, score, completed):
    with get_cursor() as cur:
        cur.execute(
            "INSERT INTO attempts (student_id, question_id, submitted_answer, score, completed) "
            "VALUES (%s, %s, %s, %s, %s)",
            (student_id, question_id, answer, score, completed),
        )
        return cur.lastrowid


def get_progress(student_id):
    with get_cursor() as cur:
        # Same idea as: SELECT COUNT(*), COUNT(DISTINCT question_id), AVG(score) ... WHERE student_id = ?
        cur.execute(
            "SELECT COUNT(*) AS total_attempts, COUNT(DISTINCT question_id) AS questions_attempted, "
            "COALESCE(AVG(score), 0) AS average_score FROM attempts WHERE student_id = %s",
            (student_id,),
        )
        summary = cur.fetchone()
        cur.execute(
            "SELECT COUNT(DISTINCT question_id) AS n FROM attempts WHERE student_id = %s AND completed = TRUE",
            (student_id,),
        )
        summary["questions_completed"] = cur.fetchone()["n"]
        cur.execute("SELECT COUNT(*) AS n FROM questions")
        summary["total_questions"] = cur.fetchone()["n"]
        cur.execute(
            "SELECT a.attempt_id, q.title, a.score, a.completed, a.attempted_at "
            "FROM attempts a JOIN questions q ON q.question_id = a.question_id "
            "WHERE a.student_id = %s ORDER BY a.attempted_at DESC, a.attempt_id DESC LIMIT 10",
            (student_id,),
        )
        summary["recent_attempts"] = cur.fetchall()
        summary["average_score"] = round(float(summary["average_score"]), 2)
        return summary
