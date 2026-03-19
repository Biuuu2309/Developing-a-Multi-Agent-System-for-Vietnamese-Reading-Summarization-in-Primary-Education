import { useCallback, useEffect, useState } from 'react';
import { handleAPIError } from '../../services/errorHandler';
import { createConversation, deleteConversation, listConversations } from '../../services/adminConversationApi';

function convId(c) {
  return c?.conversation_id ?? c?.conversationId ?? '';
}

function userIdOf(c) {
  return c?.user_id ?? c?.userId ?? '';
}

export default function AdminConversations() {
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [newUserId, setNewUserId] = useState('');
  const [newTitle, setNewTitle] = useState('');

  const load = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const data = await listConversations();
      setRows(Array.isArray(data) ? data : []);
    } catch (e) {
      setError(handleAPIError(e).message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const handleCreate = async () => {
    if (!newUserId.trim()) {
      setError('Cần user_id');
      return;
    }
    setError('');
    setLoading(true);
    try {
      await createConversation({ user_id: newUserId.trim(), title: newTitle.trim() || 'Chat' });
      setNewTitle('');
      await load();
    } catch (e) {
      setError(handleAPIError(e).message);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (!id || !window.confirm(`Xóa conversation ${id}?`)) return;
    setError('');
    try {
      await deleteConversation(id);
      await load();
    } catch (e) {
      setError(handleAPIError(e).message);
    }
  };

  return (
    <div className="admin-panel">
      <p className="admin-muted" style={{ marginBottom: 8 }}>Không có API sửa conversation trên backend.</p>
      <div className="admin-toolbar" style={{ marginBottom: 12 }}>
        <button type="button" className="admin-btn admin-btn-primary" onClick={load} disabled={loading}>
          Làm mới
        </button>
      </div>

      <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: 12 }}>
        <input
          className="admin-filter-input"
          style={{ minWidth: 200 }}
          value={newUserId}
          onChange={(e) => setNewUserId(e.target.value)}
          placeholder="user_id"
        />
        <input
          className="admin-filter-input"
          style={{ minWidth: 240, flex: 1 }}
          value={newTitle}
          onChange={(e) => setNewTitle(e.target.value)}
          placeholder="title (mặc định: Chat)"
        />
        <button type="button" className="admin-btn admin-btn-primary" onClick={handleCreate} disabled={loading}>
          Tạo
        </button>
      </div>

      {error ? <div className="admin-alert admin-alert-error">{error}</div> : null}
      {loading ? <div className="admin-muted">Đang tải...</div> : null}

      <div className="admin-table-wrap">
        <table className="admin-table">
          <thead>
            <tr>
              <th>conversation_id</th>
              <th>user_id</th>
              <th>title</th>
              <th>status</th>
              <th>created_at</th>
              <th>updated_at</th>
              <th />
            </tr>
          </thead>
          <tbody>
            {rows.map((c, idx) => {
              const id = convId(c);
              return (
                <tr key={id || `row-${idx}`}>
                  <td className="admin-cell-mono">{id || '—'}</td>
                  <td className="admin-cell-mono">{userIdOf(c) || '—'}</td>
                  <td>{c.title || '—'}</td>
                  <td>{c.status || '—'}</td>
                  <td>{c.created_at ?? c.createdAt ?? '—'}</td>
                  <td>{c.updated_at ?? c.updatedAt ?? '—'}</td>
                  <td className="admin-actions">
                    <button
                      type="button"
                      className="admin-btn admin-btn-sm admin-btn-danger"
                      onClick={() => handleDelete(id)}
                      disabled={!id}
                    >
                      Xóa
                    </button>
                  </td>
                </tr>
              );
            })}
            {!loading && rows.length === 0 ? (
              <tr>
                <td colSpan={7} style={{ padding: 12, color: '#6b7280' }}>
                  Chưa có conversation.
                </td>
              </tr>
            ) : null}
          </tbody>
        </table>
      </div>
    </div>
  );
}
