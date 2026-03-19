import { apiGet, apiPost } from './api';

export function listReadHistoryByUser(userId) {
  return apiGet(`/api/read-history/user/${encodeURIComponent(userId)}`);
}

export function logReadHistory(userId, summaryId) {
  const q = new URLSearchParams({ userId, summaryId }).toString();
  return apiPost(`/api/read-history/log?${q}`, {});
}
