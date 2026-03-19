import { useCallback, useEffect, useState } from 'react';
import { handleAPIError } from '../../services/errorHandler';
import { getMessageById, listMessages, listMessagesByConversation } from '../../services/adminMessageApi';

function formatDate(v) {
  if (!v) return '—';
  if (Array.isArray(v)) {
    const [y, m, d, h = 0, mm = 0, s = 0] = v;
    return `${y}-${String(m).padStart(2, '0')}-${String(d).padStart(2, '0')} ${String(h).padStart(2, '0')}:${String(mm).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
  }
  return String(v);
}

function shortText(v, n = 64) {
  if (!v) return '—';
  const s = String(v);
  return s.length > n ? `${s.slice(0, n)}...` : s;
}

export default function AdminMessages() {
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [conversationId, setConversationId] = useState('');
  const [messageId, setMessageId] = useState('');

  const loadAll = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const data = await listMessages();
      setRows(Array.isArray(data) ? data : []);
    } catch (e) {
      setRows([]);
      setError(handleAPIError(e).message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadAll();
  }, [loadAll]);

  const handleLoadByConversation = async () => {
    if (!conversationId.trim()) {
      setError('Vui long nhap conversationId');
      return;
    }
    setLoading(true);
    setError('');
    try {
      const data = await listMessagesByConversation(conversationId.trim());
      setRows(Array.isArray(data) ? data : []);
    } catch (e) {
      setRows([]);
      setError(handleAPIError(e).message);
    } finally {
      setLoading(false);
    }
  };

  const handleLoadByMessageId = async () => {
    if (!messageId.trim()) {
      setError('Vui long nhap messageId');
      return;
    }
    setLoading(true);
    setError('');
    try {
      const data = await getMessageById(messageId.trim());
      setRows(data ? [data] : []);
    } catch (e) {
      setRows([]);
      setError(handleAPIError(e).message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="admin-panel">
      <p className="admin-muted" style={{ marginBottom: 12 }}>
        Read-only de tranh kich hoat luong MAS khi tao message.
      </p>

      <div className="admin-toolbar" style={{ marginBottom: 12 }}>
        <button type="button" className="admin-btn admin-btn-primary" onClick={loadAll} disabled={loading}>
          Load all
        </button>
      </div>

      <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: 8 }}>
        <input
          className="admin-filter-input"
          style={{ minWidth: 280, flex: 1 }}
          value={conversationId}
          onChange={(e) => setConversationId(e.target.value)}
          placeholder="conversationId"
        />
        <button type="button" className="admin-btn" onClick={handleLoadByConversation} disabled={loading}>
          Load by conversation
        </button>
      </div>

      <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: 12 }}>
        <input
          className="admin-filter-input"
          style={{ minWidth: 280, flex: 1 }}
          value={messageId}
          onChange={(e) => setMessageId(e.target.value)}
          placeholder="messageId"
        />
        <button type="button" className="admin-btn" onClick={handleLoadByMessageId} disabled={loading}>
          Load by messageId
        </button>
      </div>

      {error ? <div className="admin-alert admin-alert-error">{error}</div> : null}
      {loading ? <div className="admin-muted">Dang tai...</div> : null}

      <div className="admin-table-wrap">
        <table className="admin-table">
          <thead>
            <tr>
              <th>messageId</th>
              <th>conversationId</th>
              <th>userId</th>
              <th>agentId</th>
              <th>role</th>
              <th>status</th>
              <th>content</th>
              <th>createdAt</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((m, idx) => (
              <tr key={m.messageId || `m-${idx}`}>
                <td className="admin-cell-mono">{m.messageId || '—'}</td>
                <td className="admin-cell-mono">{m.conversationId || '—'}</td>
                <td className="admin-cell-mono">{m.userId || '—'}</td>
                <td className="admin-cell-mono">{m.agentId || '—'}</td>
                <td>{m.role || '—'}</td>
                <td>{m.status || '—'}</td>
                <td title={m.content || ''}>{shortText(m.content, 72)}</td>
                <td>{formatDate(m.createdAt)}</td>
              </tr>
            ))}
            {!loading && rows.length === 0 ? (
              <tr>
                <td colSpan={8} style={{ padding: 12, color: '#6b7280' }}>
                  Chua co du lieu.
                </td>
              </tr>
            ) : null}
          </tbody>
        </table>
      </div>
    </div>
  );
}
