import { apiGet } from './api';

export function getAgentLogsByMessage(messageId) {
  return apiGet(`/api/agent_log/message/${encodeURIComponent(messageId)}`);
}

export function getAgentLogsByAgent(agentId) {
  return apiGet(`/api/agent_log/agent/${encodeURIComponent(agentId)}`);
}

export function getAgentLogById(logId) {
  return apiGet(`/api/agent_log/${encodeURIComponent(logId)}`);
}
