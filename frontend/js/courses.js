/* Course list page (#/). */
router.register('/', async (app) => {
  app.innerHTML = `
    <div class="flex justify-between items-center mb-section">
      <div>
        <h1 style="margin-bottom:0">我的课程</h1>
        <p class="text-muted">管理您的学习资料与自动生成的题库</p>
      </div>
      <button id="btn-new-course" class="btn btn-primary">
        <i data-lucide="plus" style="width:18px;height:18px;"></i>
        新建课程
      </button>
    </div>
    <div id="course-list" class="course-grid"></div>
  `;

  const listEl = app.querySelector('#course-list');
  const btnNew = app.querySelector('#btn-new-course');

  async function deleteCourse(id) {
    const ok = await window.showConfirm('确定要删除这门课程吗？所有相关文件和题目都将被永久删除。');
    if (!ok) return;
    try {
      await API.del(`/api/courses/${id}`);
      window.toast('课程已删除');
      loadCourses();
    } catch (e) {
      window.toast('删除失败', 'error');
    }
  }

  async function loadCourses() {
    try {
      const courses = await API.get('/api/courses');
      if (courses.length === 0) {
        listEl.innerHTML = `
          <div class="empty-state">
            <i data-lucide="book-open" style="width:64px;height:64px;"></i>
            <h3>开始你的学习之旅</h3>
            <p class="text-muted" style="max-width:300px; margin:0 auto 24px;">还没有课程。创建一个新课程，上传试卷，让 AI 为你精准提炼考点。</p>
            <button class="btn btn-secondary" onclick="document.getElementById('btn-new-course').click()">立即新建</button>
          </div>`;
        lucide.createIcons();
        return;
      }
      listEl.innerHTML = courses.map((c, i) => `
        <div class="card course-card" data-id="${c.id}">
          <div class="card-num">${String(i + 1).padStart(2, '0')}</div>
          <div class="card-body course-info" style="cursor:pointer;">
            <div class="card-title">${c.name}</div>
            <div class="card-meta">
              <span class="meta-span"><i data-lucide="file-text" style="width:15px;height:15px;"></i>${c.file_count || 0} 个文件</span>
              <span class="meta-span"><i data-lucide="help-circle" style="width:15px;height:15px;"></i>${c.question_count || 0} 道题目</span>
            </div>
          </div>
          <div style="display:flex; align-items:center; gap:8px; position:relative;">
            <div class="card-arrow">
              <i data-lucide="chevron-right" style="width:20px;height:20px;"></i>
            </div>
            <button class="btn btn-xs btn-danger btn-delete-course" data-id="${c.id}" style="opacity:0; transition:opacity 0.2s;" title="删除">
              <i data-lucide="trash-2" style="width:12px;height:12px;"></i>
            </button>
          </div>
        </div>
      `).join('');
      
      listEl.querySelectorAll('.course-card').forEach(el => {
        el.addEventListener('mouseenter', () => {
          const btn = el.querySelector('.btn-delete-course');
          if (btn) btn.style.opacity = '1';
        });
        el.addEventListener('mouseleave', () => {
          const btn = el.querySelector('.btn-delete-course');
          if (btn) btn.style.opacity = '0';
        });
      });
      
      listEl.querySelectorAll('.course-info').forEach(el => {
        el.addEventListener('click', () => router.navigate(`/course/${el.closest('.course-card').dataset.id}`));
      });
      
      listEl.querySelectorAll('.btn-delete-course').forEach(el => {
        el.addEventListener('click', (e) => {
          e.stopPropagation();
          deleteCourse(el.dataset.id);
        });
      });
      
      lucide.createIcons();
    } catch (e) {
      window.toast('加载失败', 'error');
    }
  }

  btnNew.addEventListener('click', async () => {
    const name = await window.showPrompt('请输入课程名称：', '例如：高等数学');
    if (!name) return;
    try {
      await API.post('/api/courses', { name: name.trim() });
      window.toast('课程创建成功');
      loadCourses();
    } catch (e) {
      window.toast('创建失败', 'error');
    }
  });

  await loadCourses();
});
