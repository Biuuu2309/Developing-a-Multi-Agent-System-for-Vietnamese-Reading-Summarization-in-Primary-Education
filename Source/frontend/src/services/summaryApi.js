import { apiGet } from './api';

export async function getAllSummaries() {
  return apiGet('/api/summaries');
}

export async function getTop10Summaries() {
  return apiGet('/api/summaries/top10');
}

export async function searchSummaries({ searchTerm, grade }) {
  const params = new URLSearchParams();
  params.set('searchTerm', searchTerm ?? '');
  if (grade) params.set('grade', grade);
  return apiGet(`/api/summaries/search?${params.toString()}`);
}

export async function getSummariesByStatus(status) {
  return apiGet(`/api/summaries/status/${encodeURIComponent(status)}`);
}

export async function getSummariesByContributor(userId) {
  return apiGet(`/api/summaries/contributor/${encodeURIComponent(userId)}`);
}

export async function getSummariesByGrade(grade) {
  return apiGet(`/api/summaries/grade/${encodeURIComponent(grade)}`);
}

export async function getSummariesByMethod(method) {
  return apiGet(`/api/summaries/method/${encodeURIComponent(method)}`);
}

