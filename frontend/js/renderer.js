/* Marked custom renderer — renders LaTeX and handles [Qxxxx] references. */

let _questionMap = {};

function setQuestionMap(map) {
  _questionMap = map;
}

/*
   Strategy: extract $...$ / $$...$$ before marked sees them,
   replace with safe ¶MATH¶ placeholders, restore after marked.parse().
*/

function extractAndPlacehold(text) {
  const fragments = [];
  let idx = 0;
  text = text.replace(/\$\$([\s\S]+?)\$\$/g, (_, expr) => {
    fragments.push(expr.trim());
    return `\xB6MATH\xB6D${idx++}\xB6`;
  });
  text = text.replace(/\$([^\n$]+?)\$/g, (_, expr) => {
    fragments.push(expr.trim());
    return `\xB6MATH\xB6I${idx++}\xB6`;
  });
  return { text, fragments };
}

function restorePlaceholders(html, fragments) {
  if (!window.katex) return html;
  let idx = 0;
  html = html.replace(/\xB6MATH\xB6D\d+\xB6/g, () => {
    try { return katex.renderToString(fragments[idx++], { displayMode: true, throwOnError: false }); }
    catch (e) { return `<span style="color:#dc2626">$$${fragments[idx-1]}$$</span>`; }
  });
  html = html.replace(/\xB6MATH\xB6I\d+\xB6/g, () => {
    try { return katex.renderToString(fragments[idx++], { displayMode: false, throwOnError: false }); }
    catch (e) { return `<span style="color:#dc2626">$${fragments[idx-1]}$</span>`; }
  });
  return html;
}

function convertObsidianCallouts(text) {
  /* Convert Obsidian foldable callouts to <details> elements.
     > [!TYPE]- Summary   → <details> (collapsed)
     > [!TYPE]+ Summary   → <details open> (expanded)
  */
  const lines = text.split('\n');
  const out = [];
  let i = 0;
  while (i < lines.length) {
    const m = lines[i].match(/^> \[!(\w+)]([-+])\s*(.*)$/);
    if (m) {
      const [, , foldable, summary] = m;
      const collapsed = foldable === '-';
      const body = [];
      i++;
      while (i < lines.length) {
        const cur = lines[i];
        if (/^>\s?/.test(cur)) {
          body.push(cur.replace(/^>\s?/, ''));
          i++;
        } else if (cur === '' && i + 1 < lines.length && /^>\s?/.test(lines[i + 1])) {
          body.push('');
          i++;
        } else {
          break;
        }
      }
      out.push(`<details${collapsed ? '' : ' open'}>`);
      out.push(`<summary>${summary || 'Details'}</summary>`);
      out.push(body.join('\n'));
      out.push('</details>');
    } else {
      out.push(lines[i]);
      i++;
    }
  }
  return out.join('\n');
}

function createRenderer() {
  const renderer = new marked.Renderer();
  const origParagraph = renderer.paragraph.bind(renderer);
  renderer.paragraph = function (text) {
    text = text.replace(/\[(Q\d+)\]/g, (match, qid) => {
      const q = _questionMap[qid];
      if (!q) return match;
      const content = renderMarkdown(q.content || '');
      return `<div class="question-ref" data-qid="${qid}">
        <strong>${qid}</strong>
        <span class="qtype-badge">${q.qtype || ''}</span>
        <span class="difficulty">${Array.from({length: Math.max(0, (q.difficulty || 1) - 1)}, () => '<span class="dot filled"></span>').join('')}<span class="dot"></span></span>
        <div class="qref-content">${content}</div>
        <details><summary>答案与解析</summary>
          <div class="answer-section">${renderMarkdown(q.answer || '(无答案)')}</div>
          ${q.explanation ? `<div class="explanation-section"><strong>解析</strong>${renderMarkdown(q.explanation)}</div>` : ''}
        </details>
      </div>`;
    });
    return origParagraph(text);
  };
  return renderer;
}
function renderMarkdown(text, questionMap) {
  if (questionMap) setQuestionMap(questionMap);
  const converted = convertObsidianCallouts(text);
  const { text: cleanText, fragments } = extractAndPlacehold(converted);
  const renderer = createRenderer();
  marked.setOptions({ renderer, breaks: true, gfm: true });
  let html = marked.parse(cleanText);
  html = restorePlaceholders(html, fragments);
  return html;
}

