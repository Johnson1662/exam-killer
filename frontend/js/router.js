/* Simple hash-based SPA router. */
const router = {
  routes: {},

  register(pattern, handler) {
    this.routes[pattern] = handler;
  },

  init() {
    window.addEventListener('hashchange', () => this.resolve());
    this.resolve();
  },

  resolve() {
    const hash = location.hash.slice(1) || '/';

    const app = document.getElementById('app');

    for (const [pattern, handler] of Object.entries(this.routes)) {
      const regexSource = '^' + pattern.replace(/\./g, '\\.').replace(/:\w+/g, '([^/]+)') + '$';
      const regex = new RegExp(regexSource);
      const match = hash.match(regex);
      if (match) {
        const params = match.slice(1);
        handler(app, ...params);
        return;
      }
    }

    // Default: 404
    app.innerHTML = '<h2>404</h2><p>页面未找到</p>';
  },

  navigate(path) {
    location.hash = '#' + path;
  },
};
