import { apiDelete, apiGet, apiPost, apiPut } from './api';

export function listSummarySessionsByUser(userId) {
  return apiGet(`/api/summary-sessions/user/${encodeURIComponent(userId)}`);
}

export function createSummarySession({ userId, content }) {
  return apiPost('/api/summary-sessions', { userId, content: content ?? '' });
}

export function updateSummarySession(sessionId, { content }) {
  return apiPut(`/api/summary-sessions/${encodeURIComponent(sessionId)}`, { content });
}

export function deleteSummarySession(sessionId) {
  return apiDelete(`/api/summary-sessions/${encodeURIComponent(sessionId)}`);
}

