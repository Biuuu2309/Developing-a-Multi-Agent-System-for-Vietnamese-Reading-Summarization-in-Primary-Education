// MAS (Multi-Agent System) API service

import api from './api';

/**
 * Send chat message to MAS
 * @param {Object} request - MasChatRequest
 * @param {string} request.sessionId - Optional session ID
 * @param {string} request.userId - User ID
 * @param {string} request.userInput - User input text
 * @param {string} request.conversationId - Optional conversation ID
 * @returns {Promise<Object>} MasChatResponse
 */
export async function chatWithMAS(request) {
  try {
    const response = await api.post('/api/mas/chat', request);
    return response;
  } catch (error) {
    console.error('MAS chat error:', error);
    throw error;
  }
}

/**
 * Create new MAS session
 * @param {Object} request - MasSessionRequest
 * @param {string} request.userId - User ID
 * @param {string} request.conversationId - Optional conversation ID
 * @returns {Promise<Object>} MasSessionResponse
 */
export async function createMASSession(request) {
  try {
    const response = await api.post('/api/mas/sessions', request);
    return response;
  } catch (error) {
    console.error('Create session error:', error);
    throw error;
  }
}

/**
 * Get all sessions for a user
 * @param {string} userId - User ID
 * @returns {Promise<Array>} Array of MasSessionResponse
 */
export async function getMASSessions(userId) {
  try {
    const response = await api.get(`/api/mas/sessions/user/${userId}`);
    return response;
  } catch (error) {
    console.error('Get sessions error:', error);
    throw error;
  }
}

/**
 * Get session by ID
 * @param {string} sessionId - Session ID
 * @param {string} userId - User ID
 * @returns {Promise<Object>} MasSessionResponse
 */
export async function getMASSession(sessionId, userId) {
  try {
    const response = await api.get(`/api/mas/sessions/${sessionId}?userId=${userId}`);
    return response;
  } catch (error) {
    console.error('Get session error:', error);
    throw error;
  }
}

/**
 * Get session history (states)
 * @param {string} sessionId - Session ID
 * @param {string} userId - User ID
 * @returns {Promise<Array>} Array of MasStateResponse
 */
export async function getSessionHistory(sessionId, userId) {
  try {
    const response = await api.get(`/api/mas/sessions/${sessionId}/history?userId=${userId}`);
    return response;
  } catch (error) {
    console.error('Get session history error:', error);
    throw error;
  }
}

/**
 * Get latest state for a session
 * @param {string} sessionId - Session ID
 * @param {string} userId - User ID
 * @returns {Promise<Object>} MasStateResponse
 */
export async function getLatestState(sessionId, userId) {
  try {
    const response = await api.get(`/api/mas/sessions/${sessionId}/latest-state?userId=${userId}`);
    return response;
  } catch (error) {
    console.error('Get latest state error:', error);
    throw error;
  }
}

export default {
  chatWithMAS,
  createMASSession,
  getMASSessions,
  getMASSession,
  getSessionHistory,
  getLatestState,
};
