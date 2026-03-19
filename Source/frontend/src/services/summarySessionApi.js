import api from './api';

export async function createSummarySession({ userId, content = '' }) {
  return api.post('/api/summary-sessions', { userId, content });
}

export async function getSessionsByUser(userId) {
  const list = await api.get(`/api/summary-sessions/user/${userId}`);
  return Array.isArray(list) ? list : [];
}

export async function getSummarySessionById(sessionId) {
  return api.get(`/api/summary-sessions/${sessionId}`);
}

export async function deleteSummarySession(sessionId) {
  return api.delete(`/api/summary-sessions/${sessionId}`);
}
