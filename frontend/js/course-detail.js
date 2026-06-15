/* Course detail page (#/course/:id). */
router.register('/course/:id', async (app, id) => {
  app.innerHTML = '<div id="course-header"></div><div class="tabs" id="tabs"></div><div id="tab-content"></div>';

  let course = null;

  async function loadCourse() {
    try {
      const courses = await API.get('/api/courses');
      course = courses.find(c => c.id == id);
      if (!course) { 
        app.innerHTML = `
          <div class="empty-state">
            <i data-lucide="alert-triangle" style="width:64px;height:64px;"></i>
            <h3>课程未找到</h3>
            <p class="text-muted">该课程可能已被删除或不存在。</p>
            <button class="btn btn-secondary mt-2" onclick="router.navigate('/')">返回列表</button>
          </div>`;
        lucide.createIcons();
        return; 
      }
      
      document.getElementById('course-header').innerHTML = `
        <div class="mb-section">
          <div class="flex items-center gap-2 mb-2">
            <button class="btn btn-sm btn-secondary" onclick="router.navigate('/')" title="返回列表">
              <i data-lucide="arrow-left" style="width:16px;height:16px;"></i>
            </button>
            <h1 style="margin:0">${course.name}</h1>
          </div>
          <div class="flex gap-2">
            <button class="btn btn-sm btn-secondary" id="btn-export-rg">
              <i data-lucide="download" style="width:16px;height:16px;"></i>
              导出复习手册
            </button>
            <button class="btn btn-sm btn-danger" id="btn-delete-course">
              <i data-lucide="trash-2" style="width:16px;height:16px;"></i>
              删除课程
            </button>
          </div>
        </div>
      `;
      
      document.getElementById('btn-delete-course').addEventListener('click', async () => {
        const ok = await window.showConfirm(`确定删除课程"${course.name}"及其所有数据？`);
        if (!ok) return;
        try {
          await API.del(`/api/courses/${id}`);
          window.toast('课程已删除');
          router.navigate('/');
        } catch (err) { window.toast('删除失败', 'error'); }
      });
      
      document.getElementById('btn-export-rg').addEventListener('click', () => {
        window.open(`/api/courses/${id}/export/md?scope=review-guide`, '_blank');
      });
      
      lucide.createIcons();
    } catch (e) {
      window.toast('加载失败', 'error');
    }
  }

  // Tabs
  const tabs = [
    { key: 'upload', label: '上传 & 解析', icon: 'upload-cloud' },
    { key: 'questions', label: '题库', icon: 'database' },
    { key: 'review', label: '复习手册', icon: 'file-text' },
  ];
  const tabsEl = document.getElementById('tabs');
  const contentEl = document.getElementById('tab-content');

  function showTab(key) {
    tabsEl.innerHTML = tabs.map(t =>
      `<button class="tab ${t.key === key ? 'active' : ''}" data-key="${t.key}">
        <i data-lucide="${t.icon}"></i>
        ${t.label}
      </button>`
    ).join('');
    
    tabsEl.querySelectorAll('.tab').forEach(el => {
      el.addEventListener('click', () => showTab(el.dataset.key));
    });

    switch (key) {
      case 'upload': renderUpload(contentEl, id, course); break;
      case 'questions': renderQuestionBank(contentEl, id, course); break;
      case 'review': renderReviewGuide(contentEl, id, course); break;
    }
    lucide.createIcons();
  }

  await loadCourse();
  showTab('upload');
});
