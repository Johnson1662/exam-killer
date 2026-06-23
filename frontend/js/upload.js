/* Upload & Parse tab — requires config saved in Settings tab. */

async function renderUpload(container, courseId, course) {
  const cfg = getLLMConfig();
  const llmOk = isLLMConfigured();
  const mineruOk = isMineruConfigured();
  container.innerHTML = [

    '<div class="config-bar">',
    '<div class="config-item">',
    '<span class="config-dot" style="background:' + (mineruOk ? 'var(--success)' : 'var(--danger)') + ';"></span>',
    '<div><div style="font-weight:700; font-size:0.85rem;">MinerU Token</div>',
    '<div class="text-subtle">' + (mineruOk ? '\u5DF2\u5C31\u7EEA' : '\u672A\u914D\u7F6E') + '</div></div></div>',
    '<div class="config-item">',
    '<span class="config-dot" style="background:' + (llmOk ? 'var(--success)' : 'var(--danger)') + ';"></span>',
    '<div><div style="font-weight:700; font-size:0.85rem;">LLM \u914D\u7F6E</div>',
    '<div class="text-subtle">' + (llmOk ? '\u5DF2\u5C31\u7EEA' : '\u672A\u914D\u7F6E') + '</div></div></div>',
    '</div>',
    '<div class="grid-layout">',
    /* Left column: file upload */
    '<div><h3 class="mb-2">1. \u4E0A\u4F20\u6587\u4EF6</h3>',
    '<div class="card">',
    '<p class="text-muted mb-2">\u4E0A\u4F20 PDF \u6216 \u56FE\u7247\u683C\u5F0F\u7684\u5F80\u5E74\u8BD5\u5377\u6216\u8BFE\u4EF6\u3002</p>',
    '<div class="upload-dropzone">',
    '<i data-lucide="upload-cloud" style="width:48px; height:48px; opacity:0.2; margin-bottom:16px;"></i>',
    '<input type="file" id="file-input" multiple accept=".pdf,.doc,.docx,.ppt,.pptx,.png,.jpg,.jpeg" style="display:none;">',
    '<div><button class="btn btn-secondary btn-sm" onclick="document.getElementById(\'file-input\').click()">\u9009\u62E9\u6587\u4EF6</button></div>',
    '<div id="selected-files-count" class="text-subtle mt-2">\u672A\u9009\u62E9\u6587\u4EF6</div>',
    '</div>',
    '<button class="btn btn-primary mt-2" style="width:100%" id="btn-upload">\u5F00\u59CB\u4E0A\u4F20</button>',
    '<div id="file-list" class="mt-4"></div>',
    '</div></div>',
    /* Right column: parse / extract */
    '<div><h3 class="mb-2">2. \u89E3\u6790\u4E0E\u62BD\u53D6</h3>',
    '<div class="card">',
    '<p class="text-muted mb-2">\u4F7F\u7528 MinerU \u89E3\u6790\u6587\u6863\u5185\u5BB9\uFF0C\u5E76\u7531 AI \u81EA\u52A8\u8BC6\u522B\u5E76\u63D0\u53D6\u9898\u76EE\u3002</p>',
    /* Chapter outline textarea */
    '<div class="form-group">',
    '<label>\u7AE0\u8282\u5217\u8868 (\u53EF\u9009)</label>',
    '<textarea id="upload-chapters" rows="4" placeholder="\u6BCF\u884C\u4E00\u4E2A\u7AE0\u8282\uFF0C\u4F8B\u5982\uFF1A\n\u7B2C\u4E00\u7AE0 \u6781\u9650\u4E0E\u8FDE\u7EED\n\u7B2C\u4E8C\u7AE0 \u5BFC\u6570\u4E0E\u5FAE\u5206"></textarea>',
    '<div style="display:flex; justify-content:space-between; margin-top:4px;">',
    '<button class="btn btn-xs btn-secondary" id="btn-ai-chapters" style="font-size:0.75rem;"><i data-lucide="sparkles" style="width:12px;height:12px;"></i> AI \u751F\u6210</button>',
    '<button class="btn btn-xs btn-secondary" id="btn-save-chapters" style="font-size:0.75rem;"><i data-lucide="save" style="width:12px;height:12px;"></i> \u4FDD\u5B58\u7AE0\u8282</button>',
    '</div></div>',
    '<div class="flex flex-direction-column gap-2">',
    '<button class="btn btn-primary" id="btn-parse" style="justify-content:flex-start">',
    '<i data-lucide="cpu" style="width:18px; height:18px;"></i>',
    '\u7B2C\u4E00\u6B65\uFF1A\u6587\u6863\u5185\u5BB9\u89E3\u6790</button>',
    '<button class="btn btn-secondary" id="btn-extract" style="justify-content:flex-start">',
    '<i data-lucide="wand-2" style="width:18px; height:18px;"></i>',
    '\u7B2C\u4E8C\u6B65\uFF1AAI \u9898\u76EE\u62BD\u53D6</button>',
    '</div>',
    '<div id="parse-progress" style="display:none; margin-top:12px; background:var(--surface); border:1px solid var(--hairline); border-radius:var(--radius-md); max-height:300px; overflow-y:auto;">',
    '  <div style="padding:10px 14px; font-size:0.85rem;">',
    '    <div style="display:flex; align-items:center; gap:8px; margin-bottom:8px; padding-bottom:8px; border-bottom:1px solid var(--border);">',
    '      <i data-lucide="loader" style="width:14px;height:14px;color:var(--accent);"></i>',
    '      <span id="progress-title" style="font-weight:600; flex:1;">等待处理...</span>',
    '      <span id="progress-count" class="text-subtle" style="font-size:0.8rem;"></span>',
    '    </div>',
    '    <div id="progress-log" style="display:flex; flex-direction:column; gap:4px;"></div>',
    '  </div>',
    '</div>',
    '</div></div></div>',
  ].join('');

  const chaptersTextarea = document.getElementById('upload-chapters');
  if (course.chapters) {
    chaptersTextarea.value = course.chapters;
  }
  // Pre-fill chapters from course data

  // Save chapters
  document.getElementById('btn-save-chapters').addEventListener('click', async () => {
    const chapters = chaptersTextarea.value.trim();
    try {
      await API.put(`/api/courses/${courseId}/chapters`, { chapters });
      window.toast('\u7AE0\u8282\u5DF2\u4FDD\u5B58', 'success');
    } catch (e) {
      window.toast('\u4FDD\u5B58\u5931\u8D25', 'error');
    }
  });


  // AI generate chapters
  document.getElementById('btn-ai-chapters').addEventListener('click', async () => {
    const cfg = getLLMConfig();
    if (!cfg.llm_key || !cfg.llm_endpoint || !cfg.llm_model) {
      window.toast('\u8BF7\u5148\u5728\u201C\u8BBE\u7F6E\u201D\u9875\u9762\u586B\u5199 LLM \u914D\u7F6E', 'error');
      return;
    }
    const btn = document.getElementById('btn-ai-chapters');
    btn.disabled = true;
    btn.innerHTML = '<i data-lucide="loader" style="width:12px;height:12px;"></i> \u751F\u6210\u4E2D...';
    lucide.createIcons();
    try {
      const result = await API.post(`/api/courses/${courseId}/auto-chapters`, {
        llm_key: cfg.llm_key,
        llm_endpoint: cfg.llm_endpoint,
        llm_model: cfg.llm_model,
      });
      if (result.chapters) {
        chaptersTextarea.value = result.chapters;
        // Auto-save
        await API.put(`/api/courses/${courseId}/chapters`, { chapters: result.chapters });
        window.toast('\u7AE0\u8282\u5DF2\u751F\u6210\u5E76\u4FDD\u5B58', 'success');
      } else {
        window.toast('\u65E0\u6CD5\u751F\u6210\u7AE0\u8282\uFF0C\u8BF7\u786E\u4FDD\u5DF2\u89E3\u6790\u6587\u4EF6', 'error');
      }
    } catch (e) {
      window.toast('\u751F\u6210\u5931\u8D25: ' + e.message, 'error');
    }
    btn.disabled = false;
    btn.innerHTML = '<i data-lucide="sparkles" style="width:12px;height:12px;"></i> AI \u751F\u6210';
    lucide.createIcons();
  });
  // File input
  document.getElementById('file-input').addEventListener('change', (e) => {
    const count = e.target.files.length;
    document.getElementById('selected-files-count').textContent = count ? '\u5DF2\u9009\u62E9 ' + count + ' \u4E2A\u6587\u4EF6' : '\u672A\u9009\u62E9\u6587\u4EF6';
  });

  // Upload
  document.getElementById('btn-upload').addEventListener('click', async () => {
    const input = document.getElementById('file-input');
    if (!input.files.length) { window.toast('\u8BF7\u9009\u62E9\u6587\u4EF6', 'error'); return; }
    const formData = new FormData();
    for (const f of input.files) formData.append('files', f);
    try {
      const result = await API.upload(`/api/courses/${courseId}/files`, formData);
      window.toast('\u4E0A\u4F20\u6210\u529F\uFF1A' + result.length + ' \u4E2A\u6587\u4EF6');
      renderFileList(courseId);
    } catch (e) {
      window.toast('\u4E0A\u4F20\u5931\u8D25\uFF1A' + e.message, 'error');
    }
  });

  // Parse button
  document.getElementById('btn-parse').addEventListener('click', async () => {
    const cfg = getLLMConfig();
    if (!cfg.mineru_token) { window.toast('\u8BF7\u5148\u5728\u201C\u8BBE\u7F6E\u201D\u9875\u9762\u586B\u5199 MinerU Token', 'error'); return; }
    const files = await API.get(`/api/courses/${courseId}/files`);
    const pending = files.filter(f => f.status === 'pending' || f.status === 'failed').map(f => f.id);
    if (!pending.length) { window.toast('\u6CA1\u6709\u5F85\u89E3\u6790\u7684\u6587\u4EF6', 'error'); return; }
    await API.post(`/api/courses/${courseId}/parse`, {
      mineru_token: cfg.mineru_token,
      file_ids: pending,
    });
    document.getElementById('parse-progress').style.display = 'block';
    startSSE(courseId);
  });

  // Extract button — includes chapters in request
  document.getElementById('btn-extract').addEventListener('click', async () => {
    const cfg = getLLMConfig();
    if (!cfg.llm_key || !cfg.llm_endpoint || !cfg.llm_model) {
      window.toast('\u8BF7\u5148\u5728\u201C\u8BBE\u7F6E\u201D\u9875\u9762\u586B\u5199 LLM \u914D\u7F6E', 'error');
      return;
    }
    if (!cfg.mineru_token) {
      window.toast('\u8BF7\u5148\u5728\u201C\u8BBE\u7F6E\u201D\u9875\u9762\u586B\u5199 MinerU Token', 'error');
      return;
    }
    const files = await API.get(`/api/courses/${courseId}/files`);
    const parsed = files.filter(f => f.status === 'parsed' || f.status === 'annotated').map(f => f.id);
    await API.post(`/api/courses/${courseId}/extract`, {
      llm_key: cfg.llm_key,
      llm_endpoint: cfg.llm_endpoint,
      llm_model: cfg.llm_model,
      file_ids: parsed,
      chapters: chaptersTextarea.value.trim(),
    });
    document.getElementById('parse-progress').style.display = 'block';
    startSSE(courseId);
  });

  renderFileList(courseId);
  lucide.createIcons();
}

