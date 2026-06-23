"""Export exam-killer data to a static site for GitHub Pages deployment.

Usage:
    python scripts/export_static.py [--out-dir _site]

Reads exam_killer.db, generates pre-rendered HTML + JSON data files.
The output directory can be served by any static host.
"""

import argparse
import json
import re
import shutil
import sqlite3
import sys
from pathlib import Path

SITE_DIR = Path(__file__).resolve().parent.parent / "_site"
DATA_DIR = Path("data")
DB_PATH = Path("exam_killer.db")

# ── helpers ──────────────────────────────────────────────────────────


def slugify(text: str) -> str:
    return re.sub(r"[^a-zA-Z0-9\u4e00-\u9fff_-]", "_", text).strip("_") or "course"


def esc_html(text: str) -> str:
    return (
        (text or "")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def icon_svg(name: str) -> str:
    """Minimal SVG placeholder for Lucide icons (just returns a placeholder)."""
    return f'<i data-lucide="{name}"></i>'


# ── HTML templates ───────────────────────────────────────────────────

HTML_SHELL = """\
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:opsz@14..32&family=Noto+Sans+SC:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
<link rel="stylesheet" href="{base}/assets/css/style.css">
</head>
<body>
<div id="app" class="container" style="padding-top:24px;padding-bottom:80px;">
{content}
</div>
<script src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<script src="https://unpkg.com/lucide@latest"></script>
<script>
lucide.createIcons();
// Auto-render KaTeX
document.querySelectorAll('.katex-tex').forEach(function(el) {{
    try {{ katex.render(el.textContent, el, {{ displayMode: el.dataset.display === 'true', throwOnError: false }}); }} catch(e) {{}}
}});
</script>
</body>
</html>"""

COURSE_INDEX = """\
<h1>{course_name}</h1>
<div class="tabs" style="margin-top:24px;">
  <button class="tab active" onclick="showTab('bank')">题库</button>
  <button class="tab" onclick="showTab('review')">复习指南</button>
</div>
<div id="tab-bank" class="tab-content">{bank_html}</div>
<div id="tab-review" class="tab-content" style="display:none;">{review_html}</div>
<script>
var _questions = {questions_json};
function showTab(name) {{
  document.querySelectorAll('.tab-content').forEach(function(el) {{ el.style.display = 'none'; }});
  document.getElementById('tab-' + name).style.display = '';
  document.querySelectorAll('.tab').forEach(function(el) {{ el.classList.remove('active'); }});
  document.querySelector('.tab[onclick*=\"' + name + '\"]').classList.add('active');
}}
</script>"""

# ── data reading ─────────────────────────────────────────────────────


def get_db() -> sqlite3.Connection:
    db = sqlite3.connect(str(DB_PATH))
    db.row_factory = sqlite3.Row
    return db


def load_courses(db):
    return db.execute(
        "SELECT c.*, (SELECT COUNT(*) FROM questions WHERE course_id=c.id) AS question_count "
        "FROM courses c ORDER BY c.name"
    ).fetchall()


def load_questions(db, course_id):
    return db.execute(
        "SELECT q.*, f.original_name AS source_file_name "
        "FROM questions q LEFT JOIN files f ON q.source_file_id = f.id "
        "WHERE q.course_id=? ORDER BY q.qid",
        (course_id,),
    ).fetchall()


def load_chapters(db, course_id):
    rows = db.execute(
        "SELECT chapter_tags FROM questions WHERE course_id=? AND chapter_tags IS NOT NULL AND chapter_tags != ''",
        (course_id,),
    ).fetchall()
    seen = set()
    result = []
    for r in rows:
        for ch in r["chapter_tags"].split(","):
            ch = ch.strip()
            if ch and ch not in seen:
                seen.add(ch)
                result.append(ch)
    return result


def load_knowledge_tags(db, course_id):
    rows = db.execute(
        "SELECT tag_name FROM knowledge_tags WHERE course_id=? ORDER BY tag_name",
        (course_id,),
    ).fetchall()
    return [r["tag_name"] for r in rows]


def load_review_guides(course_dir):
    guide_dir = Path(str(DATA_DIR)) / course_dir / "review-guide"
    chapters = []
    if guide_dir.exists():
        for f in sorted(guide_dir.iterdir()):
            if f.suffix == ".md":
                title = f.stem[3:] if f.stem[:2].isdigit() else f.stem
                chapters.append(
                    {"filename": f.name, "title": title, "size": f.stat().st_size}
                )
    return chapters


def render_markdown_to_html(text: str) -> str:
    """Minimal markdown → HTML for static export (without KaTeX rendering).
    Full rendering happens client-side via KaTeX + marked.
    """
    if not text:
        return ""
    # Escape HTML first, then convert markdown
    # Store LaTeX for client-side rendering
    # Replace $$...$$ and $...$ with katex-tex spans
    text = re.sub(
        r"\$\$(.+?)\$\$",
        r'<span class="katex-tex" data-display="true">\1</span>',
        text,
        flags=re.DOTALL,
    )
    text = re.sub(
        r"\$(.+?)\$", r'<span class="katex-tex" data-display="false">\1</span>', text
    )
    # Basic markdown: paragraphs, bold, italic, newlines
    paragraphs = []
    for para in text.split("\n\n"):
        para = para.strip()
        if not para:
            continue
        # Inline formatting
        para = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", para)
        para = re.sub(r"\*(.+?)\*", r"<em>\1</em>", para)
        para = re.sub(r"\n", r"<br>", para)
        paragraphs.append(f"<p>{para}</p>")
    return "\n".join(paragraphs)


# ── export functions ─────────────────────────────────────────────────


def export_all():
    db = get_db()
    courses = load_courses(db)

    if not courses:
        print("No courses found in database.")
        return

    # Clean output directory
    if SITE_DIR.exists():
        shutil.rmtree(SITE_DIR)
    SITE_DIR.mkdir(parents=True)

    # Copy frontend assets
    assets_dir = SITE_DIR / "assets"
    (assets_dir / "css").mkdir(parents=True)
    (assets_dir / "js").mkdir(parents=True)

    # Copy CSS
    css_src = Path("frontend/css/style.css")
    if css_src.exists():
        shutil.copy(css_src, assets_dir / "css" / "style.css")

    # Generate course listing (index.html)
    course_list_html = _render_course_list(courses)
    _write_page("index.html", "Exam-Killer · 期末复习资料", course_list_html)

    # 404.html for SPA fallback
    _write_page(
        "404.html",
        "页面未找到",
        '<h2>404</h2><p>页面未找到</p><a href="{base}/index.html">返回首页</a>',
    )

    # Generate per-course pages
    for course in courses:
        export_course(db, course)

    # Copy images
    copy_images()

    db.close()
    print(f"\nDone. Site generated at {SITE_DIR}")


def _render_course_list(courses):
    items = []
    for c in courses:
        items.append(
            f"""\
<div class="course-card" onclick="location.href='{slugify(c['name'])}/'">
  <h3>{esc_html(c['name'])}</h3>
  <p class="text-muted">{c['question_count']} 道题</p>
</div>"""
        )
    return f"""\
<h1>Exam-Killer</h1>
<p class="text-muted" style="margin-bottom:32px;">期末复习资料</p>
<div class="course-grid">{''.join(items)}</div>"""


def export_course(db, course):
    cid = course["id"]
    cname = course["name"]
    cslug = slugify(cname)
    course_dir = SITE_DIR / cslug
    course_dir.mkdir(parents=True)
    course_data_dir = Path(str(DATA_DIR)) / course["dir_name"]

    # Load data
    questions = load_questions(db, cid)
    tags = load_knowledge_tags(db, cid)
    chapters = load_chapters(db, cid)
    review_chapters = load_review_guides(course["dir_name"])

    # Generate question bank HTML (reusable with JS for filtering)
    questions_data = []
    for q in questions:
        qd = {
            "qid": q["qid"],
            "qtype": q["qtype"] or "",
            "content": (q["content"] or "").replace(
                "/api/assets/{0}/images/".format(course["dir_name"]), "../images/"
            ),
            "answer": (q["answer"] or "").replace(
                "/api/assets/{0}/images/".format(course["dir_name"]), "../images/"
            ),
            "explanation": (q["explanation"] or "").replace(
                "/api/assets/{0}/images/".format(course["dir_name"]), "../images/"
            ),
            "knowledge_tags": q["knowledge_tags"] or "",
            "chapter_tags": q["chapter_tags"] or "",
            "difficulty": q["difficulty"] or 1,
            "source_file_name": q["source_file_name"] or "",
        }
        questions_data.append(qd)

    # Write questions.json
    (course_dir / "questions.json").write_text(
        json.dumps(questions_data, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # Write tags.json
    (course_dir / "tags.json").write_text(
        json.dumps(tags, ensure_ascii=False), encoding="utf-8"
    )

    # Write chapters.json
    (course_dir / "chapters.json").write_text(
        json.dumps(chapters, ensure_ascii=False), encoding="utf-8"
    )

    # Generate review guide HTML pages
    review_html_parts = []
    rg_dir = course_dir / "review-guide"
    rg_dir.mkdir(exist_ok=True)
    review_data_dir = course_data_dir / "review-guide"
    if review_data_dir.exists():
        for md_file in sorted(review_data_dir.iterdir()):
            if md_file.suffix != ".md":
                continue
            title = md_file.stem[3:] if md_file.stem[:2].isdigit() else md_file.stem
            md_content = md_file.read_text(encoding="utf-8")
            # Basic MD to HTML (images paths rewritten)
            html_content = _md_to_html(md_content, cslug)
            # Write chapter page
            review_html = f"""\
<div class="chapter-content">
{html_content}
</div>"""
            _write_page(
                f"{cslug}/review-guide/{md_file.stem}.html",
                f"{title} - {cname}",
                review_html,
                base="../..",
            )
            review_html_parts.append(
                f'<div class="chapter-item" onclick="location.href=\'review-guide/{md_file.stem}.html\'"><span class="chapter-title">{esc_html(title)}</span></div>'
            )

    # Build course index page
    review_nav = (
        "".join(review_html_parts)
        if review_html_parts
        else '<p class="text-muted">暂无复习指南</p>'
    )
    bank_html = _build_question_bank_html(cslug)
    content = COURSE_INDEX.format(
        course_name=esc_html(cname),
        bank_html=bank_html,
        review_html=f'<div class="chapter-list">{review_nav}</div>',
        questions_json=json.dumps(questions_data, ensure_ascii=False),
    )
    _write_page(f"{cslug}/index.html", f"{cname} - Exam-Killer", content, base="..")

    # Copy question bank viewer JS
    _write_question_bank_js(cslug)


def _build_question_bank_html(cslug: str) -> str:
    return f"""\
<div class="filter-bar">
  <div class="filter-row">
    <div class="filter-group">
      <label>题型</label>
      <select id="filter-type" class="filter-select" onchange="applyFilter()">
        <option value="">全部题型</option>
      </select>
    </div>
    <div class="filter-group">
      <label>章节</label>
      <select id="filter-chapter" class="filter-select" onchange="applyFilter()">
        <option value="">全部章节</option>
      </select>
    </div>
  </div>
  <div class="filter-row">
    <div class="filter-group" style="flex:1;">
      <label>知识点</label>
      <div id="filter-tags" class="filter-tags"></div>
    </div>
  </div>
</div>
<script src="../assets/js/question-bank-{cslug}.js"></script>"""


def _write_question_bank_js(cslug: str):
    """Generate a lightweight question-bank viewer for this course."""
    js = f"""\
(function(){{
var allQuestions = [];
var allChapters = [];
var allTags = [];
var selectedTag = null;

function loadData() {{
  Promise.all([
    fetch('questions.json').then(function(r) {{ return r.json(); }}),
    fetch('chapters.json').then(function(r) {{ return r.json(); }}),
    fetch('tags.json').then(function(r) {{ return r.json(); }})
  ]).then(function(results) {{
    allQuestions = results[0];
    allChapters = results[1];
    allTags = results[2];
    buildFilters();
    render();
  }});
}}

function typeLabel(t) {{
  var map = {{ single_choice:'单选题', multiple_choice:'多选题', fill_blank:'填空题', true_false:'判断题', short_answer:'简答题', calculation:'计算题', proof:'证明题', essay:'论述题' }};
  return map[t] || t;
}}

function buildFilters() {{
  // Type dropdown
  var typeSel = document.getElementById('filter-type');
  var types = {{}};
  allQuestions.forEach(function(q) {{ if (q.qtype) types[q.qtype] = true; }});
  Object.keys(types).sort().forEach(function(t) {{
    var opt = document.createElement('option');
    opt.value = t; opt.textContent = typeLabel(t);
    typeSel.appendChild(opt);
  }});
  // Chapter dropdown
  var chSel = document.getElementById('filter-chapter');
  allChapters.forEach(function(ch) {{
    var opt = document.createElement('option');
    opt.value = ch; opt.textContent = ch;
    chSel.appendChild(opt);
  }});
  // Tags
  renderTags();
}}

function getFiltered() {{
  var qtype = document.getElementById('filter-type').value;
  var chapter = document.getElementById('filter-chapter').value;
  return allQuestions.filter(function(q) {{
    if (qtype && q.qtype !== qtype) return false;
    if (chapter && (q.chapter_tags || '').split(',').map(function(s){{return s.trim();}}).indexOf(chapter) === -1) return false;
    if (selectedTag && (q.knowledge_tags || '').split(',').map(function(s){{return s.trim();}}).indexOf(selectedTag) === -1) return false;
    return true;
  }});
}}

function renderTags() {{
  var filtered = getFiltered();
  var counts = {{}};
  filtered.forEach(function(q) {{
    (q.knowledge_tags || '').split(',').forEach(function(t) {{ t = t.trim(); if (t) counts[t] = (counts[t] || 0) + 1; }});
  }});
  if (selectedTag && !counts[selectedTag]) selectedTag = null;
  var el = document.getElementById('filter-tags');
  var html = '<button class="tag-chip' + (!selectedTag ? ' active' : '') + '" data-tag="\\">全部 <span class="tag-count">' + filtered.length + '</span></button>';
  Object.keys(counts).sort().forEach(function(t) {{
    html += '<button class="tag-chip' + (selectedTag === t ? ' active' : '') + '" data-tag="' + t.replace(/"/g,'&quot;') + '">' + t + ' <span class="tag-count">' + counts[t] + '</span></button>';
  }});
  el.innerHTML = html;
  el.querySelectorAll('.tag-chip').forEach(function(btn) {{
    btn.addEventListener('click', function() {{
      selectedTag = btn.dataset.tag || null;
      renderTags();
      render();
    }});
  }});
}}

function render() {{
  var filtered = getFiltered();
  var el = document.getElementById('question-list');
  if (filtered.length === 0) {{
    el.innerHTML = '<div class="empty-state"><h3>未找到题目</h3></div>';
    return;
  }}
  el.innerHTML = filtered.map(function(q) {{
    var contentHtml = (q.content || '').replace(/\\$\\$(.+?)\\$\\$/g, '<span class=\\"katex-tex\\" data-display=\\"true\\">$1</span>').replace(/\\$(.+?)\\$/g, '<span class=\\"katex-tex\\" data-display=\\"false\\">$1</span>');
    contentHtml = contentHtml.replace(/\\n\\n/g, '</p><p>').replace(/\\n/g, '<br>');
    contentHtml = '<p>' + contentHtml + '</p>';
    return '<div class=\\"question-card\\">' +
      '<div class=\\"flex justify-between items-center mb-2\\"><span class=\\"qtype-badge\\">' + typeLabel(q.qtype) + '</span><span class=\\"text-muted\\" style=\\"font-size:12px;font-weight:600;opacity:0.5;\\">' + q.qid + '</span></div>' +
      '<div class=\\"question-content\\">' + contentHtml + '</div>' +
      '<button class=\\"btn btn-sm btn-secondary toggle-answer\\" onclick=\\"this.nextElementSibling.classList.toggle(\\'open\\');this.textContent=this.nextElementSibling.classList.contains(\\'open\\')?'隐藏解析':'显示解析'\\">显示解析</button>' +
      '<div class=\\"answer-section\\"><h4>答案</h4><p>' + (q.answer || '(无答案)') + '</p>' +
      (q.explanation ? '<h4>解析</h4><p>' + q.explanation + '</p>' : '') + '</div>' +
      '</div>';
  }}).join('');
  // Re-render KaTeX
  renderKatex();
}}

function renderKatex() {{
  if (typeof katex === 'undefined') return;
  document.querySelectorAll('.katex-tex').forEach(function(el) {{
    try {{ katex.render(el.textContent, el, {{ displayMode: el.dataset.display === 'true', throwOnError: false }}); }} catch(e) {{}}
  }});
}}

window.applyFilter = function() {{
  renderTags();
  render();
}};

loadData();
}})();"""
    (SITE_DIR / "assets" / "js" / f"question-bank-{cslug}.js").write_text(
        js, encoding="utf-8"
    )


def _md_to_html(md: str, course_slug: str) -> str:
    """Convert review-guide markdown to HTML for static display."""
    # Image path rewriting: images/xxx → ../../images/xxx (from review-guide subdir)
    md = re.sub(r"!\[\]\(images/([^)]+)\)", r"![](../../images/\1)", md)


def _inline_html(text: str) -> str:
    """Convert inline formatting."""
    text = esc_html(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
    return text


def copy_images():
    """Copy all question images to _site/images/ (flat, keyed by filename)."""
    img_dir = SITE_DIR / "images"
    img_dir.mkdir(exist_ok=True)
    count = 0
    seen = set()
    for course_dir in Path(str(DATA_DIR)).iterdir():
        if not course_dir.is_dir():
            continue
        raw_base = course_dir / "raw"
        if not raw_base.exists():
            continue
        for raw_dir in sorted(raw_base.iterdir()):
            if not raw_dir.is_dir():
                continue
            images_path = raw_dir / "images"
            if images_path.exists():
                for img in images_path.iterdir():
                    if img.is_file() and img.name not in seen:
                        seen.add(img.name)
                        shutil.copy2(img, img_dir / img.name)
                        count += 1
    print(f"Copied {count} images")


def _write_page(path: str, title: str, content: str, base: str = "."):
    full_path = SITE_DIR / path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_text(
        HTML_SHELL.format(title=esc_html(title), content=content, base=base),
        encoding="utf-8",
    )
    print(f"  {full_path.relative_to(SITE_DIR)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export exam-killer to static site")
    parser.add_argument("--out-dir", default=str(SITE_DIR), help="Output directory")
    args = parser.parse_args()
    SITE_DIR = Path(args.out_dir)
    export_all()
