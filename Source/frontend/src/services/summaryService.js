// Summary service - Format requests and handle summary-specific logic

import { chatWithMAS, createMASSession } from './masApi';

/**
 * Format user input for Normal mode
 * @param {Object} data - Form data
 * @param {string} data.summaryType - 'abstractive' or 'extractive'
 * @param {string} data.gradeLevel - Grade level (1-5) for abstractive
 * @param {string} data.text - Text to summarize
 * @returns {string} Formatted user input
 */
function formatNormalModeInput(data) {
  const { summaryType, gradeLevel, text } = data;
  
  let prompt = '';
  
  if (summaryType === 'abstractive') {
    prompt = 'Tóm tắt diễn giải';
    if (gradeLevel) {
      prompt += ` lớp ${gradeLevel}`;
    }
  } else if (summaryType === 'extractive') {
    prompt = 'Tóm tắt trích xuất';
  }
  
  return `${prompt}: ${text}`;
}

/**
 * Submit summary request (Normal mode)
 * @param {Object} params
 * @param {string} params.userId - User ID
 * @param {string} params.sessionId - Optional session ID
 * @param {string} params.conversationId - Optional conversation ID
 * @param {Object} params.formData - Form data (summaryType, gradeLevel, text)
 * @returns {Promise<Object>} MAS response
 */
export async function submitSummary({ userId, sessionId, conversationId, formData }) {
  try {
    const userInput = formatNormalModeInput(formData);
    
    const request = {
      userId,
      sessionId: sessionId || null,
      conversationId: conversationId || null,
      userInput,
    };

    const response = await chatWithMAS(request);
    return response;
  } catch (error) {
    console.error('Submit summary error:', error);
    throw error;
  }
}

/**
 * Submit chat message (Chatbox mode)
 * @param {Object} params
 * @param {string} params.userId - User ID
 * @param {string} params.sessionId - Session ID (required for chatbox)
 * @param {string} params.conversationId - Optional conversation ID
 * @param {string} params.message - User message
 * @returns {Promise<Object>} MAS response
 */
export async function submitChatMessage({ userId, sessionId, conversationId, message }) {
  try {
    if (!sessionId) {
      // Create new session if not exists
      const sessionResponse = await createMASSession({ userId, conversationId });
      sessionId = sessionResponse.sessionId;
    }

    const request = {
      userId,
      sessionId,
      conversationId: conversationId || null,
      userInput: message,
    };

    const response = await chatWithMAS(request);
    return {
      ...response,
      sessionId, // Ensure sessionId is returned
    };
  } catch (error) {
    console.error('Submit chat message error:', error);
    throw error;
  }
}

/**
 * Parse MAS response for Normal mode
 * @param {Object} response - MasChatResponse
 * @returns {Object} Parsed summary data
 */
export function parseSummaryResponse(response) {
  try {
    const summary = response.summary || response.finalOutput || '';
    
    // Parse intent to get summaryType and gradeLevel
    let summaryType = 'abstractive';
    let gradeLevel = null;
    
    if (response.intent) {
      try {
        const intent = typeof response.intent === 'string' 
          ? JSON.parse(response.intent) 
          : response.intent;
        
        summaryType = intent.summarization_type || 'abstractive';
        gradeLevel = intent.grade_level || null;
      } catch (e) {
        console.warn('Failed to parse intent:', e);
      }
    }

    // Parse agent confidences
    let agentConfidences = {};
    if (response.agentConfidences) {
      try {
        agentConfidences = typeof response.agentConfidences === 'string'
          ? JSON.parse(response.agentConfidences)
          : response.agentConfidences;
      } catch (e) {
        console.warn('Failed to parse agent confidences:', e);
      }
    }

    return {
      summary,
      summaryType,
      gradeLevel,
      agentConfidences,
      evaluation: response.evaluation,
      status: response.status,
      sessionId: response.sessionId,
      messageId: response.messageId,
      summaryId: response.summaryId,
      imageUrl: response.imageUrl,
      summaryImageUrl: response.summaryImageUrl,
    };
  } catch (error) {
    console.error('Parse summary response error:', error);
    return {
      summary: response.finalOutput || '',
      summaryType: 'abstractive',
      gradeLevel: null,
      agentConfidences: {},
      status: response.status || 'FAILED',
    };
  }
}

/**
 * Parse MAS response for Chatbox mode
 * @param {Object} response - MasChatResponse
 * @returns {Object} Parsed chat data
 */
export function parseChatResponse(response) {
  try {
    const content = response.finalOutput || '';
    const clarificationNeeded = response.clarificationNeeded || false;
    const clarificationQuestion = response.clarificationQuestion || '';

    // Parse agent confidences
    let agentConfidences = {};
    if (response.agentConfidences) {
      try {
        agentConfidences = typeof response.agentConfidences === 'string'
          ? JSON.parse(response.agentConfidences)
          : response.agentConfidences;
      } catch (e) {
        console.warn('Failed to parse agent confidences:', e);
      }
    }

    return {
      content,
      clarificationNeeded,
      clarificationQuestion,
      agentConfidences,
      summary: response.summary,
      status: response.status,
      sessionId: response.sessionId,
      messageId: response.messageId,
    };
  } catch (error) {
    console.error('Parse chat response error:', error);
    return {
      content: response.finalOutput || 'Lỗi khi xử lý',
      clarificationNeeded: false,
      clarificationQuestion: '',
      agentConfidences: {},
      status: response.status || 'FAILED',
    };
  }
}

export default {
  submitSummary,
  submitChatMessage,
  parseSummaryResponse,
  parseChatResponse,
  formatNormalModeInput,
};
