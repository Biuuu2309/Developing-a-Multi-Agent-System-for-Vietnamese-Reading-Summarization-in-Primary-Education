import { Plus, MessageSquare, Trash2, Clock, PanelLeftClose, PanelLeftOpen } from 'lucide-react';
import './Sidebar.css';

function formatDate(date) {
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
}

function getSessionTitle(session) {
  const text = session.content ? String(session.content).trim() : 'Phiên mới';
  return text.slice(0, 40) + (text.length > 40 ? '...' : '') || 'Phiên mới';
}

export default function Sidebar({
  sessions = [],
  selectedSessionId, // MAS sessionId
  onSelectSession,
  onDeleteSession,
  onNewSession,
  onCollapse,
  collapsed = false,
  isOpen = true,
  onClose,
}) {
  const sortedSessions = [...sessions].sort(
    (a, b) => new Date(b.timestamp || 0).getTime() - new Date(a.timestamp || 0).getTime()
  );

  const handleDelete = (e, sessionId) => {
    e.stopPropagation();
    onDeleteSession?.(sessionId);
  };

  return (
    <>
      {isOpen && <div className="sidebar-overlay" onClick={onClose} aria-hidden="true" />}
      <aside className={`sidebar sidebar-left ${isOpen ? 'sidebar-visible' : ''} ${collapsed ? 'sidebar-collapsed' : ''}`}>
        <div className="sidebar-header">
          <button type="button" className="sidebar-new-session" onClick={onNewSession} title="Phiên mới">
            <Plus size={20} />
            {!collapsed && <span>Phiên mới</span>}
          </button>
          {!collapsed && <h2 className="sidebar-title">Phiên tóm tắt</h2>}
          <div className="sidebar-header-actions">
            {onCollapse && (
              <button type="button" className="sidebar-icon-btn" onClick={onCollapse} title={collapsed ? 'Mở rộng' : 'Thu gọn'}>
                {collapsed ? <PanelLeftOpen size={20} /> : <PanelLeftClose size={20} />}
              </button>
            )}
            {onClose && (
              <button type="button" className="sidebar-close-btn" onClick={onClose} title="Đóng">
                <PanelLeftClose size={20} />
              </button>
            )}
          </div>
        </div>

        <div className="sidebar-content">
          {sortedSessions.length === 0 ? (
            <div className="sidebar-empty">
              <MessageSquare size={40} />
              <p>Chưa có phiên nào</p>
              <span>Tạo phiên mới để bắt đầu tóm tắt</span>
              {!collapsed && (
                <button type="button" className="sidebar-empty-btn" onClick={onNewSession}>
                  <Plus size={16} />
                  Phiên mới
                </button>
              )}
            </div>
          ) : (
            <ul className="sidebar-sessions">
              {sortedSessions.map((session) => (
                <li
                  key={session.sessionId}
                  className={`sidebar-session-item ${selectedSessionId === session.sessionId ? 'active' : ''}`}
                  onClick={() => onSelectSession?.(session)}
                >
                  <div className="session-icon">
                    <MessageSquare size={18} />
                  </div>
                  {!collapsed && (
                    <>
                      <div className="session-body">
                        <div className="session-title">{getSessionTitle(session)}</div>
                        <div className="session-meta">
                          <Clock size={12} />
                          <span>{formatDate(session.timestamp)}</span>
                        </div>
                      </div>
                      <button
                        type="button"
                        className="session-delete-btn"
                        onClick={(e) => handleDelete(e, session.sessionId)}
                        title="Xóa phiên"
                      >
                        <Trash2 size={14} />
                      </button>
                    </>
                  )}
                </li>
              ))}
            </ul>
          )}
        </div>
      </aside>
    </>
  );
}
