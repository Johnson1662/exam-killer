/* Shared API config — stored in localStorage, shared by upload & review pages. */

const DEFAULT_LLM = { endpoint: 'https://opencode.ai/zen/v1', model: 'deepseek-v4-flash-free' };
const DEFAULT_PROVIDER_ID = 'opencode-zen';

async function fetchDefaults() {
  try {
    const cfg = await API.get('/api/config');
    DEFAULT_LLM.endpoint = cfg.llm_endpoint || DEFAULT_LLM.endpoint;
    DEFAULT_LLM.model = cfg.llm_model || DEFAULT_LLM.model;
  } catch (_) {}
}

// ── Per-provider config ───────────────────────────────────────────

function getDefaultProvider() {
  return localStorage.getItem('exam_killer_default_provider') || DEFAULT_PROVIDER_ID;
}

function setDefaultProvider(id) {
  localStorage.setItem('exam_killer_default_provider', id);
}

function getProviderConfig(providerId) {
  try {
    return JSON.parse(localStorage.getItem('exam_killer_cfg_' + providerId)) || {};
  } catch (_) { return {}; }
}

function setProviderConfig(providerId, config) {
  localStorage.setItem('exam_killer_cfg_' + providerId, JSON.stringify(config));
}

// ── Legacy global keys (fallback, written on save for compat) ─────

const LEGACY_KEY = 'exam_killer_llm_key';
const LEGACY_EP  = 'exam_killer_llm_endpoint';
const LEGACY_MODEL = 'exam_killer_llm_model';

// ── Public API ────────────────────────────────────────────────────

function getLLMConfig() {
  var mineru = localStorage.getItem('exam_killer_mineru_token');

  // Try default provider's per-provider config first
  var providerId = getDefaultProvider();
  var cfg = getProviderConfig(providerId);

  // Backward compat: if per-provider has no data, fall back to legacy globals
  if (!cfg.key && !cfg.endpoint) {
    return {
      llm_key: localStorage.getItem(LEGACY_KEY),
      llm_endpoint: localStorage.getItem(LEGACY_EP),
      llm_model: localStorage.getItem(LEGACY_MODEL),
      mineru_token: mineru,
    };
  }

  return {
    llm_key: cfg.key || '',
    llm_endpoint: cfg.endpoint || '',
    llm_model: cfg.model || '',
    mineru_token: mineru,
  };
}

function saveLLMConfig(key, endpoint, model, mineruToken) {
  var providerId = getDefaultProvider();

  // Write per-provider
  setProviderConfig(providerId, { key: key, endpoint: endpoint, model: model });

  // Write legacy globals too (some callers may read them directly)
  localStorage.setItem(LEGACY_KEY, key);
  localStorage.setItem(LEGACY_EP, endpoint);
  localStorage.setItem(LEGACY_MODEL, model);
  localStorage.setItem('exam_killer_mineru_token', mineruToken);
}

function isLLMConfigured() {
  var cfg = getLLMConfig();
  return !!(cfg.llm_key && cfg.llm_endpoint && cfg.llm_model);
}

function isMineruConfigured() {
  return !!getLLMConfig().mineru_token;
}
