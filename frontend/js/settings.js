/* Settings page — standalone top-level route (#/settings). */
const PROVIDERS = [
  { id: 'opencode-zen', name: 'OpenCode Zen', endpoint: 'https://opencode.ai/zen/v1' },
  { id: 'opencode-go', name: 'OpenCode Go', endpoint: 'https://opencode.ai/zen/go/v1' },
  { id: 'deepseek', name: 'DeepSeek', endpoint: 'https://api.deepseek.com/v1' },
  { id: 'ollama', name: 'Ollama Cloud', endpoint: 'https://ollama.com' },
  { id: 'openai', name: 'OpenAI', endpoint: 'https://api.openai.com/v1' },
  { id: 'custom', name: '自定义', endpoint: '' },
];

function inferProvider(endpoint) {
  if (!endpoint) return 'custom';
  if (endpoint.startsWith('https://opencode.ai/zen')) return 'opencode-zen';
  if (endpoint.startsWith('https://opencode.ai/go')) return 'opencode-go';
  if (endpoint.startsWith('https://ollama.com')) return 'ollama';
  if (endpoint.startsWith('http://localhost:11434')) return 'ollama';
  if (endpoint.startsWith('https://api.openai.com')) return 'openai';
  return 'custom';
}

async function fetchModels(providerId, endpoint, apiKey) {
  if (!endpoint) throw new Error('Endpoint 不能为空');
  if (providerId !== 'ollama' && !apiKey) throw new Error('请先填写 API Key');

  const resp = await API.post('/api/llm/models', {
    provider_id: providerId,
    endpoint: endpoint,
    api_key: apiKey,
  });

  return resp && Array.isArray(resp.models) ? resp.models : [];
}

