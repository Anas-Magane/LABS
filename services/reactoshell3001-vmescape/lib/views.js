'use strict';

function esc(s) {
  return String(s == null ? '' : s).replace(/[&<>"']/g, (c) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
  }[c]));
}

function layout({ title, user, body, extraHead = '' }) {
  const navRight = user
    ? `<a href="/dashboard">Dashboard</a><form action="/api/logout" method="POST" class="inline-form"><button class="link-btn" type="submit">Log out</button></form>`
    : `<a href="/login">Log in</a><a class="btn btn-primary btn-sm" href="/register">Register</a>`;

  return `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>${esc(title)} - Aramoon</title>
  <link rel="stylesheet" href="/assets/style.css">
  ${extraHead}
</head>
<body>
<nav class="nav">
  <a href="/" class="brand"><img src="/assets/aramoon-logo.svg" alt="Aramoon" height="26"></a>
  <ul class="nav-links">
    <li><a href="/programs">Programs</a></li>
    <li><a href="/ecosystem">Ecosystem</a></li>
    <li><a href="/services">Services</a></li>
    <li><a href="/institution">Institution</a></li>
  </ul>
  <div class="nav-right">${navRight}</div>
</nav>
${body}
<footer>
  <span>&copy; 2026 Aramoon. Learn. Practice. Build.</span>
  <span>support@aramoon.ma &middot; @aramoon_it</span>
</footer>
</body>
</html>`;
}

function authLayout({ title, formTitle, error, action, fields, footer }) {
  return layout({
    title,
    user: null,
    body: `
<div class="auth-wrap">
  <h1>${esc(formTitle)}</h1>
  ${error ? `<div class="alert alert-error">${esc(error)}</div>` : ''}
  <form method="POST" action="${action}" class="stacked-form">
    ${fields}
    <button class="btn btn-primary" type="submit">${esc(formTitle)}</button>
  </form>
  <p class="muted">${footer}</p>
</div>`,
  });
}

function loginPage({ error } = {}) {
  return authLayout({
    title: 'Log in',
    formTitle: 'Log in',
    error,
    action: '/api/login',
    fields: `
      <label>Email
        <input type="email" name="email" required autofocus>
      </label>
      <label>Password
        <input type="password" name="password" required>
      </label>`,
    footer: `New here? <a href="/register">Create a student account</a>.`,
  });
}

function registerPage({ error } = {}) {
  return authLayout({
    title: 'Register',
    formTitle: 'Create your account',
    error,
    action: '/api/register',
    fields: `
      <label>Full name
        <input type="text" name="username" required autofocus>
      </label>
      <label>Email
        <input type="email" name="email" required>
      </label>
      <label>Password
        <input type="password" name="password" required minlength="6">
      </label>`,
    footer: `Already enrolled? <a href="/login">Log in</a>.`,
  });
}

function dashboardPage(user) {
  const staffPanel = user.role === 'staff' ? `
    <div class="card card-accent">
      <h3>Staff Tools</h3>
      <p class="muted">Internal web-tooling utilities. Staff role required.</p>
      <a class="btn btn-outline btn-sm" href="/staff/tools/reactoshell">Open ReactoShell &rarr;</a>
    </div>` : '';

  return layout({
    title: 'Dashboard',
    user,
    body: `
<div class="tool-wrap">
  <h1>Welcome back, ${esc(user.username)}.</h1>
  <div class="card-grid">
    <div class="card">
      <h3>Profile</h3>
      <p class="muted">Cohort: ${esc(user.cohort)} &middot; Role: <code>${esc(user.role)}</code></p>
      <a class="btn btn-outline btn-sm" href="/profile">Edit profile</a>
    </div>
    <div class="card">
      <h3>My Program</h3>
      <p class="muted">Full-Stack Web Development &mdash; Year 2, Semester 1.</p>
    </div>
    ${staffPanel}
  </div>
</div>`,
  });
}

