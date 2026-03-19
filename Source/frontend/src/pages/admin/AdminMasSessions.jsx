import { useCallback, useState } from 'react';
import { handleAPIError } from '../../services/errorHandler';
import { createMasSession, listMasSessionsByUser, updateMasSessionStatus } from '../../services/adminMasSessionApi';

const STATUS_OPTIONS = ['ACTIVE', 'COMPLETED', 'ARCHIVED'];

function formatDate(v) {
  if (!v) return '—';
  if (Array.isArray(v)) {
    const [y, m, d, h = 0, mm = 0, s = 0] = v;
    return `${y}-${String(m).padStart(2, '0')}-${String(d).padStart(2, '0')} ${String(h).padStart(2, '0')}:${String(mm).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
  }
  return String(v);
}

export default function AdminMasSessions() {
  const [userId, setUserId] = useState('');
  const [conversationId, setConversationId] = useState('');
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const load = useCallback(async () => {
    if (!userId.trim()) {
      setRows([]);
      return;
    }
    setLoading(true);
    setError('');
    try {
      const data = await listMasSessionsByUser(userId.trim());
      setRows(Array.isArray(data) ? data : []);
    } catch (e) {
      setError(handleAPIError(e).message);
      setRows([]);
    } finally {
      setLoading(false);
    }
  }, [userId]);

  const handleCreate = async () => {
    if (!userId.trim()) {
      setError('Vui lòng nhập userId');
      return;
    }
    setLoading(true);
    setError('');
    try {
      await createMasSession({ userId: userId.trim(), conversationId: conversationId.trim() });
      setConversationId('');
      await load();
    } catch (e) {
      setError(handleAPIError(e).message);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateStatus = async (sessionId, status) => {
    if (!sessionId) return;
    setLoading(true);
    setError('');
    try {
      await updateMasSessionStatus(sessionId, status);
      await load();
    } catch (e) {
      setError(handleAPIError(e).message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="admin-panel">
      <p className="admin-muted" style={{ marginBottom: 12 }}>Backend không có API xóa session.</p>
      <div className="admin-toolbar">
        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
          <input
            style={{ minWidth: 220 }}
            className="admin-filter-input"
            value={userId}
            onChange={(e) => setUserId(e.target.value)}
            placeholder="userId"
          />
          <button type="button" className="admin-btn" onClick={load} disabled={loading}>
            Load
          </button>
        </div>
      </div>

      <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: 12 }}>
        <input
          style={{ minWidth: 260, flex: 1 }}
          className="admin-filter-input"
          value={conversationId}
          onChange={(e) => setConversationId(e.target.value)}
          placeholder="conversationId (optional)"
        />
        <button type="button" className="admin-btn admin-btn-primary" onClick={handleCreate} disabled={loading}>
          Tạo session
        </button>
      </div>

      {error ? <div className="admin-alert admin-alert-error">{error}</div> : null}
      {loading ? <div className="admin-muted">Đang tải...</div> : null}

      <div className="admin-table-wrap">
        <table className="admin-table">
          <thead>
            <tr>
              <th>sessionId</th>
              <th>userId</th>
              <th>conversationId</th>
              <th>status</th>
              <th>createdAt</th>
              <th>updatedAt</th>
              <th />
            </tr>
          </thead>
          <tbody>
            {rows.map((s) => (
              <tr key={s.sessionId}>
                <td className="admin-cell-mono">{s.sessionId || '—'}</td>
                <td className="admin-cell-mono">{s.userId || '—'}</td>
                <td className="admin-cell-mono">{s.conversationId || '—'}</td>
                <td>{s.status || '—'}</td>
                <td>{formatDate(s.createdAt)}</td>
                <td>{formatDate(s.updatedAt)}</td>
                <td className="admin-actions">
                  <select
                    className="admin-filter-input"
                    value={s.status || 'ACTIVE'}
                    onChange={(e) => handleUpdateStatus(s.sessionId, e.target.value)}
                    disabled={loading}
                  >
                    {STATUS_OPTIONS.map((opt) => (
                      <option key={opt} value={opt}>
                        {opt}
                      </option>
                    ))}
                  </select>
                </td>
              </tr>
            ))}
            {!loading && rows.length === 0 ? (
              <tr>
                <td colSpan={7} style={{ padding: 12, color: '#6b7280' }}>
                  Chưa có dữ liệu. Nhập userId và bấm Load.
                </td>
              </tr>
            ) : null}
          </tbody>
        </table>
      </div>
    </div>
  );
}
