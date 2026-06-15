"""SQLite CRUD. All functions use a module-level connection via get_db()."""

import sqlite3
import re
import threading
from pathlib import Path
from typing import Optional

from .config import DATA_DIR, DB_PATH

_local = threading.local()


def get_db() -> sqlite3.Connection:
    """Thread-local connection."""
    if not hasattr(_local, "conn") or _local.conn is None:
        _local.conn = sqlite3.connect(str(DB_PATH))
        _local.conn.row_factory = sqlite3.Row
        _local.conn.execute("PRAGMA journal_mode=WAL")
        _local.conn.execute("PRAGMA foreign_keys=ON")
    return _local.conn


def init_db():
    db = get_db()
    db.executescript("""
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            dir_name TEXT UNIQUE NOT NULL,
            created_at TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
            filename TEXT NOT NULL,
            original_name TEXT NOT NULL,
            file_type TEXT DEFAULT '',
            status TEXT DEFAULT 'pending',
            raw_dir TEXT,
            error_msg TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            qid TEXT UNIQUE NOT NULL,
            course_id INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
            source_file_id INTEGER REFERENCES files(id),
            qtype TEXT DEFAULT '',
            content TEXT NOT NULL,
            options TEXT,
            answer TEXT,
            explanation TEXT,
            knowledge_tags TEXT,
            difficulty INTEGER DEFAULT 1,
            created_at TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS knowledge_tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id INTEGER NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
            tag_name TEXT NOT NULL,
            UNIQUE(course_id, tag_name)
        );
    """)
    db.commit()
    # v0.2 additions — columns for chapter separation
    for alter in [
        "ALTER TABLE files ADD COLUMN chapters TEXT DEFAULT ''",
        "ALTER TABLE questions ADD COLUMN chapter_tags TEXT DEFAULT ''",
        "ALTER TABLE courses ADD COLUMN chapters TEXT DEFAULT ''",
    ]:
        try:
            db.execute(alter)
        except Exception:
            pass
    db.commit()


# ── Courses ──────────────────────────────────────────────────────────

def add_course(name: str, dir_name: str) -> int:
    db = get_db()
    cur = db.execute("INSERT INTO courses (name, dir_name) VALUES (?, ?)", (name, dir_name))
    db.commit()
    return cur.lastrowid


def get_courses() -> list[dict]:
    db = get_db()
    rows = db.execute("""
        SELECT c.*,
               (SELECT COUNT(*) FROM files WHERE course_id = c.id) AS file_count,
               (SELECT COUNT(*) FROM questions WHERE course_id = c.id) AS question_count
        FROM courses c ORDER BY c.id
    """).fetchall()
    return [dict(r) for r in rows]


def get_course(course_id: int) -> Optional[dict]:
    db = get_db()
    row = db.execute("SELECT * FROM courses WHERE id = ?", (course_id,)).fetchone()
    return dict(row) if row else None


def get_course_by_dir(dir_name: str) -> Optional[dict]:
    db = get_db()
    row = db.execute("SELECT * FROM courses WHERE dir_name = ?", (dir_name,)).fetchone()
    return dict(row) if row else None


def delete_course(course_id: int):
    db = get_db()
    db.execute("DELETE FROM courses WHERE id = ?", (course_id,))
    db.commit()


# ── Files ────────────────────────────────────────────────────────────

def add_file(course_id: int, filename: str, original_name: str) -> int:
    db = get_db()
    cur = db.execute(
        "INSERT INTO files (course_id, filename, original_name) VALUES (?, ?, ?)",
        (course_id, filename, original_name),
    )
    db.commit()
    return cur.lastrowid


def update_file_status(file_id: int, status: str, raw_dir: Optional[str] = None, error_msg: Optional[str] = None):
    db = get_db()
    db.execute(
        "UPDATE files SET status=?, raw_dir=COALESCE(?, raw_dir), error_msg=COALESCE(?, error_msg) WHERE id=?",
        (status, raw_dir, error_msg, file_id),
    )
    db.commit()


def get_file(file_id: int) -> Optional[dict]:
    db = get_db()
    row = db.execute("SELECT * FROM files WHERE id = ?", (file_id,)).fetchone()
    return dict(row) if row else None


def get_files(course_id: int) -> list[dict]:
    db = get_db()
    rows = db.execute("SELECT * FROM files WHERE course_id = ? ORDER BY id", (course_id,)).fetchall()
    return [dict(r) for r in rows]


