import { apiGet } from './api';

export function listMessages() {
  return apiGet('/api/message');
}

export function listMessagesByConversation(conversationId) {
  return apiGet(`/api/message/conversation/${encodeURIComponent(conversationId)}`);
}

export function getMessageById(messageId) {
  return apiGet(`/api/message/new/${encodeURIComponent(messageId)}`);
}
