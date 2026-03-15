import { useState, useRef, useEffect } from 'react';
import { Send, User, Bot } from 'lucide-react';
import './SummaryModes.css';

export default function ChatboxMode({ onSubmit }) {
  const [messages, setMessages] = useState([
    {
      id: 1,
      role: 'assistant',
      content: 'Xin chào! Tôi có thể giúp bạn tóm tắt văn bản. Hãy cho tôi biết bạn muốn tóm tắt theo cách nào (diễn giải hay trích xuất) và cấp lớp của bạn.',
    },
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = {
      id: messages.length + 1,
      role: 'user',
      content: input.trim(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    // Simulate API call
    setTimeout(() => {
      const assistantMessage = {
        id: messages.length + 2,
        role: 'assistant',
        content: 'Tôi đã nhận được yêu cầu của bạn. Đang xử lý...',
      };
      setMessages((prev) => [...prev, assistantMessage]);
      setIsLoading(false);

      if (onSubmit) {
        onSubmit({
          message: userMessage.content,
          messages: [...messages, userMessage, assistantMessage],
        });
      }
    }, 1000);
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
              <div className="chatbox-message-text">{message.content}</div>
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
