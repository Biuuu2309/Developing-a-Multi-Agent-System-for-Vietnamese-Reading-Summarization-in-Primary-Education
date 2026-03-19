import { apiDelete, apiGet, apiPost } from './api';

export function listAgents() {
  return apiGet('/api/agent');
}

export function createAgent(payload) {
  return apiPost('/api/agent', payload);
}

export function deleteAgent(agentId) {
  return apiDelete(`/api/agent/${encodeURIComponent(agentId)}`);
}
