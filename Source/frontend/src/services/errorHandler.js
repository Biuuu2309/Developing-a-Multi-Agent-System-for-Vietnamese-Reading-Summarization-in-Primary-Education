// Error handling utilities

/**
 * Custom error class for API errors
 */
export class APIError extends Error {
  constructor(message, status, data = null) {
    super(message);
    this.name = 'APIError';
    this.status = status;
    this.data = data;
  }
}

/**
 * Handle API errors and provide user-friendly messages
 */
export function handleAPIError(error) {
  if (error instanceof APIError) {
    return {
      message: error.message,
      status: error.status,
      data: error.data,
    };
  }

  if (error instanceof TypeError && error.message.includes('fetch')) {
    return {
      message: 'Không thể kết nối đến server. Vui lòng kiểm tra kết nối mạng.',
      status: 0,
      data: null,
    };
  }

  return {
    message: error.message || 'Đã xảy ra lỗi không xác định',
    status: null,
    data: null,
  };
}

/**
 * Retry function with exponential backoff
 */
export async function retryWithBackoff(fn, maxRetries = 3, delay = 1000) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      
      // Exponential backoff: delay * 2^i
      const waitTime = delay * Math.pow(2, i);
      await new Promise((resolve) => setTimeout(resolve, waitTime));
    }
  }
}

export default {
  APIError,
  handleAPIError,
  retryWithBackoff,
};
