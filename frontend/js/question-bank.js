/* Question bank tab — multi-dimension filter: source | type | chapter | tags. */
async function renderQuestionBank(container, courseId, course) {
  container.innerHTML = `
    <div class="filter-bar">
      <div class="filter-row">
        <div class="filter-group">
          <label for="filter-source">来源试卷</label>
          <select id="filter-source" class="filter-select">
            <option value="">全部试卷</option>
          </select>
        </div>
        <div class="filter-group">
          <label for="filter-type">题型</label>
          <select id="filter-type" class="filter-select">
            <option value="">全部题型</option>
          </select>
        </div>
        <div class="filter-group">
          <label for="filter-chapter">章节</label>
          <select id="filter-chapter" class="filter-select">
            <option value="">全部章节</option>
          </select>
        </div>
      </div>
      <div class="filter-row">
        <div class="filter-group" style="flex:1;">
          <label>知识点</label>
          <div id="tag-list" class="filter-tags"></div>
        </div>
      </div>
    </div>
    <div id="question-list" style="display:flex; flex-direction:column; gap:24px;"></div>
  `;

  const listEl = container.querySelector('#question-list');
  const tagsEl = container.querySelector('#tag-list');
  const sourceSelect = container.querySelector('#filter-source');
  const typeSelect = container.querySelector('#filter-type');
  const chapterSelect = container.querySelector('#filter-chapter');

  let allQuestions = [];
  let selectedTag = null;
  let allChapters = [];
  let tagsCollapsed = true;

  async function loadData() {
    try {
      // Fetch questions, tags, files, and chapters in parallel
      const [questions, tagNames, files, chapters] = await Promise.all([
        API.get(`/api/courses/${courseId}/questions`),
        API.get(`/api/courses/${courseId}/tags`),
        API.get(`/api/courses/${courseId}/files`),
        API.get(`/api/courses/${courseId}/chapters`).catch(() => []),
      ]);
      allQuestions = questions;
      allChapters = chapters;
      // Populate chapter dropdown (clear first to avoid duplicates on re-load)
      chapterSelect.innerHTML = '<option value="">\u5168\u90E8\u7AE0\u8282</option>';
      chapters.forEach(ch => {
        const opt = document.createElement('option');
        opt.value = ch;
        opt.textContent = ch;
        chapterSelect.appendChild(opt);
      });

      // Build source file map
      const fileMap = {};
      files.forEach(f => { fileMap[f.id] = f.original_name || f.filename; });

      // Populate source dropdown (clear first)
      sourceSelect.innerHTML = '<option value="">\u5168\u90E8\u8BD5\u5377</option>';
      const sourceIds = new Set();
      questions.forEach(q => { if (q.source_file_id) sourceIds.add(q.source_file_id); });
      sourceIds.forEach(id => {
        const opt = document.createElement('option');
        opt.value = id;
        opt.textContent = fileMap[id] || '\u6587\u4EF6 #' + id;
        sourceSelect.appendChild(opt);
      });

      // Populate type dropdown (clear first)
      typeSelect.innerHTML = '<option value="">\u5168\u90E8\u9898\u578B</option>';
      const types = new Set();
      questions.forEach(q => { if (q.qtype) types.add(q.qtype); });
      types.forEach(t => {
        const opt = document.createElement('option');
        opt.value = t;
        opt.textContent = typeLabel(t);
      });

      function rerender() {
        renderTags();
        renderQuestions();
        lucide.createIcons();
      }
      if (!listEl._filterDel) {
        listEl._filterDel = true;
        sourceSelect.addEventListener('change', rerender);
        typeSelect.addEventListener('change', rerender);
        chapterSelect.addEventListener('change', rerender);
      }

      renderTags();
      renderQuestions();
      lucide.createIcons();
    } catch (e) {
      window.toast('加载题库失败: ' + String(e && e.message ? e.message : e), 'error');
      console.error('QuestionBank load error:', e);
    }
  }

  function typeLabel(t) {
    const map = {
      single_choice: '\u5355\u9009\u9898',
      multiple_choice: '\u591A\u9009\u9898',
      fill_blank: '\u586B\u7A7A\u9898',
      true_false: '\u5224\u65AD\u9898',
      short_answer: '\u7B80\u7B54\u9898',
      calculation: '\u8BA1\u7B97\u9898',
      proof: '\u8BC1\u660E\u9898',
      essay: '\u8BBA\u8FF0\u9898',
    };
    return map[t] || t;
  }


  function getFilteredQuestions() {
    var sourceId = sourceSelect.value;
    var qtype = typeSelect.value;
    var chapterTitle = chapterSelect.value;
    return allQuestions.filter(function (q) {
      if (sourceId && String(q.source_file_id) !== sourceId) return false;
      if (qtype && q.qtype !== qtype) return false;
      if (chapterTitle) {
        var qcs = (q.chapter_tags || '').split(',').map(function (s) { return s.trim(); }).filter(Boolean);
        if (qcs.indexOf(chapterTitle) === -1) return false;
      }
      return true;
    });
  }

  function renderTags() {
    var filtered = getFilteredQuestions();

    // Compute tag counts from the filtered question set
    var counts = {};
    filtered.forEach(function (q) {
      (q.knowledge_tags || '').split(',').map(function (s) { return s.trim(); }).filter(Boolean).forEach(function (t) {
        counts[t] = (counts[t] || 0) + 1;
      });
    });

    // Clear selected tag if no longer available in filtered set
    if (selectedTag && !counts[selectedTag]) {
      selectedTag = null;
    }

    var tagArr = Object.keys(counts).map(function (name) { return { name: name, count: counts[name] }; });
    tagArr.sort(function (a, b) { return b.count - a.count || a.name.localeCompare(b.name); });
    var allTags = [
      '<button class="tag-chip ' + (!selectedTag ? 'active' : '') + '" data-tag="">',
      '\u5168\u90E8 <span class="tag-count">' + filtered.length + '</span>',
      '</button>',
    ].concat(tagArr.map(function (t) {
      return '<button class="tag-chip ' + (selectedTag === t.name ? 'active' : '') + '" data-tag="' + t.name + '">'
        + t.name + ' <span class="tag-count">' + t.count + '</span></button>';
    }));

    tagsEl.innerHTML = [
      '<div class="tag-list-wrapper' + (tagsCollapsed ? ' collapsed' : '') + '">',
      allTags.join(''),
      '</div>',
      '<button class="tag-toggle btn btn-sm btn-ghost" style="margin-top:6px;">',
      tagsCollapsed ? '\u5C55\u5F00 <i data-lucide="chevron-down" style="width:14px;height:14px;"></i>' : '\u6298\u53E0 <i data-lucide="chevron-up" style="width:14px;height:14px;"></i>',
      '</button>',
    ].join('');

    tagsEl.querySelectorAll('.tag-chip').forEach(function (el) {
      el.addEventListener('click', function () {
        selectedTag = el.dataset.tag || null;
        renderTags();
        renderQuestions();
        lucide.createIcons();
      });
    });

    var toggleBtn = tagsEl.querySelector('.tag-toggle');
    if (toggleBtn) {
      toggleBtn.addEventListener('click', function (e) {
        e.stopPropagation();
        tagsCollapsed = !tagsCollapsed;
        renderTags();
        lucide.createIcons();
      });
    }
  }

  function renderQuestions() {
    var filtered = getFilteredQuestions();
    if (selectedTag) {
      filtered = filtered.filter(function (q) {
        return (q.knowledge_tags || '').split(',').map(function (s) { return s.trim(); }).indexOf(selectedTag) !== -1;
      });
    }

    if (filtered.length === 0) {
      listEl.innerHTML = [
        '<div class="empty-state">',
        '<i data-lucide="search" style="width:48px;height:48px;opacity:0.2;margin-bottom:16px;"></i>',
        '<h3>\u672A\u627E\u5230\u9898\u76EE</h3>',
        '<p class="text-muted">\u6CA1\u6709\u5339\u914D\u5F53\u524D\u7B5B\u9009\u6761\u4EF6\u7684\u9898\u76EE\u3002</p>',
        '</div>',
      ].join('');
      lucide.createIcons();
      return;
    }

    listEl.innerHTML = filtered.map(q => {
      const tags = (q.knowledge_tags || '').split(',').map(s => s.trim()).filter(Boolean);
      const chapters = (q.chapter_tags || '').split(',').map(s => s.trim()).filter(Boolean);
      return [
        '<div class="question-card">',
        '<div class="flex justify-between items-center mb-2">',
        '<div class="flex items-center gap-2">',
        '<span class="qtype-badge">' + (typeLabel(q.qtype) || '\u9898\u76EE') + '</span>',
        '<div class="difficulty">',
        Array.from({length: 5}, (_, i) => '<span class="dot ' + (i < (q.difficulty || 1) ? 'filled' : '') + '"></span>').join(''),
        '</div>',
        '</div>',
        '<span class="text-muted" style="font-size:12px; font-weight:600; opacity:0.5;">' + q.qid + '</span>',
        '</div>',
        '<div class="text-muted" style="font-size:0.8rem; margin-bottom:12px; display:flex; flex-wrap:wrap; gap:12px;">',
        chapters.length ? '<span>' + chapters.join(' / ') + '</span>' : '',
        q.source_file_name ? '<span>' + q.source_file_name + '</span>' : '',
        '</div>',
        '<div class="question-content">' + renderMarkdown(q.content) + '</div>',
        tags.length ? [
          '<div class="flex flex-wrap gap-2" style="margin-top:16px;">',
          tags.map(t => '<span class="tag-chip no-hover">' + t + '</span>').join(''),
          '</div>',
        ].join('') : '',
        '<button class="btn btn-sm btn-secondary toggle-answer" style="margin-top:20px;">',
        '<i data-lucide="eye" style="width:14px;height:14px;"></i>',
        '\u663E\u793A\u89E3\u6790',
        '</button>',
        '<div class="answer-section">',
        '<h4 style="margin-bottom:12px;">\u7B54\u6848</h4>',
        renderMarkdown(q.answer || '(\u65E0\u7B54\u6848)'),
        q.explanation ? [
          '<h4 style="margin-top:24px; margin-bottom:12px;">\u89E3\u6790</h4>',
          renderMarkdown(q.explanation),
        ].join('') : '',
        '</div>',
        '<div class="flex gap-2" style="margin-top:12px;">',
        '<button class="btn btn-sm btn-secondary edit-q" data-qid="' + q.qid + '">',
        '<i data-lucide="pencil" style="width:14px;height:14px;"></i>',
        '\u7F16\u8F91',
        '</button>',
        '<button class="btn btn-sm btn-danger delete-q" data-qid="' + q.qid + '">',
        '<i data-lucide="trash-2" style="width:14px;height:14px;"></i>',
        '\u5220\u9664',
        '</button>',
        '</div>',
        '</div>',
      ].join('');
    }).join('');

    listEl.querySelectorAll('.toggle-answer').forEach(btn => {
      btn.addEventListener('click', () => {
        const section = btn.nextElementSibling;
        section.classList.toggle('open');
        const isOpen = section.classList.contains('open');
        btn.innerHTML = isOpen
          ? '<i data-lucide="eye-off" style="width:14px;height:14px;"></i>\u9690\u85CF\u89E3\u6790'
          : '<i data-lucide="eye" style="width:14px;height:14px;"></i>\u663E\u793A\u89E3\u6790';
        lucide.createIcons();
      });
    });

    listEl.querySelectorAll('.delete-q').forEach(btn => {
      btn.addEventListener('click', async () => {
        if (!confirm('\u786E\u5B9A\u5220\u9664 ' + btn.dataset.qid + '\uFF1F')) return;
        try {
          await API.del('/api/courses/' + courseId + '/questions/' + btn.dataset.qid);
          await loadData();
        } catch (e) {
          window.toast('\u5220\u9664\u5931\u8D25\uFF1A' + e.message, 'error');
        }
      });
    });
  }


  function buildEditForm(q) {
    var qtypeOptions = [
      {value:'single_choice', label:'单选题'},
      {value:'multiple_choice', label:'多选题'},
      {value:'fill_blank', label:'填空题'},
      {value:'true_false', label:'判断题'},
      {value:'short_answer', label:'简答题'},
      {value:'essay', label:'论述题'},
      {value:'comprehensive', label:'综合题'},
    ];
    return [
      '<div class="edit-form">',
      '<div class="edit-form-row">',
      '<label style="display:block;font-size:0.8rem;font-weight:600;margin-bottom:4px;">题型</label>',
      '<select class="form-select edit-qtype">',
      '<option value="">-- 不修改 --</option>',
      qtypeOptions.map(function(o) { return '<option value="' + o.value + '"' + (q.qtype === o.value ? ' selected' : '') + '>' + o.label + '</option>'; }).join(''),
      '</select>',
      '</div>',
      '<div class="edit-form-row" style="margin-top:12px;">',
      '<label style="display:block;font-size:0.8rem;font-weight:600;margin-bottom:4px;">难度</label>',
      '<select class="form-select edit-difficulty">',
      [1,2,3,4,5].map(function(d) { return '<option value="' + d + '"' + (q.difficulty === d ? ' selected' : '') + '>' + d + '</option>'; }).join(''),
      '</select>',
      '</div>',
      '<div class="edit-form-row" style="margin-top:12px;">',
      '<label style="display:block;font-size:0.8rem;font-weight:600;margin-bottom:4px;">题目内容</label>',
      '<textarea class="form-textarea edit-content" rows="6">' + (q.content || '') + '</textarea>',
      '</div>',
      '<div class="edit-form-row" style="margin-top:12px;">',
      '<label style="display:block;font-size:0.8rem;font-weight:600;margin-bottom:4px;">答案</label>',
      '<textarea class="form-textarea edit-answer" rows="4">' + (q.answer || '') + '</textarea>',
      '</div>',
      '<div class="edit-form-row" style="margin-top:12px;">',
      '<label style="display:block;font-size:0.8rem;font-weight:600;margin-bottom:4px;">解析</label>',
      '<textarea class="form-textarea edit-explanation" rows="4">' + (q.explanation || '') + '</textarea>',
      '</div>',
      '<div class="edit-form-row" style="margin-top:12px;">',
      '<label style="display:block;font-size:0.8rem;font-weight:600;margin-bottom:4px;">知识点标签</label>',
      '<input class="form-input edit-tags" value="' + (q.knowledge_tags || '') + '" placeholder="逗号分隔">',
      '</div>',
      '<div class="flex gap-2" style="margin-top:16px;">',
      '<button class="btn btn-sm btn-primary save-q" data-qid="' + q.qid + '"><i data-lucide="check" style="width:14px;height:14px;"></i> 保存</button>',
      '<button class="btn btn-sm btn-secondary cancel-q" data-qid="' + q.qid + '"><i data-lucide="x" style="width:14px;height:14px;"></i> 取消</button>',
      '</div>',
      '</div>',
    ].join('');
  }

  // Edit/save/cancel delegation (attach once)
  if (!listEl._editDel) {
    listEl._editDel = true;
    listEl.addEventListener('click', function(e) {
      var editBtn = e.target.closest('.edit-q');
      if (editBtn) {
        e.preventDefault();
        var qid = editBtn.dataset.qid;
        var q = allQuestions.find(function(q) { return q.qid === qid; });
        if (!q) return;
        var card = editBtn.closest('.question-card');
        if (!card) return;
        card.innerHTML = buildEditForm(q);
        lucide.createIcons();
        e.stopPropagation();
        return;
      }
      var saveBtn = e.target.closest('.save-q');
      if (saveBtn) {
        e.preventDefault();
        var qid = saveBtn.dataset.qid;
        var card = saveBtn.closest('.question-card');
        if (!card) return;
        var form = card.querySelector('.edit-form');
        if (!form) return;
        var data = {};
        var qtype = form.querySelector('.edit-qtype');
        if (qtype && qtype.value) data.qtype = qtype.value;
        var difficulty = form.querySelector('.edit-difficulty');
        if (difficulty) data.difficulty = parseInt(difficulty.value) || 1;
        var content = form.querySelector('.edit-content');
        if (content) data.content = content.value;
        var answer = form.querySelector('.edit-answer');
        if (answer) data.answer = answer.value;
        var explanation = form.querySelector('.edit-explanation');
        if (explanation) data.explanation = explanation.value;
        var tags = form.querySelector('.edit-tags');
        if (tags) data.knowledge_tags = tags.value;
        API.put('/api/courses/' + courseId + '/questions/' + qid, data).then(function() {
          return loadData();
        }).catch(function(err) {
          window.toast('保存失败：' + (err.message || String(err)), 'error');
        });
        e.stopPropagation();
        return;
      }
      var cancelBtn = e.target.closest('.cancel-q');
      if (cancelBtn) {
        e.preventDefault();
        loadData();
        e.stopPropagation();
        return;
      }
    });
  }
  await loadData();
}
