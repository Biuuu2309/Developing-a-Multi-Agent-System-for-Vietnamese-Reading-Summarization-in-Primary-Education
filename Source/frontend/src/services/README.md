# Frontend Services Documentation

## Overview

This directory contains all API service layers for communicating with the Spring Boot backend.

## Files

### `api.js`
Base API configuration and HTTP request utilities.

**Features:**
- Base URL configuration (via `VITE_API_BASE_URL` env variable)
- Automatic auth token injection from localStorage
- Error handling with custom `APIError` class
- Methods: `apiGet`, `apiPost`, `apiPut`, `apiDelete`

**Usage:**
```javascript
import api from './api';

const data = await api.post('/api/endpoint', { key: 'value' });
```

### `errorHandler.js`
Error handling utilities and retry logic.

**Features:**
- `APIError` class for structured error handling
- `handleAPIError()` for user-friendly error messages
- `retryWithBackoff()` for automatic retry with exponential backoff

**Usage:**
```javascript
import { handleAPIError, retryWithBackoff } from './errorHandler';

try {
  const result = await retryWithBackoff(() => api.get('/api/data'), 3, 1000);
} catch (error) {
  const userError = handleAPIError(error);
  console.error(userError.message);
}
```

### `masApi.js`
MAS (Multi-Agent System) API service.

**Endpoints:**
- `POST /api/mas/chat` - Send chat message to MAS
- `POST /api/mas/sessions` - Create new session
- `GET /api/mas/sessions/user/{userId}` - Get all user sessions
- `GET /api/mas/sessions/{sessionId}` - Get session by ID
- `GET /api/mas/sessions/{sessionId}/history` - Get session history
- `GET /api/mas/sessions/{sessionId}/latest-state` - Get latest state

**Usage:**
```javascript
import { chatWithMAS, createMASSession } from './masApi';

// Chat with MAS
const response = await chatWithMAS({
  userId: 'user123',
  sessionId: 'session456',
  userInput: 'Tóm tắt diễn giải lớp 1: Văn bản cần tóm tắt...',
  conversationId: 'conv789'
});

// Create session
const session = await createMASSession({
  userId: 'user123',
  conversationId: 'conv789'
});
```

### `summaryService.js`
Summary-specific service for formatting requests and parsing responses.

**Features:**
- Format Normal mode form data into MAS request
- Format Chatbox mode messages
- Parse MAS responses for both modes
- Extract summary type, grade level, agent confidences

**Usage:**
```javascript
import { submitSummary, parseSummaryResponse } from './summaryService';

// Submit summary (Normal mode)
const response = await submitSummary({
  userId: 'user123',
  sessionId: 'session456',
  formData: {
    summaryType: 'abstractive',
    gradeLevel: '1',
    text: 'Văn bản cần tóm tắt...'
  }
});

// Parse response
const parsed = parseSummaryResponse(response);
console.log(parsed.summary, parsed.summaryType, parsed.gradeLevel);
```

### `sessionService.js`
Session management utilities.

**Features:**
- Get/create active session
- Load user sessions
- Manage active session in localStorage
- Get current user ID

**Usage:**
```javascript
import { getOrCreateSession, loadUserSessions, getCurrentUserId } from './sessionService';

// Get or create session
const sessionId = await getOrCreateSession('user123');

// Load all user sessions
const sessions = await loadUserSessions('user123');

// Get current user
const userId = getCurrentUserId();
```

## Environment Variables

Create a `.env` file in the frontend root:

```env
VITE_API_BASE_URL=http://localhost:8080
```

## Request/Response Formats

### MasChatRequest
```typescript
{
  sessionId?: string;
  userId: string;
  userInput: string;
  conversationId?: string;
}
```

### MasChatResponse
```typescript
{
  sessionId: string;
  stateId?: string;
  messageId: string;
  finalOutput: string;
  intent: string; // JSON string
  plan: string; // JSON string
  summary: string;
  evaluation: string; // JSON string
  clarificationNeeded: boolean;
  clarificationQuestion: string;
  agentConfidences: string; // JSON string
  status: string;
}
```

### MasSessionRequest
```typescript
{
  userId: string;
  conversationId?: string;
}
```

### MasSessionResponse
```typescript
{
  sessionId: string;
  userId: string;
  conversationId?: string;
  status: string;
  createdAt: string;
  updatedAt: string;
}
```

## Error Handling

All services throw `APIError` instances which can be caught and handled:

```javascript
import { handleAPIError } from './errorHandler';

try {
  const result = await chatWithMAS(request);
} catch (error) {
  const userError = handleAPIError(error);
  // Display userError.message to user
  // Check userError.status for HTTP status code
  // Access userError.data for additional error details
}
```

## Next Steps

After Phase 1, these services will be integrated into:
- `NormalMode.jsx` - For form submissions
- `ChatboxMode.jsx` - For chat messages
- `summary.jsx` - For session management
- `Sidebar.jsx` - For loading session history