def get_unparsed_file_ids(course_id: int, file_ids: list[int]) -> list[int]:
    """Return file ids from file_ids that are not yet parsed/failed."""
    if not file_ids:
        return []
    db = get_db()
    placeholders = ",".join("?" * len(file_ids))
    rows = db.execute(
        f"SELECT id FROM files WHERE course_id=? AND id IN ({placeholders}) AND status='pending'",
        [course_id, *file_ids],
    ).fetchall()
    return [r["id"] for r in rows]


# ── Questions ────────────────────────────────────────────────────────

_QBLOCK_RE = re.compile(
    r"### (Q\d+)\n(.*?)(?=\n### |\Z)", re.DOTALL
)


def parse_question_block(qid: str, block: str) -> Optional[dict]:
    def extract(pattern: str, default: str = "") -> str:
        m = re.search(pattern, block)
        return m.group(1).strip() if m else default

    qtype = extract(r"\*\*题型\*\*：(\S+)")
    diff_str = extract(r"\*\*难度\*\*：(\d+)", "1")
    source = extract(r"\*\*来源\*\*：(.+)")
    tags = extract(r"\*\*知识点\*\*：(.+)")
    answer = extract(r"\*\*答案\*\*：(.+)")
    explanation = extract(r"\*\*解析\*\*：(.+)")

    # content is everything between the header row and the first **field
    # We'll grab all text between the header fields and the first ** marker after the blank line
    lines = block.split("\n")
    content_lines = []
    in_header = True
    for line in lines:
        if in_header and line.startswith("**"):
            continue  # skip field lines in header
        if in_header and line.strip() == "":
            in_header = False
            continue
        if not in_header and line.startswith("**选项**"):
            continue
        if not in_header and (line.startswith("**答案**") or line.startswith("**解析**")):
            break
        if not in_header:
            content_lines.append(line)

    content = "\n".join(content_lines).strip()
    if not content:
        content = extract(r"(.*?)(?=\n\n\*\*|\Z)")  # fallback

    # options
    options = None
    opt_match = re.search(r"\*\*选项\*\*(.*?)(?=\*\*答案|\*\*解析|\Z)", block, re.DOTALL)
    if opt_match:
        opt_text = opt_match.group(1).strip()
        if opt_text:
            options = opt_text

    return {
        "qid": qid,
        "qtype": qtype,
        "content": content,
        "options": options,
        "answer": answer,
        "explanation": explanation,
        "knowledge_tags": tags,
        "difficulty": int(diff_str) if diff_str.isdigit() else 1,
    }


