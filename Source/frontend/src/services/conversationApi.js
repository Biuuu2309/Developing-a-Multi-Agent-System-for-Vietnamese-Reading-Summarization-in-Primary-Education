import api from './api';

export async function createConversation({ userId, title = 'New chat', status = 'ACTIVE' }) {
  const payload = {
    user_id: userId,
    title,
    status,
    created_at: null,
    updated_at: null,
  };
  return api.post('/api/conversations/create', payload);
}

export async function getConversations() {
  return api.get('/api/conversations');
}

export async function getConversationById(conversationId) {
  return api.get(`/api/conversations/${conversationId}`);
}

export async function deleteConversation(conversationId) {
  return api.delete(`/api/conversations/${conversationId}`);
}

