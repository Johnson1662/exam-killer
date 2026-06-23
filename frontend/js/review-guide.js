/* Review guide tab. */

let _rgCourseId = null;

async function renderReviewGuide(container, courseId, course) {
  _rgCourseId = courseId;
  container.innerHTML = [
    '<div class="flex justify-between items-center mb-2">',
    '  <h3 style="margin:0">复习手册</h3>',
    '  <div id="rg-status"></div>',
    '</div>',
    '',
    '<!-- 可折叠配置区 -->',
    '<div class="rg-config-header">',
    '  <div style="font-size:0.8125rem; font-weight:500; color:var(--fg-subtle);">',
    '    <span id="rg-config-summary">AI 配置与生成</span>',
    '  </div>',
    '  <button class="rg-config-toggle" id="btn-toggle-config">',
    '    <i data-lucide="chevron-down" style="width:16px;height:16px;"></i>',
    '    配置',
    '  </button>',
    '</div>',
    '<div class="rg-config-body" id="rg-config-body">',
    '  <div class="rg-config-card">',
    '    <div style="flex:1">',
    '      <div style="font-size:0.8125rem; font-weight:500; color:var(--fg); margin-bottom:2px;">自定义大纲（可选）</div>',
    '      <p class="text-subtle" style="margin:0; font-size:0.75rem;">AI 将根据当前题库与自定义大纲，提取核心考点生成复习手册。</p>',
    '    </div>',
    '    <button class="btn btn-outline-sparkle" id="btn-generate-review">',
    '      <i data-lucide="sparkles" style="width:14px;height:14px;"></i>',
    '      生成手册',
    '    </button>',
    '  </div>',
    '  <div class="mt-3">',
    '    <textarea id="rg-outline" rows="3" placeholder="例如：&#10;第一章：极限与连续&#10;第二章：导数与微分&#10;..." style="width:100%;"></textarea>',
    '  </div>',
    '</div>',
    '<div id="rg-progress" class="progress-log mt-4" style="display:none"></div>',
    '<div class="rg-layout mt-4">',
    '  <aside class="rg-sidebar">',
    '    <div id="rg-chapters" class="chapter-list-nav"></div>',
    '  </aside>',
    '  <main class="rg-content-area">',
    '    <div id="rg-chapter-content"></div>',
    '  </main>',
    '</div>',
  ].join('\n');

  loadChapters();

  // Pre-fill chapters from course data (synced with upload tab)
  const rgOutline = document.getElementById('rg-outline');
  if (course && course.chapters) {
    rgOutline.value = course.chapters;
  }

  document.getElementById('btn-generate-review').addEventListener('click', async () => {
    const cfg = getLLMConfig();
    if (!cfg.llm_key || !cfg.llm_endpoint || !cfg.llm_model) {
      window.toast('请先在"设置"页面填写 LLM 配置', 'error');
      return;
    }
    const outline = document.getElementById('rg-outline').value.trim();

    const progressEl = document.getElementById('rg-progress');
    progressEl.style.display = 'block';
    progressEl.innerHTML = '<div>开始生成...</div>';

    try {
      await API.post(`/api/courses/${courseId}/generate-review`, {
        llm_key: cfg.llm_key,
        llm_endpoint: cfg.llm_endpoint,
        llm_model: cfg.llm_model,
        outline: outline || null,
      });
    } catch (e) {
      progressEl.innerHTML += `<div class="text-danger">触发失败: ${e.message}</div>`;
      return;
    }
    // SSE for progress
    const es = new EventSource(`/api/courses/${courseId}/parse/events`);
    es.addEventListener('message', async (e) => {
      if (e.data === 'done') {
        progressEl.innerHTML += '<div style="color:var(--success); font-weight:700; margin-top:8px;">[OK] 复习手册生成完毕</div>';
        es.close();
        // Sync outline back to course chapters
        const outline = document.getElementById('rg-outline').value.trim();
        if (outline) {
          try { await API.put(`/api/courses/${courseId}/chapters`, { chapters: outline }); } catch (_) {}
        }
        setTimeout(() => {
          loadChapters().then(() => {
            const first = document.querySelector('.chapter-item');
            if (first) first.click();
          });
        }, 500);
        return;
      }
      progressEl.innerHTML += `<div>${e.data}</div>`;
      progressEl.scrollTop = progressEl.scrollHeight;
    });
    let _toolCallId = 0;
    let _thinkingRow = null;
    es.addEventListener('tool', (e) => {
      try {
        const d = JSON.parse(e.data);
        const rowId = `tool-${++_toolCallId}`;

        if (d.tool === 'llm') {
          if (d.status === 'thinking' && !_thinkingRow) {
            _thinkingRow = document.createElement('div');
            _thinkingRow.className = 'tool-call thinking';
            _thinkingRow.id = 'thinking-indicator';
            _thinkingRow.innerHTML = '<span class="tool-icon">\u{1F914}</span> <span class="tool-msg">AI 思考中...</span>';
            progressEl.appendChild(_thinkingRow);
            progressEl.scrollTop = progressEl.scrollHeight;
          } else if (d.status === 'done' && _thinkingRow) {
            _thinkingRow.remove();
            _thinkingRow = null;
          }
          return;
        }

        if (_thinkingRow) {
          _thinkingRow.remove();
          _thinkingRow = null;
        }

        const icons = { read: '\u{1F4D6}', write: '\u{1F4DD}', edit: '\u{270F}\u{FE0F}' };
        const icon = icons[d.tool] || '\u{2699}\u{FE0F}';
        const pathStr = d.path || '';

        let statusHtml = '';
        if (d.status === 'running') {
          statusHtml = '<span class="tool-spinner"></span>';
        } else if (d.status === 'done') {
          const detail = d.detail && isNaN(d.detail) ? '' : (d.detail ? ` (${d.detail})` : '');
          statusHtml = '<span class="tool-check">\u2713</span>' + detail;
        } else if (d.status === 'error') {
          statusHtml = '<span class="tool-error">\u2717</span> ' + (d.detail || '');
        }

        const div = document.createElement('div');
        div.className = 'tool-call' + (d.status === 'running' ? ' running' : '');
        div.id = rowId;
        div.innerHTML = `<span class="tool-icon">${icon}</span> <span class="tool-msg">${d.tool === 'write' ? '写入' : d.tool === 'read' ? '读取' : '编辑'} ${pathStr}</span> <span class="tool-status">${statusHtml}</span>`;
        progressEl.appendChild(div);
        progressEl.scrollTop = progressEl.scrollHeight;
      } catch (_) {}
    });
  });

  // 折叠/展开配置区
  const toggleBtn = document.getElementById('btn-toggle-config');
  const configBody = document.getElementById('rg-config-body');
  toggleBtn.addEventListener('click', () => {
    configBody.classList.toggle('collapsed');
    toggleBtn.classList.toggle('collapsed');
  });
}
async function loadChapters() {
  const el = document.getElementById('rg-chapters');
  if (!el) return;
  try {
    const chapters = await API.get(`/api/courses/${_rgCourseId}/review/chapters`);
    if (!chapters || !chapters.length) {
      el.innerHTML = `
        <div class="empty-state">
          <i data-lucide="book-open" style="width:48px;height:48px;"></i>
          <p class="text-muted">暂无章节，请先生成复习手册。</p>
        </div>`;
      lucide.createIcons();
      return;
    }

    /* 有章节 → 折叠配置区 */
    const cb = document.getElementById('rg-config-body');
    const tb = document.getElementById('btn-toggle-config');
    if (cb && tb) { cb.classList.add('collapsed'); tb.classList.add('collapsed'); }

    el.innerHTML = [
      '<div class="chapter-list">',
      ...chapters.map((ch, i) => [
        `<div class="chapter-item" data-filename="${ch.filename}">`,
        `  <div class="chapter-num">${String(i + 1).padStart(2, '00')}</div>`,
        `  <div class="chapter-title">${ch.title}</div>`,
        `</div>`,
      ]).flat(),
      '</div>',
    ].join('\n');
    lucide.createIcons();

    // Event listeners for chapters
    el.querySelectorAll('.chapter-item').forEach(item => {
      item.addEventListener('click', async () => {
        el.querySelectorAll('.chapter-item').forEach(i => i.classList.remove('active'));
        item.classList.add('active');

        const filename = item.dataset.filename;
        const contentEl = document.getElementById('rg-chapter-content');
        contentEl.innerHTML = '<div class="skeleton" style="height:400px; width:100%;"></div>';
        
        try {
          const res = await API.get(`/api/courses/${_rgCourseId}/review/chapters/${filename}`);
          const questions = await API.get(`/api/courses/${_rgCourseId}/questions`);
          const qMap = {};
          questions.forEach(q => {
            if (q.qid) qMap[q.qid] = q;
          });
          
          contentEl.innerHTML = `
            <div class="card fade-in" style="padding:48px;">
              <div class="markdown-content">
                ${renderMarkdown(res.content, qMap)}
              </div>
            </div>
          `;
          lucide.createIcons();
          contentEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
        } catch (e) {
          contentEl.innerHTML = `<div class="card"><p class="text-danger">加载失败: ${e.message}</p></div>`;
        }
      });
    });

  } catch (e) {
    el.innerHTML = `<p class="text-muted">加载章节列表失败: ${e.message}</p>`;
  }
}
