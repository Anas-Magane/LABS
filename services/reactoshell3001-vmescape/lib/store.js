// In-memory user/session store. Ephemeral by design (like the Dev Panel's
// SQLite challenge and the SMB passdb) - a container restart resets the
// whole platform back to zero accounts, nothing baked in here is a secret.
'use strict';

const crypto = require('crypto');

const usersById = new Map();
const userIdByEmail = new Map();
const sessions = new Map(); // token -> userId

let nextId = 1;

function hash(password, salt) {
  return crypto.scryptSync(password, salt, 32).toString('hex');
}

function createUser({ username, email, password }) {
  const normalizedEmail = String(email).trim().toLowerCase();
  if (userIdByEmail.has(normalizedEmail)) {
    throw new Error('An account with that email already exists.');
  }
  const salt = crypto.randomBytes(16).toString('hex');
  const user = {
    id: nextId++,
    username: String(username).trim(),
    email: normalizedEmail,
    salt,
    passwordHash: hash(password, salt),
    role: 'student',
    cohort: 'Fall 2026',
    bio: '',
    github: '',
  };
  usersById.set(user.id, user);
  userIdByEmail.set(normalizedEmail, user.id);
  return user;
}

function findByEmail(email) {
  const id = userIdByEmail.get(String(email).trim().toLowerCase());
  return id ? usersById.get(id) : undefined;
}

function findById(id) {
  return usersById.get(id);
}

function verifyPassword(user, password) {
  return hash(password, user.salt) === user.passwordHash;
}

function createSession(userId) {
  const token = crypto.randomBytes(24).toString('hex');
  sessions.set(token, userId);
  return token;
}

function getUserBySessionToken(token) {
  const id = sessions.get(token);
  return id ? usersById.get(id) : undefined;
}

function destroySession(token) {
  sessions.delete(token);
}

function publicProfile(user) {
  return {
    id: user.id,
    username: user.username,
    email: user.email,
    role: user.role,
    cohort: user.cohort,
    bio: user.bio,
    github: user.github,
  };
}

module.exports = {
  createUser,
  findByEmail,
  findById,
  verifyPassword,
  createSession,
  getUserBySessionToken,
  destroySession,
  publicProfile,
};
