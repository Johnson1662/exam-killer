import sqlite3, re

db = sqlite3.connect("exam_killer.db")
rows = db.execute("SELECT id, content FROM questions WHERE course_id=7 AND content LIKE '%(-p%'").fetchall()

for qid, content in rows:
    # Replace math-mode hyphens used as negation
    new_content = content
    # Specific case: $-(-p -> $\\neg(\\neg p
    new_content = new_content.replace("$-( -p", "$\\neg( \\neg p")
    new_content = new_content.replace("$-(-p", "$\\neg(\\neg p")
    new_content = new_content.replace("$ -(-p", "$ \\neg(\\neg p")
    
    if new_content != content:
        db.execute("UPDATE questions SET content=? WHERE id=?", (new_content, qid))
        print(f"Fixed Q{qid}")
    else:
        print(f"No match Q{qid}: {content[:60]}")

db.commit()
db.close()
print("Done")
