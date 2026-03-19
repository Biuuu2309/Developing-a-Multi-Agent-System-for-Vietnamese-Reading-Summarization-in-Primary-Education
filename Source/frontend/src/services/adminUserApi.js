import { apiDelete, apiGet, apiPost, apiPut } from './api';

export function listUsers() {
  return apiGet('/api/users');
}

export function createUser(payload) {
  return apiPost('/api/users', payload);
}

export function updateUserProfile(userId, payload) {
  return apiPut(`/api/users/${encodeURIComponent(userId)}/profile`, payload);
}

export function deleteUser(userId) {
  return apiDelete(`/api/users/${encodeURIComponent(userId)}`);
}
