import sqlite3

db = sqlite3.connect("exam_killer.db")

# Fix Q0029
db.execute(
    "UPDATE questions SET content=? WHERE qid=?",
    ('求 $\\neg(\\neg p \\land q) \\rightarrow r$ 的主析取范式。', 'Q0029')
)

# Fix Q0035  
db.execute(
    "UPDATE questions SET content=? WHERE qid=?",
    ('证明： $\\neg(\\neg p \\rightarrow q)$ 逻辑值含 $\\neg p$ 。', 'Q0035')
)

db.commit()
db.close()
print("Done")
