import { apiGet, apiPost, apiPut } from './api';

export function listMasSessionsByUser(userId) {
  return apiGet(`/api/mas/sessions/user/${encodeURIComponent(userId)}`);
}

export function createMasSession({ userId, conversationId }) {
  return apiPost('/api/mas/sessions', {
    userId,
    conversationId: conversationId || null,
  });
}

export function updateMasSessionStatus(sessionId, status) {
  return apiPut(`/api/mas/sessions/${encodeURIComponent(sessionId)}/status?status=${encodeURIComponent(status)}`, {});
}
