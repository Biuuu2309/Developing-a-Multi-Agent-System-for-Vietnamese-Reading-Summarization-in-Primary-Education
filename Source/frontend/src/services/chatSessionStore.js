const SESSIONS_KEY = 'chat_sessions';
const MESSAGES_PREFIX = 'chat_session_messages:';

export function loadChatSessions() {
  try {
    const raw = localStorage.getItem(SESSIONS_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

export function saveChatSessions(sessions) {
  localStorage.setItem(SESSIONS_KEY, JSON.stringify(sessions));
}

export function upsertChatSession(session) {
  const sessions = loadChatSessions();
  const idx = sessions.findIndex((s) => s.sessionId === session.sessionId);
  const next = idx >= 0 ? sessions.map((s, i) => (i === idx ? { ...s, ...session } : s)) : [session, ...sessions];
  saveChatSessions(next);
  return next;
}

export function setActiveChatSessionId(sessionId) {
  localStorage.setItem('active_chat_session_id', sessionId);
}

export function getActiveChatSessionId() {
  return localStorage.getItem('active_chat_session_id');
}

export function loadChatMessages(sessionId) {
  try {
    const raw = localStorage.getItem(`${MESSAGES_PREFIX}${sessionId}`);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

export function saveChatMessages(sessionId, messages) {
  localStorage.setItem(`${MESSAGES_PREFIX}${sessionId}`, JSON.stringify(messages));
}

export function renameChatSessionTitle(sessionId, title) {
  const sessions = loadChatSessions();
  const next = sessions.map((s) => (s.sessionId === sessionId ? { ...s, title } : s));
  saveChatSessions(next);
  return next;
}

