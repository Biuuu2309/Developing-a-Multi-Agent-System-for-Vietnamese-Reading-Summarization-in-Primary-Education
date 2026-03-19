import { useCallback, useEffect, useState } from 'react';
import { handleAPIError } from '../../services/errorHandler';
import {
  createSummarySession,
  deleteSummarySession,
  listSummarySessionsByUser,
  updateSummarySession,
} from '../../services/adminSummarySessionApi';

function safeSessionUserId(s) {
  return s?.createdBy?.userId || s?.userId || '';
}

function safeSessionUsername(s) {
  return s?.createdBy?.username || s?.username || '';
}

export default function AdminSummarySessions() {
  const [userId, setUserId] = useState('');
  const [content, setContent] = useState('');

  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const [editing, setEditing] = useState(null);

  const load = useCallback(async () => {
    if (!userId.trim()) {
      setRows([]);
      return;
    }
    setLoading(true);
    setError('');
    try {
      const data = await listSummarySessionsByUser(userId.trim());
      setRows(Array.isArray(data) ? data : []);
    } catch (e) {
      setError(handleAPIError(e).message);
      setRows([]);
    } finally {
      setLoading(false);
    }
  }, [userId]);

  useEffect(() => {
    // Không tự load cho đến khi admin nhập userId
  }, []);

  const handleCreate = async () => {
    if (!userId.trim()) {
      setError('Vui lòng nhập userId');
      return;
    }
    setError('');
    setLoading(true);
    try {
      await createSummarySession({ userId: userId.trim(), content });
      setContent('');
      await load();
    } catch (e) {
      setError(handleAPIError(e).message);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (sessionId) => {
    if (!window.confirm(`Xóa summary_session ${sessionId}?`)) return;
    setError('');
    setLoading(true);
    try {
      await deleteSummarySession(sessionId);
      await load();
    } catch (e) {
      setError(handleAPIError(e).message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="admin-panel">
      <div className="admin-toolbar">
        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
          <input
            style={{ minWidth: 240 }}
            className="admin-filter-input"
            value={userId}
            onChange={(e) => setUserId(e.target.value)}
            placeholder="userId (ví dụ: 123)"
          />
          <button type="button" className="admin-btn" onClick={load} disabled={loading}>
            Load
          </button>
        </div>
      </div>

      <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: 12 }}>
        <input
          style={{ minWidth: 360, flex: 1 }}
          className="admin-filter-input"
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder="content ban đầu (có thể trống)"
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
              <th>username</th>
              <th>timestamp</th>
              <th>content</th>
              <th>contentHash</th>
              <th />
            </tr>
          </thead>
          <tbody>
            {rows.map((s) => (
              <tr key={s.sessionId}>
                <td className="admin-cell-mono">{s.sessionId}</td>
                <td className="admin-cell-mono">{safeSessionUserId(s) || '—'}</td>
                <td>{safeSessionUsername(s) || '—'}</td>
                <td>{s.timestamp ? String(s.timestamp) : '—'}</td>
                <td>{s.content || '—'}</td>
                <td className="admin-cell-mono">{s.contentHash || '—'}</td>
                <td className="admin-actions">
                  <button type="button" className="admin-btn admin-btn-sm" onClick={() => setEditing(s)}>
                    Sửa
                  </button>
                  <button
                    type="button"
                    className="admin-btn admin-btn-sm admin-btn-danger"
                    onClick={() => handleDelete(s.sessionId)}
                  >
                    Xóa
                  </button>
                </td>
              </tr>
            ))}
            {!loading && rows.length === 0 ? (
              <tr>
                <td colSpan={7} style={{ padding: 12, color: '#6b7280' }}>
                  Chưa có dữ liệu. Nhập `userId` và bấm Load.
                </td>
              </tr>
            ) : null}
          </tbody>
        </table>
      </div>

      {editing ? (
        <EditSummarySessionModal
          session={editing}
          onClose={() => setEditing(null)}
          onSaved={async () => {
            setEditing(null);
            await load();
          }}
        />
      ) : null}
    </div>
  );
}

function EditSummarySessionModal({ session, onClose, onSaved }) {
  const [content, setContent] = useState(session?.content || '');
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSaving(true);
    try {
      await updateSummarySession(session.sessionId, { content });
      await onSaved();
    } catch (err) {
      setError(handleAPIError(err).message);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="admin-modal-backdrop" role="presentation" onClick={onClose}>
      <div className="admin-modal" role="dialog" onClick={(ev) => ev.stopPropagation()}>
        <div className="admin-modal-head">
          <h2 className="admin-modal-title">Sửa summary_session</h2>
          <button type="button" className="admin-btn" onClick={onClose}>
            Đóng
          </button>
        </div>
        {error ? <div className="admin-alert admin-alert-error">{error}</div> : null}

        <form onSubmit={handleSubmit} className="admin-form">
          <label className="admin-field">
            <span>content</span>
            <input value={content} onChange={(e) => setContent(e.target.value)} required />
          </label>

          <div className="admin-modal-actions">
            <button type="submit" className="admin-btn admin-btn-primary" disabled={saving}>
              {saving ? 'Đang lưu...' : 'Lưu'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

