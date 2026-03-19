import { apiGet } from './api';

export function listMasStatesBySession(sessionId, userId) {
  return apiGet(
    `/api/mas/sessions/${encodeURIComponent(sessionId)}/history?userId=${encodeURIComponent(userId)}`,
  );
}

export function getLatestMasState(sessionId, userId) {
  return apiGet(
    `/api/mas/sessions/${encodeURIComponent(sessionId)}/latest-state?userId=${encodeURIComponent(userId)}`,
  );
}
