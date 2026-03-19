import { apiDelete, apiGet, apiPost } from './api';

export function listConversations() {
  return apiGet('/api/conversations');
}

export function createConversation({ user_id, title }) {
  return apiPost('/api/conversations/create', {
    user_id: user_id ?? '',
    title: title ?? '',
  });
}

export function deleteConversation(conversationId) {
  return apiDelete(`/api/conversations/${encodeURIComponent(conversationId)}`);
}
