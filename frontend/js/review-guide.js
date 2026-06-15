/* Review guide tab. */

let _rgCourseId = null;

async function renderReviewGuide(container, courseId, course) {
  _rgCourseId = courseId;
  container.innerHTML = `
    <div class="flex justify-between items-center mb-2">
      <h3 style="margin:0">复习手册</h3>
      <div id="rg-status"></div>
    </div>
    <div class="card">
      <p class="text-muted mb-4">生成复习手册需要先完成题目抽取。AI 将根据课程内容与题库，为您自动整理核心考点与解析。</p>
      <div class="form-group">
        <label>自定义大纲 (可选)</label>
        <textarea id="rg-outline" rows="4" placeholder="例如：\n第一章：极限与连续\n第二章：导数与微分\n..."></textarea>
      </div>
      <div class="flex justify-end mt-4">
        <button class="btn btn-primary" id="btn-generate-review">
          <i data-lucide="sparkles" style="width:18px; height:18px;"></i>
          生成/更新复习手册
        </button>

      </div>
      <div id="rg-progress" class="progress-log mt-4"></div>
    </div>
    <div class="mt-4" id="rg-chapters"></div>
  `;

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

    el.innerHTML = `
      <h3 class="mb-2">已有章节</h3>
      <div class="chapter-list">
        ${chapters.map((ch, i) => `
          <div class="chapter-item" data-filename="${ch.filename}">
            <div class="chapter-num">${String(i + 1).padStart(2, '0')}</div>
            <div class="chapter-title">${ch.title}</div>
            <div style="margin-left:auto; opacity:0.3;">
              <i data-lucide="chevron-right"></i>
            </div>
          </div>
        `).join('')}
      </div>
      <div id="rg-chapter-content" class="mt-4"></div>
    `;
    lucide.createIcons();

    // Event listeners for chapters
    el.querySelectorAll('.chapter-item').forEach(item => {
      item.addEventListener('click', async () => {
        // Highlight active chapter
        el.querySelectorAll('.chapter-item').forEach(i => {
           i.style.borderColor = 'var(--border)';
           i.style.background = 'var(--surface)';
        });
        item.style.borderColor = 'var(--accent)';
        item.style.background = 'var(--accent-soft)';

        const filename = item.dataset.filename;
        const contentEl = document.getElementById('rg-chapter-content');
        contentEl.innerHTML = '<div class="skeleton" style="height:400px; width:100%;"></div>';
        
        try {
          const res = await API.get(`/api/courses/${_rgCourseId}/review/chapters/${filename}`);
          // Fetch questions to populate the map for [Qxxxx] references
          const questions = await API.get(`/api/courses/${_rgCourseId}/questions`);
          const qMap = {};
          questions.forEach(q => {
            if (q.qid) qMap[q.qid] = q;
          });
          
          contentEl.innerHTML = `
            <div class="card fade-in" style="padding:48px; border-top: 8px solid var(--accent);">
              <div class="markdown-content">
                ${renderMarkdown(res.content, qMap)}
              </div>
            </div>
          `;
          lucide.createIcons();
          // Scroll to content
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
