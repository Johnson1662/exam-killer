/* API helper — thin fetch wrapper. */
const API = {
  async get(path) {
    const r = await fetch(path);
    if (!r.ok) {
      const msg = await r.text().catch(() => r.statusText);
      throw new Error(msg);
    }
    return r.json();
  },

  async post(path, body) {
    const r = await fetch(path, {
      method: 'POST',
      headers: body instanceof FormData ? {} : { 'Content-Type': 'application/json' },
      body: body instanceof FormData ? body : JSON.stringify(body),
    });
    if (!r.ok) {
      const msg = await r.text().catch(() => r.statusText);
      throw new Error(msg);
    }
    return r.json();
  },

  async put(path, body) {
    const r = await fetch(path, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    if (!r.ok) {
      const msg = await r.text().catch(() => r.statusText);
      throw new Error(msg);
    }
    return r.json();
  },

  async del(path) {
    const r = await fetch(path, { method: 'DELETE' });
    if (!r.ok) {
      const msg = await r.text().catch(() => r.statusText);
      throw new Error(msg);
    }
    return r.json();
  },

  async upload(path, formData) {
    const r = await fetch(path, { method: 'POST', body: formData });
    if (!r.ok) {
      const msg = await r.text().catch(() => r.statusText);
      throw new Error(msg);
    }
    return r.json();
  },
};
