import { apiDelete, apiGet, apiPatch } from './api';

export async function listSummaries() {
  return apiGet('/api/summaries');
}

export async function deleteSummary(summaryId) {
  return apiDelete(`/api/summaries/${encodeURIComponent(summaryId)}`);
}

// patchSummary uses PATCH /api/summaries/{id}
export async function updateSummaryTitleAndStatus(summaryId, { title, status }) {
  const payload = {};
  if (title !== undefined) payload.title = title;
  if (status !== undefined) payload.status = status;
  return apiPatch(`/api/summaries/${encodeURIComponent(summaryId)}`, payload);
}

