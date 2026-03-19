import { useState, useRef, useEffect } from 'react';
import { Send, User, Bot, AlertCircle } from 'lucide-react';
import { chatWithMAS } from '../../../services/masApi';
import { createConversation } from '../../../services/conversationApi';
import { createMASSession } from '../../../services/masApi';
import { parseChatResponse } from '../../../services/summaryService';
import { createFromMas } from '../../../services/summaryHistoryApi';
import { getCurrentUserId } from '../../../services/sessionService';
import { createSummarySession } from '../../../services/summarySessionApi';
import { handleAPIError } from '../../../services/errorHandler';
import SummaryResult from './SummaryResult';
import './SummaryModes.css';

const WELCOME_MESSAGE = {
  id: 1,
  role: 'assistant',
  content: 'Xin chào! Tôi có thể giúp bạn tóm tắt văn bản. Hãy cho tôi biết bạn muốn tóm tắt theo cách nào (diễn giải hay trích xuất) và cấp lớp của bạn.',
};

export default function ChatboxMode({ summarySessionId, onSubmit, initialData }) {
  const [messages, setMessages] = useState([WELCOME_MESSAGE]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [conversationId, setConversationId] = useState(null);
  const [masSessionId, setMasSessionId] = useState(null);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    if (initialData?.conversationId) setConversationId(initialData.conversationId);
    if (initialData?.masSessionId) setMasSessionId(initialData.masSessionId);
    if (initialData?.messages?.length) setMessages(initialData.messages);
  }, [initialData]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userContent = input.trim();
    const userMessage = { id: Date.now(), role: 'user', content: userContent };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setError(null);
    setIsLoading(true);

    const userId = getCurrentUserId();
    let currentSummarySessionId = summarySessionId;
    let currentConvId = conversationId;
    let currentMasId = masSessionId;

    try {
      if (!currentSummarySessionId) {
        const created = await createSummarySession({ userId, content: '' });
        currentSummarySessionId = created.sessionId;
        if (onSubmit) {
          onSubmit({
            kind: 'session_created',
            summarySessionId: currentSummarySessionId,
            source: 'chatbox_send',
          });
        }
      }

      if (!currentConvId) {
        const conv = await createConversation({ userId, title: 'New chat', status: 'ACTIVE' });
        currentConvId = conv.conversation_id;
        setConversationId(currentConvId);
        const mas = await createMASSession({ userId, conversationId: currentConvId });
        currentMasId = mas.sessionId;
        setMasSessionId(currentMasId);
      }

      const response = await chatWithMAS({
        userId,
        sessionId: currentMasId,
        conversationId: currentConvId,
        userInput: userContent,
      });

      const parsed = parseChatResponse(response);
      const hasResultBlock = parsed.summary || parsed.summaryImageUrl;
      const assistantMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: hasResultBlock ? '' : (parsed.content || parsed.summary || 'Đã xử lý.'),
        result: hasResultBlock ? parsed : null,
      };
      const nextMessages = [...messages, userMessage, assistantMessage];
      setMessages(nextMessages);

      const summaryContent = parsed.summary || parsed.content || '';
      const summaryImageUrl = typeof parsed.summaryImageUrl === 'string' ? parsed.summaryImageUrl : (parsed.summaryImageUrl ? JSON.stringify(parsed.summaryImageUrl) : null);
      const evaluation = typeof parsed.evaluation === 'string' ? parsed.evaluation : (parsed.evaluation ? JSON.stringify(parsed.evaluation) : null);

      await createFromMas({
        summarySessionId: currentSummarySessionId,
        userInput: userContent,
        summaryContent,
        summaryImageUrl,
        evaluation,
        masSessionId: currentMasId,
        conversationId: currentConvId,
      });

      if (onSubmit) {
        onSubmit({
          kind: 'message',
          message: userContent,
          messages: nextMessages,
          summarySessionId: currentSummarySessionId,
          conversationId: currentConvId,
          masSessionId: currentMasId,
          result: parsed,
        });
      }
    } catch (err) {
      const userError = handleAPIError(err);
      setError(userError.message);
      setMessages((prev) => [...prev, { id: Date.now() + 1, role: 'assistant', content: userError.message }]);
      if (onSubmit) {
        onSubmit({
          kind: 'error',
          message: userContent,
          messages: [...messages, userMessage, { id: Date.now() + 1, role: 'assistant', content: userError.message }],
          conversationId: currentConvId || null,
          masSessionId: currentMasId || null,
        });
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="chatbox-mode-container">
      <div className="chatbox-messages">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`chatbox-message ${message.role === 'user' ? 'user-message' : 'assistant-message'}`}
          >
            <div className="chatbox-message-avatar">
              {message.role === 'user' ? (
                <User size={20} />
              ) : (
                <Bot size={20} />
              )}
            </div>
            <div className="chatbox-message-content">
              {message.content && (
                <div className="chatbox-message-text">{message.content}</div>
              )}
              {message.result && (message.result.summary || message.result.summaryImageUrl) && (
                <SummaryResult result={message.result} embedded />
              )}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="chatbox-message assistant-message">
            <div className="chatbox-message-avatar">
              <Bot size={20} />
            </div>
            <div className="chatbox-message-content">
              <div className="chatbox-typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {error && (
        <div className="error-message" style={{ marginBottom: '8px' }}>
          <AlertCircle size={18} />
          <span>{error}</span>
        </div>
      )}

      <form onSubmit={handleSubmit} className="chatbox-input-form">
        <div className="chatbox-input-container">
          <textarea
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSubmit(e);
              }
            }}
            placeholder="Nhập tin nhắn của bạn..."
            rows={1}
            className="chatbox-input"
            disabled={isLoading}
          />
          <button
            type="submit"
            className="chatbox-send-btn"
            disabled={!input.trim() || isLoading}
          >
            <Send size={18} />
          </button>
        </div>
      </form>
    </div>
  );
}
