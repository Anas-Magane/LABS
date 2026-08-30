// Aramoon - Student Space platform.
//
// Public marketing site + a small authenticated student area + an
// internal "ReactoShell" tool restricted to staff accounts.
'use strict';

const express = require('express');
const path = require('path');
const cookieParser = require('cookie-parser');
const { VM } = require('vm2');
const React = require('react');
const ReactDOMServer = require('react-dom/server');

const store = require('./lib/store');
const views = require('./lib/views');

const app = express();
app.disable('x-powered-by');
app.use(express.json({ limit: '10kb' }));
app.use(express.urlencoded({ extended: false }));
app.use(cookieParser());

// Static marketing site (public, no auth) - clean URLs, no .html.
app.use(express.static(path.join(__dirname, 'site'), { extensions: ['html'] }));
app.use('/assets', express.static(path.join(__dirname, 'public')));

// ---------------------------------------------------------------------------
// Auth plumbing
// ---------------------------------------------------------------------------

app.use((req, res, next) => {
  const token = req.cookies && req.cookies.sid;
  req.user = (token && store.getUserBySessionToken(token)) || null;
  next();
});

function requireAuthPage(req, res, next) {
  if (!req.user) return res.redirect('/login');
  next();
}

function requireAuthApi(req, res, next) {
  if (!req.user) return res.status(401).json({ error: 'Not authenticated.' });
  next();
}

function requireStaffPage(req, res, next) {
  if (!req.user) return res.redirect('/login');
  if (req.user.role !== 'staff') return res.status(403).send(views.forbiddenPage());
  next();
}

function requireStaffApi(req, res, next) {
  if (!req.user) return res.status(401).json({ error: 'Not authenticated.' });
  if (req.user.role !== 'staff') return res.status(403).json({ error: 'Staff role required.' });
  next();
}

// ---------------------------------------------------------------------------
// Registration / login / logout
// ---------------------------------------------------------------------------

app.get('/register', (req, res) => {
  if (req.user) return res.redirect('/dashboard');
  res.send(views.registerPage({}));
});

app.post('/api/register', (req, res) => {
  const { username, email, password } = req.body || {};
  if (!username || !email || !password) {
    return res.status(400).send(views.registerPage({ error: 'All fields are required.' }));
  }
  try {
    const user = store.createUser({ username, email, password });
    const token = store.createSession(user.id);
    res.cookie('sid', token, { httpOnly: true, sameSite: 'lax' });
    res.redirect('/dashboard');
  } catch (e) {
    res.status(400).send(views.registerPage({ error: e.message }));
  }
});

app.get('/login', (req, res) => {
  if (req.user) return res.redirect('/dashboard');
  res.send(views.loginPage({}));
});

app.post('/api/login', (req, res) => {
  const { email, password } = req.body || {};
  const user = email && store.findByEmail(email);
  if (!user || !store.verifyPassword(user, password || '')) {
    return res.status(401).send(views.loginPage({ error: 'Invalid email or password.' }));
  }
  const token = store.createSession(user.id);
  res.cookie('sid', token, { httpOnly: true, sameSite: 'lax' });
  res.redirect('/dashboard');
});

app.post('/api/logout', (req, res) => {
  const token = req.cookies && req.cookies.sid;
  if (token) store.destroySession(token);
  res.clearCookie('sid');
  res.redirect('/');
});

// ---------------------------------------------------------------------------
// Student area
// ---------------------------------------------------------------------------

app.get('/dashboard', requireAuthPage, (req, res) => {
  res.send(views.dashboardPage(req.user));
});

app.get('/profile', requireAuthPage, (req, res) => {
  res.send(views.profilePage(req.user, {}));
});

// Profile update. Intentionally merges the whole request body into the
// stored account record with no field allowlist - the edit form only
// sends { username, bio, github }, but nothing on the server stops any
// other JSON field (e.g. `role`) from riding along.
app.patch('/api/profile', requireAuthApi, (req, res) => {
  const updates = req.body || {};
  Object.assign(req.user, updates);
  res.json({ ok: true, profile: store.publicProfile(req.user) });
});

// ---------------------------------------------------------------------------
// Staff-only: ReactoShell internal tool
// ---------------------------------------------------------------------------

app.get('/staff/tools/reactoshell', requireStaffPage, (req, res) => {
  res.send(views.reactoshellPage(req.user));
});

app.post('/staff/tools/reactoshell/api/render', requireStaffApi, (req, res) => {
  const code = req.body && req.body.code;
  if (typeof code !== 'string' || !code.trim()) {
    return res.status(400).json({ error: 'Missing "code" field.' });
  }
  if (code.length > 4000) {
    return res.status(400).json({ error: 'Code too long for the preview sandbox.' });
  }

  try {
    const vm = new VM({
      timeout: 2000,
      sandbox: { React, console: { log() {}, error() {} } },
    });
    const result = vm.run(code);

    let html;
    if (result && typeof result === 'object' && result.$$typeof) {
      html = ReactDOMServer.renderToStaticMarkup(result);
    } else if (result === null || result === undefined) {
      html = '<em>(no value - end your snippet with a React element expression)</em>';
    } else {
      html = `<pre>${String(result).replace(/</g, '&lt;')}</pre>`;
    }
    res.json({ html });
  } catch (err) {
    res.status(500).json({ error: 'Run error: ' + err.message });
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, '0.0.0.0', () => {
  console.log(`Aramoon platform listening on :${PORT}`);
});
