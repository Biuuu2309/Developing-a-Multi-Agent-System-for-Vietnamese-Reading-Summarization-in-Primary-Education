// Session management service

import { createMASSession, getMASSessions, getMASSession } from './masApi';

/**
 * Get current user ID from localStorage or context
 * @returns {string|null} User ID
 */
export function getCurrentUserId() {
  // TODO: Get from auth context or localStorage
  // Temporary hardcoded userId for testing
  const userId = localStorage.getItem('user_id');
  return userId || '34f8a78d-cd08-41fa-8835-a9b72c4f7c44'; // Temporary test userId
}

/**
 * Create or get existing session
 * @param {string} userId - User ID
 * @param {string} conversationId - Optional conversation ID
 * @returns {Promise<string>} Session ID
 */
export async function getOrCreateSession(userId, conversationId = null) {
  try {
    // Check if there's an active session in localStorage
    const activeSessionId = localStorage.getItem('active_session_id');
    if (activeSessionId) {
      // Verify session exists
      try {
        await getMASSession(activeSessionId, userId);
        return activeSessionId;
      } catch {
        // Session doesn't exist, create new one
        localStorage.removeItem('active_session_id');
      }
    }

    // Create new session
    const response = await createMASSession({ userId, conversationId });
    const sessionId = response.sessionId;
    
    // Store in localStorage
    localStorage.setItem('active_session_id', sessionId);
    
    return sessionId;
  } catch (error) {
    console.error('Get or create session error:', error);
    throw error;
  }
}

/**
 * Load sessions for current user
 * @param {string} userId - User ID
 * @returns {Promise<Array>} Array of sessions
 */
export async function loadUserSessions(userId) {
  try {
    const sessions = await getMASSessions(userId);
    
    // Transform to frontend format
    return sessions.map((session) => ({
      id: session.sessionId,
      sessionId: session.sessionId,
      userId: session.userId,
      conversationId: session.conversationId,
      status: session.status,
      createdAt: session.createdAt,
      updatedAt: session.updatedAt,
    }));
  } catch (error) {
    console.error('Load user sessions error:', error);
    return [];
  }
}

/**
 * Clear active session
 */
export function clearActiveSession() {
  localStorage.removeItem('active_session_id');
}

/**
 * Set active session
 */
export function setActiveSession(sessionId) {
  localStorage.setItem('active_session_id', sessionId);
}

/**
 * Get active session ID
 */
export function getActiveSessionId() {
  return localStorage.getItem('active_session_id');
}

export default {
  getCurrentUserId,
  getOrCreateSession,
  loadUserSessions,
  clearActiveSession,
  setActiveSession,
  getActiveSessionId,
};