async function renderFileList(courseId) {
  var el = document.getElementById('file-list');
  try {
    var files = await API.get('/api/courses/' + courseId + '/files');
    if (!files.length) {
      el.innerHTML = '<div class="text-subtle text-center">\u6682\u65E0\u4E0A\u4F20\u6587\u4EF6</div>';
      return;
    }
    el.innerHTML = '<div style="font-weight:700; font-size:0.85rem; margin-bottom:8px; color:var(--fg-muted);">\u6587\u4EF6\u5217\u8868</div>'
      + files.map(function (f) {
        return '<div class="flex justify-between items-center" style="padding:8px 12px; background:var(--bg); border-radius:var(--radius-sm); margin-bottom:4px; border:1px solid var(--border);">'
          + '<span style="font-size:0.85rem; font-weight:600; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; max-width:200px;">' + f.filename + '</span>'
          + '<span class="status-badge ' + (f.status === 'parsed' ? 'success' : '') + '" style="font-size:10px;">' + f.status + '</span>'
          + '</div>';
      }).join('');
  } catch (e) {
    el.innerHTML = '<span class="text-muted">\u52A0\u8F7D\u5931\u8D25</span>';
  }
}
function startSSE(courseId) {
  var el = document.getElementById('parse-progress');
  el.style.display = 'block';
  var log = document.getElementById('progress-log');
  log.innerHTML = ''; // clear old entries
  var countEl = document.getElementById('progress-count');
  var doneCount = 0;

  var es = new EventSource('/api/courses/' + courseId + '/parse/events');

  es.addEventListener('message', function (e) {
    var data = e.data;

    // Check for done signal first
    if (data === 'done' || data === '[DONE]') {
      log.innerHTML += '<div style="display:flex;align-items:center;gap:6px;padding:6px 0;border-top:1px solid var(--border);margin-top:4px;padding-top:8px;color:var(--success);font-weight:600;font-size:0.85rem;">'
        + '<i data-lucide="check-circle" style="width:14px;height:14px;color:var(--success);"></i> '
        + '\u5904\u7406\u5B8C\u6210\uFF0C\u5171 ' + doneCount + ' \u9879</div>';
      countEl.textContent = '\u5DF2\u5B8C\u6210 ' + doneCount + ' \u9879';
      es.close();
      renderFileList(courseId);
      lucide.createIcons();
      return;
    }

    // Determine style from message content
    var icon = 'circle';
    var color = 'var(--text-muted)';
    var bg = '';

    if (data.indexOf('\u5B8C\u6210') !== -1 && data.indexOf('\u5931\u8D25') === -1) {
      // "完成:" or "解析完成:" — success
      icon = 'check-circle';
      color = 'var(--success)';
      doneCount++;
    } else if (data.indexOf('\u5931\u8D25') !== -1 || data.indexOf('\u8DF3\u8FC7') !== -1 || data.indexOf('\u8D85\u65F6') !== -1) {
      icon = 'alert-circle';
      color = 'var(--danger)';
    } else if (data.indexOf('\u89E3\u6790\u4E2D') !== -1 || data.indexOf('\u6B63\u5728') !== -1 || data.indexOf('\u5E76\u53D1') !== -1) {
      icon = 'loader';
      color = 'var(--accent)';
      bg = 'background:rgba(99,102,241,0.04)';
    } else if (data.indexOf('\u89E3\u6790\u5B8C\u6210') !== -1) {
      icon = 'check-circle';
      color = 'var(--success)';
      doneCount++;
    } else if (data.indexOf('\u9898\u5E93') !== -1) {
      icon = 'database';
      color = 'var(--accent)';
    }

    log.innerHTML += '<div style="display:flex;align-items:center;gap:6px;padding:4px 6px;border-radius:4px;' + bg + ';font-size:0.82rem;">'
      + '<i data-lucide="' + icon + '" style="width:12px;height:12px;flex-shrink:0;color:' + color + ';"></i>'
      + '<span style="color:' + color + ';">' + data + '</span>'
      + '</div>';

    countEl.textContent = doneCount ? '\u5DF2\u5B8C\u6210 ' + doneCount + ' \u9879' : '';
    el.scrollTop = el.scrollHeight;
    lucide.createIcons();
  });

  es.addEventListener('error', function () {
    log.innerHTML += '<div style="display:flex;align-items:center;gap:6px;padding:4px 0;color:var(--text-muted);font-style:italic;font-size:0.82rem;">SSE \u8FDE\u63A5\u65AD\u5F00</div>';
    el.scrollTop = el.scrollHeight;
    es.close();
  });
}