def sync_questions_from_md(course_id: int):
    """Full rebuild of questions + tags from question-bank.md."""
    course = get_course(course_id)
    if not course:
        return
    md_path = DATA_DIR / course["dir_name"] / "question-bank.md"
    if not md_path.exists():
        return

    md = md_path.read_text("utf-8")
    matches = _QBLOCK_RE.findall(md)

    questions = []
    tags: set[str] = set()
    for qid, block in matches:
        q = parse_question_block(qid, block)
        if q:
            questions.append(q)
            if q["knowledge_tags"]:
                for t in q["knowledge_tags"].split(","):
                    t = t.strip()
                    if t:
                        tags.add(t)

    db = get_db()
    try:
        db.execute("BEGIN")
        db.execute("DELETE FROM questions WHERE course_id = ?", (course_id,))
        db.execute("DELETE FROM knowledge_tags WHERE course_id = ?", (course_id,))

        for q in questions:
            db.execute(
                """INSERT INTO questions
                   (qid, course_id, qtype, content, options, answer, explanation, knowledge_tags, difficulty)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    q["qid"], course_id, q["qtype"], q["content"],
                    q["options"], q["answer"], q["explanation"],
                    q["knowledge_tags"], q["difficulty"],
                ),
            )

        for t in sorted(tags):
            db.execute(
                "INSERT OR IGNORE INTO knowledge_tags (course_id, tag_name) VALUES (?, ?)",
                (course_id, t),
            )
        db.execute("COMMIT")
    except Exception:
        db.execute("ROLLBACK")
        raise

# ── New annotation-based sync (replaces sync_questions_from_md) ────

_ANNOTATION_RE = re.compile(
    r"<!-- QUESTION: (.*?) -->\s*\n(.*?)\s*\n\s*<!-- QUESTION END -->", re.DOTALL
)

_ANSWER_RE = re.compile(r"\s*<!-- ANSWER -->\s*", re.DOTALL)
_EXPLANATION_RE = re.compile(r"\s*<!-- EXPLANATION -->\s*", re.DOTALL)


def _extract_kv(text: str, key: str, default: str = "") -> str:
    m = re.search(rf"{re.escape(key)}=(.+?)(?=\s+\w+=|\s*$)", text)
    return m.group(1).strip() if m else default


def _extract_field(text: str, pattern: str, default: str = "") -> str:
    m = re.search(pattern, text)
    return m.group(1).strip() if m else default


def parse_annotated_questions(text: str, source_label: str) -> list[dict]:
    """Extract questions from <!-- QUESTION: ... --> annotated markdown.

    Supports two formats:
    New: uses ``<!-- ANSWER -->`` / ``<!-- EXPLANATION -->`` section markers
    Old fallback: uses ``**答案**：`` / ``**解析**：`` inline fields
    """
    questions = []
    for match in _ANNOTATION_RE.finditer(text):
        header = match.group(1)
        body = match.group(2).strip()

        qtype = _extract_kv(header, "qtype")
        chapter = _extract_kv(header, "chapter", "")
        tags = _extract_kv(header, "tags", "")
        diff_str = _extract_kv(header, "difficulty", "1")

        difficulty = 1
        try:
            difficulty = int(diff_str)
        except ValueError:
            pass

        # Try new format: split by <!-- ANSWER --> and <!-- EXPLANATION -->
        ans_match = list(_ANSWER_RE.finditer(body))
        expl_match = list(_EXPLANATION_RE.finditer(body))

        if ans_match or expl_match:
            # New format — use start() for content boundary, end() for section starts
            ans_start = ans_match[0].start() if ans_match else len(body)
            ans_end = ans_match[0].end() if ans_match else len(body)
            expl_start = expl_match[0].start() if expl_match else len(body)
            expl_end = expl_match[0].end() if expl_match else len(body)

            content = body[:min(ans_start, expl_start)].strip()
            answer = ""
            explanation = ""

            if ans_match and ans_end < len(body):
                if expl_match and expl_start > ans_end:
                    answer = body[ans_end:expl_start].strip()
                    explanation = body[expl_end:].strip()
                else:
                    answer = body[ans_end:].strip()

            if expl_match and not ans_match:
                explanation = body[expl_end:].strip()
        else:
            # Old format fallback: **答案**： / **解析**：
            content = _strip_trailing_fields(body, ["**答案**", "**解析**"])
            answer = _extract_field(body, r"\*\*答案\*\*[：:] *(.+)")
            explanation = _extract_field(body, r"\*\*解析\*\*[：:] *(.+)")

        questions.append({
            "qtype": qtype,
            "content": content,
            "options": None,
            "answer": answer or "",
            "knowledge_tags": tags,
            "chapter_tags": chapter,
            "source": source_label,
            "explanation": explanation or "",
            "difficulty": difficulty,
        })
    return questions


def _strip_trailing_fields(text: str, field_names: list[str]) -> str:
    """Remove lines starting with any of field_names (and following lines) from the end of text."""
    lines = text.split("\n")
    end = len(lines)
    for i in range(len(lines) - 1, -1, -1):
        stripped = lines[i].strip()
        if any(stripped.startswith(f + "：") or stripped.startswith(f + ":") for f in field_names):
            end = i
        elif stripped == "" and i < end - 1:
            end = i
        elif stripped == "":
            continue
        else:
            break
    return "\n".join(lines[:end]).strip()


def sync_all_questions(course_id: int) -> int:
    """Scan raw/*/output files, extract annotated questions, deduplicate, assign QIDs, write to SQLite.
    Returns question count.
    """
    course = get_course(course_id)
    if not course:
        return 0
    course_dir = DATA_DIR / course["dir_name"]
    raw_base = course_dir / "raw"
    if not raw_base.exists():
        return 0

    all_questions: list[dict] = []
    all_tags: set[str] = set()
    raw_dirs = sorted(
        [d for d in raw_base.iterdir() if d.is_dir()],
        key=lambda d: int(d.name) if d.name.isdigit() else d.name,
    )

    for raw_dir in raw_dirs:
        # Try output.md first, fall back to output (old format)
        output_file = raw_dir / "output.md"
        if not output_file.exists():
            output_file = raw_dir / "output"
        if not output_file.exists():
            continue
        text = output_file.read_text("utf-8")
        questions = parse_annotated_questions(text, raw_dir.name)

        # Track source file and chapter info
        file_id = int(raw_dir.name) if raw_dir.name.isdigit() else None
        file_chapters = ""
        if file_id:
            try:
                db = get_db()
                row = db.execute("SELECT chapters FROM files WHERE id=?", (file_id,)).fetchone()
                if row and row["chapters"]:
                    file_chapters = row["chapters"]
            except Exception:
                pass

        # Inject source_file_id and chapter info
        for q in questions:
            q["source_file_id"] = file_id
            if not q.get("chapter_tags") and file_chapters:
                q["chapter_tags"] = file_chapters

        # Rewrite image paths: ![](images/xxx.jpg) → ![](/api/assets/{dir}/images/xxx.jpg)
        course_dir_name = course["dir_name"]
        for q in questions:
            q["content"] = re.sub(
                r'!\[\]\(images/([^)]+)\)',
                rf'![](/api/assets/{course_dir_name}/images/\1)',
                q["content"],
            )
            if q["answer"]:
                q["answer"] = re.sub(
                    r'!\[\]\(images/([^)]+)\)',
                    rf'![](/api/assets/{course_dir_name}/images/\1)',
                    q["answer"],
                )

        # Strip leading question numbers like "1. ", "2、", "3 ", "(1)" from content
        for q in questions:
            q["content"] = re.sub(
                r'^\s*(?:\d+\s*[.、）\)]\s*|\d+\s+|\(\d+\)|（\d+）|[(（]\d+[)）])\s*',
                '', q["content"], count=1
            )

        all_questions.extend(questions)

    # Deduplicate by first 120 chars of content
    seen: set[str] = set()
    unique: list[dict] = []
    for q in all_questions:
        key = q["content"].replace(" ", "")[:120]
        if key and key not in seen:
            seen.add(key)
            unique.append(q)
            if q["knowledge_tags"]:
                for t in q["knowledge_tags"].split(","):
                    t = t.strip()
                    if t:
                        all_tags.add(t)

    # Assign QIDs sequentially
    for i, q in enumerate(unique, 1):
        q["qid"] = f"Q{i:04d}"

    # Write to SQLite
    db = get_db()
    try:
        db.execute("BEGIN")
        db.execute("DELETE FROM questions WHERE course_id = ?", (course_id,))
        db.execute("DELETE FROM knowledge_tags WHERE course_id = ?", (course_id,))

        for q in unique:
            db.execute(
                """INSERT INTO questions
                   (qid, course_id, source_file_id, qtype, content, options, answer, explanation, knowledge_tags, chapter_tags, difficulty)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    q["qid"], course_id, q.get("source_file_id"), q["qtype"], q["content"],
                    q["options"], q["answer"], q["explanation"],
                    q["knowledge_tags"], q.get("chapter_tags", ""), q["difficulty"],
                ),
            )

        for t in sorted(all_tags):
            db.execute(
                "INSERT OR IGNORE INTO knowledge_tags (course_id, tag_name) VALUES (?, ?)",
                (course_id, t),
            )
        db.execute("COMMIT")
    except Exception:
        db.execute("ROLLBACK")
        raise

    return len(unique)


def get_questions(
    course_id: int,
    tag: Optional[str] = None,
    qtype: Optional[str] = None,
    limit: int = 200,
    offset: int = 0,
) -> list[dict]:
    db = get_db()
    clauses = ["course_id = ?"]
    params: list = [course_id]
    if tag:
        clauses.append("knowledge_tags LIKE ?")
        params.append(f"%{tag}%")
    if qtype:
        clauses.append("qtype = ?")
        params.append(qtype)
    sql = f"SELECT * FROM questions WHERE {' AND '.join(clauses)} ORDER BY qid LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    rows = db.execute(sql, params).fetchall()
    return [dict(r) for r in rows]


def get_question_by_qid(course_id: int, qid: str) -> Optional[dict]:
    db = get_db()
    row = db.execute(
        "SELECT * FROM questions WHERE course_id = ? AND qid = ?", (course_id, qid)
    ).fetchone()
    return dict(row) if row else None


def get_knowledge_tags(course_id: int) -> list[str]:
    db = get_db()
    rows = db.execute(
        "SELECT tag_name FROM knowledge_tags WHERE course_id = ? ORDER BY tag_name", (course_id,)
    ).fetchall()
    return [r["tag_name"] for r in rows]


def get_chapters(course_id: int) -> list[str]:
    db = get_db()
    rows = db.execute(
        "SELECT chapter_tags FROM questions WHERE course_id=? AND chapter_tags IS NOT NULL AND chapter_tags != '' ORDER BY chapter_tags",
        (course_id,),
    ).fetchall()
    result = set()
    for r in rows:
        if not r["chapter_tags"]:
            continue
        for ch in r["chapter_tags"].split(","):
            ch = ch.strip()
            if ch:
                result.add(ch)
    return sorted(result)
