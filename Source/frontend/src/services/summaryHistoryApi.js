import api from './api';

export async function createFromMas(payload) {
  return api.post('/api/summary-histories/create-from-mas', payload);
}

export async function getHistoriesBySession(sessionId) {
  const list = await api.get(`/api/summary-histories/session/${sessionId}`);
  return Array.isArray(list) ? list : [];
}
