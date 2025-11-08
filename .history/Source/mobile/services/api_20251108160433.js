import axios from 'axios';
import { API_CONFIG } from '@/config/api';

const api = axios.create({
  baseURL: API_CONFIG.BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: API_CONFIG.TIMEOUT,
});

export const messageService = {
  createMessage: async (conversationId, userId, content, agentId = null, role = 'USER') => {
    try {
      const response = await api.post('/message/create', {
        conversationId,
        userId,
        content,
        agentId,
        role,
        metadata: null,
      });
      return response.data;
    } catch (error) {
      console.error('Error creating message:', error);
      throw error;
    }
  },

  getMessagesByConversation: async (conversationId) => {
    try {
      const response = await api.get(`/message/conversation/${conversationId}`);
      return response.data;
    } catch (error) {
      console.error('Error getting messages:', error);
      throw error;
    }
  },

  createConversation: async (userId, title = 'New Conversation') => {
    try {
      const response = await api.post('/conversations/create', {
        user_id: userId,
        title,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      });
      return response.data;
    } catch (error) {
      console.error('Error creating conversation:', error);
      throw error;
    }
  },
};

export default api;

