/**
 * Error handling utilities for MAS Flow
 */

export class MASFlowError extends Error {
  constructor(message, code, details = {}) {
    super(message);
    this.name = 'MASFlowError';
    this.code = code;
    this.details = details;
  }
}

/**
 * Validate MAS response structure
 */
export function validateMASResponse(response) {
  if (!response) {
    return { valid: false, error: 'No response provided' };
  }

  // Check if response has required structure
  if (typeof response !== 'object') {
    return { valid: false, error: 'Invalid response format' };
  }

  // Check agent_confidences if present
  if (response.agent_confidences) {
    try {
      const confidences =
        typeof response.agent_confidences === 'string'
          ? JSON.parse(response.agent_confidences)
          : response.agent_confidences;

      if (typeof confidences !== 'object' || confidences === null) {
        return {
          valid: false,
          error: 'Invalid agent_confidences format',
        };
      }
    } catch (e) {
      return {
        valid: false,
        error: 'Failed to parse agent_confidences',
        details: e.message,
      };
    }
  }

  return { valid: true };
}

/**
 * Safe parse JSON with error handling
 */
export function safeParseJSON(jsonString, fallback = null) {
  try {
    return JSON.parse(jsonString);
  } catch (e) {
    console.warn('Failed to parse JSON:', e);
    return fallback;
  }
}

/**
 * Get error message for display
 */
export function getErrorMessage(error) {
  if (error instanceof MASFlowError) {
    return error.message;
  }
  if (error instanceof Error) {
    return error.message;
  }
  return 'An unknown error occurred';
}