router.register('/settings', async function (app) {
  await fetchDefaults();
  var providerId = getDefaultProvider();
  var cfg = getLLMConfig();

  app.innerHTML = [
    '<div style="margin-bottom:32px;">',
    '  <h1>设置</h1>',
    '  <p class="text-muted">凭据仅存储在浏览器本地。请确保您的 API 余额充足。</p>',
    '</div>',
    '<div class="card mb-4">',
    '  <h3 class="mb-2 flex items-center gap-2">',
    '    <i data-lucide="cpu" style="width:20px;height:20px;color:var(--primary);"></i>',
    '    MinerU 配置',
    '  </h3>',
    '  <div class="form-group">',
    '    <label>MinerU Token</label>',
    '    <input type="password" id="input-mineru-token" value="' + (cfg.mineru_token || '') + '" placeholder="输入 MinerU API Token">',
    '  </div>',
    '</div>',

    '<div class="card">',
    '  <h3 class="mb-2 flex items-center gap-2">',
    '    <i data-lucide="sparkles" style="width:20px;height:20px;color:var(--primary);"></i>',
    '    LLM 配置',
    '  </h3>',
    '  <p class="text-subtle mb-2" style="margin-bottom:20px;">用于题目抽取、知识点整理与解析生成。</p>',


    '  <div class="form-group">',
    '    <label>默认提供商</label>',
    '    <select id="input-llm-provider">',
          PROVIDERS.map(function (p) {
            return '<option value="' + p.id + '"' + (p.id === providerId ? ' selected' : '') + '>' + p.name + '</option>';
          }).join(''),
    '    </select>',
    '    <div style="font-size:0.8rem;color:var(--fg-muted);margin-top:2px;">',
    '      默认: <span id="default-provider-label"></span>',
    '      <a href="#" id="btn-set-default" style="margin-left:8px;">设为默认</a>',
    '    </div>',
    '  </div>',

    '  <div class="form-group">',
    '    <label>API Key</label>',
    '    <div style="display:flex;gap:8px;">',
    '      <input type="password" id="input-llm-key" value="' + (cfg.llm_key || '') + '" placeholder="sk-..." style="flex:1;">',
    '      <button class="btn btn-xs btn-ghost" id="btn-toggle-key" title="显示/隐藏 Key" type="button" style="padding:4px 8px;">',
    '        <i data-lucide="eye" style="width:14px;height:14px;"></i>',
    '      </button>',
    '    </div>',
    '  </div>',

    '  <div class="form-group">',
    '    <label>端点 (Endpoint)</label>',
    '    <input type="text" id="input-llm-endpoint" value="' + (cfg.llm_endpoint || '') + '" placeholder="https://...">',
    '  </div>',
    '  <div class="form-group">',
    '    <label>模型</label>',
    '    <div style="display:flex;gap:8px;">',
    '      <input type="text" id="input-llm-model" value="' + (cfg.llm_model || '') + '" placeholder="选择或输入模型名称…" style="flex:1;" list="model-list">',
    '      <datalist id="model-list"></datalist>',
    '      <button class="btn btn-secondary" id="btn-fetch-models" style="white-space:nowrap;">',
    '        <i data-lucide="refresh-cw" style="width:14px;height:14px;"></i> 获取列表',
    '      </button>',
    '    </div>',
    '  </div>',
    '</div>',
    '<div class="mt-4 flex items-center gap-2">',
    '  <span id="save-status" class="text-muted" style="font-weight:700;"></span>',
    '  <button class="btn btn-primary" id="btn-save-config">',
    '    <i data-lucide="save" style="width:18px;height:18px;"></i>',
    '    保存配置',
    '  </button>',
    '</div>',
  ].join('\n');

  lucide.createIcons();

  // ── Provider switch → endpoint auto-fill ───────────────────────
  var providerSel = document.getElementById('input-llm-provider');
  var endpointInput = document.getElementById('input-llm-endpoint');
  var modelInput = document.getElementById('input-llm-model');

  providerSel.addEventListener('change', function () {
    var prov = PROVIDERS.find(function (p) { return p.id === providerSel.value; });
    if (prov && prov.endpoint) {
      endpointInput.value = prov.endpoint;
    }
    // Load this provider's saved config
    var pCfg = getProviderConfig(providerSel.value);
    if (pCfg.key) document.getElementById('input-llm-key').value = pCfg.key;
    if (pCfg.model) modelInput.value = pCfg.model;
    if (pCfg.endpoint) endpointInput.value = pCfg.endpoint;
    updateDefaultUI();
  });

  // ── "设为默认" button ──────────────────────────────────────────────
  var defaultLabel = document.getElementById('default-provider-label');
  var setDefaultBtn = document.getElementById('btn-set-default');
  function updateDefaultUI() {
    var current = providerSel.value;
    var def = getDefaultProvider();
    var prov = PROVIDERS.find(function (p) { return p.id === def; });
    defaultLabel.textContent = prov ? prov.name : def;
    setDefaultBtn.style.display = current === def ? 'none' : 'inline';
  }
  updateDefaultUI();

  setDefaultBtn.addEventListener('click', function (e) {
    e.preventDefault();
    setDefaultProvider(providerSel.value);
    updateDefaultUI();
    window.toast('默认提供商已更新');
  });

  // ── API Key show/hide toggle ───────────────────────────────────────
  var keyInput = document.getElementById('input-llm-key');
  document.getElementById('btn-toggle-key').addEventListener('click', function () {
    var isPassword = keyInput.type === 'password';
    keyInput.type = isPassword ? 'text' : 'password';
    this.innerHTML = isPassword
      ? '<i data-lucide="eye-off" style="width:14px;height:14px;"></i>'
      : '<i data-lucide="eye" style="width:14px;height:14px;"></i>';
    lucide.createIcons();
  });
  // ── Fetch model list ───────────────────────────────────────────
  document.getElementById('btn-fetch-models').addEventListener('click', async function () {
    var provId = providerSel.value;
    var ep = endpointInput.value.trim();
    var key = document.getElementById('input-llm-key').value.trim();

    if (!ep || !key) {
      window.toast('请先填写 Endpoint 和 API Key', 'error');
      return;
    }

    var btn = this;
    btn.disabled = true;
    btn.innerHTML = '<i data-lucide="loader" style="width:14px;height:14px;"></i> 获取中…';
    lucide.createIcons();

    try {
      var models = await fetchModels(provId, ep, key);
      if (models.length === 0) {
        window.toast('未获取到模型列表', 'error');
        return;
      }
      var dl = document.getElementById('model-list');
      dl.innerHTML = models.map(function (m) {
        return '<option value="' + m.value + '">' + m.label + '</option>';
      }).join('');

      // Pick first model if input is empty
      if (!modelInput.value && models.length > 0) {
        modelInput.value = models[0].value;
      }

      window.toast('获取到 ' + models.length + ' 个模型', 'success');
    } catch (e) {
      window.toast('获取模型列表失败: ' + e.message, 'error');
    } finally {
      btn.disabled = false;
      btn.innerHTML = '<i data-lucide="refresh-cw" style="width:14px;height:14px;"></i> 获取列表';
      lucide.createIcons();
    }
  });

  // ── Save config ────────────────────────────────────────────────
  document.getElementById('btn-save-config').addEventListener('click', function () {
    var currentId = providerSel.value;
    var key = document.getElementById('input-llm-key').value;
    var ep = endpointInput.value;
    var model = modelInput.value;
    var mineru = document.getElementById('input-mineru-token').value;

    // Save under current provider
    setProviderConfig(currentId, { key: key, endpoint: ep, model: model });
    setDefaultProvider(currentId);

    // Also write legacy globals for backward compat
    localStorage.setItem('exam_killer_llm_key', key);
    localStorage.setItem('exam_killer_llm_endpoint', ep);
    localStorage.setItem('exam_killer_llm_model', model);
    localStorage.setItem('exam_killer_mineru_token', mineru);

    updateDefaultUI();
    window.toast('配置已成功保存');
  });
});
