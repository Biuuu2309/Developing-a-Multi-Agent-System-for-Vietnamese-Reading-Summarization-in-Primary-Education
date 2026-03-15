import { useState, useEffect } from 'react';
import { X, History, Clock, FileText, Trash2, MessageSquare } from 'lucide-react';
import './Sidebar.css';

export default function Sidebar({ isOpen, onClose, sessions, onSelectSession, onDeleteSession }) {
  const [localSessions, setLocalSessions] = useState([]);

  useEffect(() => {
    // Load sessions from localStorage
    const savedSessions = localStorage.getItem('summary_sessions');
    if (savedSessions) {
      try {
        const parsed = JSON.parse(savedSessions);
        setLocalSessions(parsed);
      } catch (e) {
        console.error('Failed to parse sessions:', e);
      }
    }
  }, [sessions]);

  // Merge prop sessions with local sessions
  const allSessions = [...localSessions, ...(sessions || [])].sort((a, b) => {
    return new Date(b.timestamp || b.createdAt) - new Date(a.timestamp || a.createdAt);
  });

  const formatDate = (date) => {
    if (!date) return 'Không xác định';
    const d = new Date(date);
    const now = new Date();
    const diff = now - d;
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (minutes < 1) return 'Vừa xong';
    if (minutes < 60) return `${minutes} phút trước`;
    if (hours < 24) return `${hours} giờ trước`;
    if (days < 7) return `${days} ngày trước`;
    return d.toLocaleDateString('vi-VN');
  };

  const getSummaryTypeLabel = (type) => {
    return type === 'abstractive' ? 'Diễn giải' : type === 'extractive' ? 'Trích xuất' : 'Chatbox';
  };

  const handleDelete = (e, sessionId) => {
    e.stopPropagation();
    if (onDeleteSession) {
      onDeleteSession(sessionId);
    } else {
      // Delete from localStorage
      const updated = localSessions.filter((s) => s.id !== sessionId);
      setLocalSessions(updated);
      localStorage.setItem('summary_sessions', JSON.stringify(updated));
    }
  };

  return (
    <>
      {/* Overlay */}
      {isOpen && <div className="sidebar-overlay" onClick={onClose} />}

      {/* Sidebar */}
      <div className={`sidebar ${isOpen ? 'sidebar-open' : ''}`}>
        <div className="sidebar-header">
          <div className="sidebar-header-content">
            <History size={20} />
            <h2>Lịch sử</h2>
          </div>
          <button className="sidebar-close-btn" onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        <div className="sidebar-content">
          {allSessions.length === 0 ? (
            <div className="sidebar-empty">
              <History size={48} />
              <p>Chưa có lịch sử</p>
              <span>Các phiên làm việc của bạn sẽ hiển thị ở đây</span>
            </div>
          ) : (
            <div className="sidebar-sessions">
              {allSessions.map((session) => (
                <div
                  key={session.id}
                  className="sidebar-session-item"
                  onClick={() => onSelectSession && onSelectSession(session)}
                >
                  <div className="session-header">
                    <div className="session-type">
                      {session.mode === 'chatbox' ? (
                        <MessageSquare size={16} />
                      ) : (
                        <FileText size={16} />
                      )}
                      <span>{getSummaryTypeLabel(session.summaryType || session.mode)}</span>
                    </div>
                    <button
                      className="session-delete-btn"
                      onClick={(e) => handleDelete(e, session.id)}
                      title="Xóa"
                    >
                      <Trash2 size={14} />
                    </button>
                  </div>

                  <div className="session-preview">
                    {session.mode === 'chatbox' ? (
                      <div className="session-chat-preview">
                        {session.messages && session.messages.length > 0 ? (
                          <div className="chat-preview-text">
                            {session.messages[session.messages.length - 1]?.content?.substring(0, 100)}
                            {session.messages[session.messages.length - 1]?.content?.length > 100 && '...'}
                          </div>
                        ) : (
                          <div className="chat-preview-text">{session.text?.substring(0, 100)}...</div>
                        )}
                      </div>
                    ) : (
                      <div className="session-text-preview">
                        {session.text?.substring(0, 150)}
                        {session.text?.length > 150 && '...'}
                      </div>
                    )}
                  </div>

                  <div className="session-footer">
                    <div className="session-meta">
                      <Clock size={12} />
                      <span>{formatDate(session.timestamp || session.createdAt)}</span>
                    </div>
                    {session.gradeLevel && (
                      <div className="session-grade">Lớp {session.gradeLevel}</div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </>
  );
}
