"""Export exam-killer to a full SPA static site for GitHub Pages deployment."""

import argparse
import json
import re
import shutil
import sqlite3
from pathlib import Path

SITE_DIR = Path(__file__).resolve().parent.parent / "_site"
DATA_DIR = Path("data")
DB_PATH = Path("exam_killer.db")


def esc_html(text: str) -> str:
    return (
        (text or "")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def get_db() -> sqlite3.Connection:
    db = sqlite3.connect(str(DB_PATH))
    db.row_factory = sqlite3.Row
    return db


def export_all():
    db = get_db()
    courses = db.execute(
        "SELECT c.*, (SELECT COUNT(*) FROM questions WHERE course_id=c.id) AS question_count "
        "FROM courses c ORDER BY c.name"
    ).fetchall()
    if not courses:
        print("No courses found.")
        return

    if SITE_DIR.exists():
        shutil.rmtree(SITE_DIR)
    SITE_DIR.mkdir(parents=True)

    # Copy frontend assets
    assets_js = SITE_DIR / "assets" / "js"
    assets_css = SITE_DIR / "assets" / "css"
    assets_js.mkdir(parents=True)
    assets_css.mkdir(parents=True)
    for f in sorted(Path("frontend/js").iterdir()):
        if f.suffix == ".js":
            shutil.copy(f, assets_js / f.name)
    css_src = Path("frontend/css/style.css")
    if css_src.exists():
        shutil.copy(css_src, assets_css / "style.css")

    course_map = {c["id"]: c["dir_name"] for c in courses}
    courses_dir = SITE_DIR / "courses"
    courses_dir.mkdir()
    course_list = []

    for c in courses:
        cid = c["id"]
        cslug = c["dir_name"]
        course_dir = courses_dir / str(cid)
        course_dir.mkdir()

        questions = db.execute(
            "SELECT q.*, f.original_name AS source_file_name "
            "FROM questions q LEFT JOIN files f ON q.source_file_id = f.id "
            "WHERE q.course_id=? ORDER BY q.qid",
            (cid,),
        ).fetchall()
        qlist = []
        for q in questions:
            qd = dict(q)
            for field in ("content", "answer", "explanation"):
                if qd.get(field):
                    qd[field] = qd[field].replace(
                        f"/api/assets/{cslug}/images/", "images/"
                    )
            qlist.append(qd)
        (course_dir / "questions.json").write_text(
            json.dumps(qlist, ensure_ascii=False, indent=2), encoding="utf-8"
        )

        tags = db.execute(
            "SELECT tag_name FROM knowledge_tags WHERE course_id=? ORDER BY tag_name",
            (cid,),
        ).fetchall()
        (course_dir / "tags.json").write_text(
            json.dumps([t["tag_name"] for t in tags], ensure_ascii=False),
            encoding="utf-8",
        )

        ch_rows = db.execute(
            "SELECT DISTINCT chapter_tags FROM questions WHERE course_id=? AND chapter_tags IS NOT NULL AND chapter_tags != ''",
            (cid,),
        ).fetchall()
        chapters = set()
        for r in ch_rows:
            for ch in r["chapter_tags"].split(","):
                ch = ch.strip()
                if ch:
                    chapters.add(ch)
        (course_dir / "chapters.json").write_text(
            json.dumps(sorted(chapters), ensure_ascii=False), encoding="utf-8"
        )

        files = db.execute(
            "SELECT id, original_name FROM files WHERE course_id=? ORDER BY original_name",
            (cid,),
        ).fetchall()
        (course_dir / "files.json").write_text(
            json.dumps(
                [{"id": f["id"], "filename": f["original_name"]} for f in files],
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        (course_dir / "course.json").write_text(
            json.dumps(
                {
                    "id": cid,
                    "name": c["name"],
                    "dir_name": cslug,
                    "question_count": c["question_count"],
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        course_list.append(
            {
                "id": cid,
                "name": c["name"],
                "dir_name": cslug,
                "question_count": c["question_count"],
                "created_at": c["created_at"],
            }
        )

        # Review guide chapters
        rg_src = Path(str(DATA_DIR)) / cslug / "review-guide"
        rg_dst = course_dir / "review-guide"
        rg_dst.mkdir(exist_ok=True)
        rg_chapters = []
        if rg_src.exists():
            for md_file in sorted(rg_src.iterdir()):
                if md_file.suffix != ".md":
                    continue
                title = md_file.stem[3:] if md_file.stem[:2].isdigit() else md_file.stem
                html_content = md_to_html(md_file.read_text(encoding="utf-8"), cid)
                ch_file = rg_dst / f"{md_file.stem}.html"
                ch_file.write_text(html_content, encoding="utf-8")
                rg_chapters.append({"filename": f"{md_file.stem}.html", "title": title})
        (course_dir / "review.json").write_text(
            json.dumps(rg_chapters, ensure_ascii=False), encoding="utf-8"
        )

    # Copy images
    img_dir = SITE_DIR / "images"
    img_dir.mkdir()
    seen, img_count = set(), 0
    for cslug in course_map.values():
        for raw_dir in (
            sorted((Path(str(DATA_DIR)) / cslug / "raw").iterdir())
            if (Path(str(DATA_DIR)) / cslug / "raw").exists()
            else []
        ):
            img_path = raw_dir / "images"
            if img_path.exists():
                for img in img_path.iterdir():
                    if img.is_file() and img.name not in seen:
                        seen.add(img.name)
                        shutil.copy2(img, img_dir / img.name)
                        img_count += 1
    print(f"Copied {img_count} images")

    # Write static API adapter
    write_static_api(course_map)
    # Write SPA index
    write_spa_index(course_list)
    db.close()
    print(f"Done. Site at {SITE_DIR}")


def write_static_api(course_map: dict):
    mapping = json.dumps(course_map, ensure_ascii=False)
    js = f"""\
(function() {{
var CM = {mapping};
function cd(id) {{ var d = CM[id]; return d ? 'courses/' + id : null; }}
function url(p) {{
  var m = p.match(/^\\/api\\/courses\\/(\\d+)\\/(\\w+)/);
  if (!m) return null;
  var dir = cd(m[1]); if (!dir) return null;
  if (m[2] === 'review' && p.includes('/review/chapters/')) return dir + '/review-guide/' + p.split('/').pop();
  if (m[2] === 'review') return dir + '/review.json';
  if (m[2] === 'chapters' || m[2] === 'tags' || m[2] === 'files' || m[2] === 'questions') return dir + '/' + m[2] + '.json';
  return null;
}}
window.API = {{
  get: function(p) {{
    var u = url(p);
    if (u) return fetch(u).then(function(r) {{ if (!r.ok) throw new Error(r.status + ' ' + u); return r.json(); }});
    return Promise.reject(new Error('No mapping: ' + p));
  }},
  post: function() {{ return Promise.reject(new Error('Read-only')); }},
  put: function() {{ return Promise.reject(new Error('Read-only')); }},
  del: function() {{ return Promise.reject(new Error('Read-only')); }},
  upload: function() {{ return Promise.reject(new Error('Read-only')); }},
}};
var s = document.createElement('style');
s.textContent = '.upload-tab,.edit-q,.save-q,.cancel-q,.delete-q,#btn-delete-course,#btn-export-rg,.topbar-link[href$=\"/settings\"]{{display:none!important}}';
document.head.appendChild(s);
}})();
"""
    (SITE_DIR / "static-api.js").write_text(js, encoding="utf-8")


def write_spa_index(course_list: list):
    src = Path("frontend/index.html")
    if not src.exists():
        return
    html = src.read_text(encoding="utf-8")
    # Inject static API adapter before first script
    html = html.replace(
        '<script src="js/api.js"></script>',
        "<script>window.__STATIC_COURSES__ = "
        + json.dumps(course_list, ensure_ascii=False)
        + ';</script>\n<script src="static-api.js"></script>\n<script src="js/api.js"></script>',
    )
    # Hide settings link
    html = html.replace('href="#/settings"', 'href="#/settings" style="display:none"')
    (SITE_DIR / "index.html").write_text(html, encoding="utf-8")


def md_to_html(md: str, cid: int) -> str:
    """Convert review-guide markdown to pre-rendered HTML."""
    # Image: images/xxx.jpg → ../../images/xxx.jpg
    md = re.sub(r"!\[\]\(images/([^)]+)\)", r"![](../../images/\1)", md)
    md = re.sub(
        r"\$\$(.+?)\$\$",
        r'<span class="katex-tex" data-display="true">\1</span>',
        md,
        flags=re.DOTALL,
    )
    md = re.sub(
        r"\$(.+?)\$", r'<span class="katex-tex" data-display="false">\1</span>', md
    )
    lines = md.split("\n")
    html = []
    i = 0
    while i < len(lines):
        line = lines[i]
        m = re.match(r"^(#{1,6})\s+(.+)$", line)
        if m:
            html.append(f"<h{m[1]}>{inline_html(m[2])}</h{m[1]}>")
            i += 1
            continue
        if re.match(r"^---+\s*$", line):
            html.append("<hr>")
            i += 1
            continue
        if line.startswith("> "):
            ql = []
            while i < len(lines) and lines[i].startswith("> "):
                ql.append(lines[i][2:])
                i += 1
            html.append("<blockquote>" + inline_html("<br>".join(ql)) + "</blockquote>")
            continue
        if line.startswith("```"):
            cl = []
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                cl.append(lines[i])
                i += 1
            i += 1
            code = esc_html("\n".join(cl))
            lang = re.match(r"```(\w*)", line)
            html.append(
                f'<pre><code class="language-{lang[1] or ""}">{code}</code></pre>'
            )
            continue
        if not line.strip():
            i += 1
            continue
        pl = []
        while (
            i < len(lines)
            and lines[i].strip()
            and not lines[i].startswith("#")
            and not lines[i].startswith("```")
            and not lines[i].startswith("> ")
        ):
            pl.append(lines[i])
            i += 1
        if pl:
            html.append("<p>" + inline_html("<br>".join(pl)) + "</p>")
    return "\n".join(html)


def inline_html(text: str) -> str:
    text = esc_html(text)
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", default=str(SITE_DIR))
    args = parser.parse_args()
    SITE_DIR = Path(args.out_dir)
    export_all()