function profilePage(user, { error, success } = {}) {
  return layout({
    title: 'Profile',
    user,
    body: `
<!-- sprint note: profile save now just PATCHes /api/profile with whatever
     the form state holds - simpler than maintaining a field list by hand
     on both ends. revisit before this gets more fields. -->
<div class="tool-wrap tool-wrap-narrow">
  <h1>Your profile</h1>
  ${error ? `<div class="alert alert-error">${esc(error)}</div>` : ''}
  ${success ? `<div class="alert alert-success">${esc(success)}</div>` : ''}
  <form id="profileForm" class="stacked-form">
    <label>Display name
      <input type="text" name="username" value="${esc(user.username)}">
    </label>
    <label>Bio
      <textarea name="bio" rows="3">${esc(user.bio)}</textarea>
    </label>
    <label>GitHub
      <input type="text" name="github" value="${esc(user.github)}" placeholder="github.com/yourname">
    </label>
    <button class="btn btn-primary" type="submit">Save changes</button>
  </form>
  <div id="status" class="muted" style="margin-top:10px"></div>
</div>
<script>
  document.getElementById('profileForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const fd = new FormData(e.target);
    const body = Object.fromEntries(fd.entries());
    const statusEl = document.getElementById('status');
    statusEl.textContent = 'Saving...';
    try {
      const resp = await fetch('/api/profile', {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      const data = await resp.json();
      statusEl.textContent = resp.ok ? 'Saved.' : (data.error || 'Save failed.');
    } catch (err) {
      statusEl.textContent = 'Network error: ' + err.message;
    }
  });
</script>`,
  });
}

function forbiddenPage() {
  return layout({
    title: '403 Forbidden',
    user: null,
    body: `<div class="tool-wrap"><h1>403</h1><p class="muted">Staff role required for this area.</p></div>`,
  });
}

function reactoshellPage(user) {
  return layout({
    title: 'ReactoShell',
    user,
    body: `
<div class="tool-wrap">
  <h1>ReactoShell</h1>
  <p class="muted">Internal component-preview &amp; automation sandbox for the web tooling team.
    Snippets run inside an isolated <code>vm2</code> virtual machine - only <code>React</code>
    is exposed. End the snippet with a value (a bare expression, no <code>return</code> needed)
    to preview it as a React element.</p>

  <div class="tool-banner">Staff-only internal tool. Sandbox runtime: <code>vm2</code>.</div>

  <div class="tool-grid">
    <div>
      <textarea id="code" spellcheck="false">React.createElement('div', null, 'Hello from ReactoShell!');</textarea>
      <div style="margin-top:12px">
        <button class="btn btn-primary" id="renderBtn" type="button">Run</button>
      </div>
      <div id="status" class="muted"></div>
    </div>
    <div>
      <div id="output"><em>(output will appear here)</em></div>
    </div>
  </div>
</div>
<script>
  const btn = document.getElementById('renderBtn');
  const codeEl = document.getElementById('code');
  const outEl = document.getElementById('output');
  const statusEl = document.getElementById('status');

  btn.addEventListener('click', async () => {
    statusEl.textContent = 'Running...';
    statusEl.className = 'muted';
    try {
      const resp = await fetch('/staff/tools/reactoshell/api/render', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code: codeEl.value }),
      });
      const data = await resp.json();
      if (!resp.ok) {
        statusEl.textContent = data.error || 'Run failed.';
        statusEl.className = 'error';
        return;
      }
      outEl.innerHTML = data.html;
      statusEl.textContent = 'Done.';
    } catch (e) {
      statusEl.textContent = 'Network error: ' + e.message;
      statusEl.className = 'error';
    }
  });
</script>`,
  });
}

module.exports = {
  loginPage,
  registerPage,
  dashboardPage,
  profilePage,
  forbiddenPage,
  reactoshellPage,
  esc,
};
