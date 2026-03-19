import { apiDelete, apiGet, apiPut } from './api';

export function listSummaryHistoriesBySession(sessionId) {
  return apiGet(`/api/summary-histories/session/${encodeURIComponent(sessionId)}`);
}

export function listSummaryHistoriesByUser(userId) {
  return apiGet(`/api/summary-histories/user/${encodeURIComponent(userId)}`);
}

export function getSummaryHistoryById(historyId) {
  return apiGet(`/api/summary-histories/${encodeURIComponent(historyId)}`);
}

export function updateSummaryHistory(historyId, { method, summaryContent, isAccepted }) {
  const payload = {};
  if (method !== undefined) payload.method = method;
  if (summaryContent !== undefined) payload.summaryContent = summaryContent;
  if (isAccepted !== undefined) payload.isAccepted = isAccepted;
  return apiPut(`/api/summary-histories/${encodeURIComponent(historyId)}`, payload);
}

export function deleteSummaryHistory(historyId) {
  return apiDelete(`/api/summary-histories/${encodeURIComponent(historyId)}`);
}

