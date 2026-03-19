import { useCallback, useEffect, useMemo, useState } from 'react';
import { handleAPIError } from '../../services/errorHandler';
import { deleteSummary, listSummaries, updateSummaryTitleAndStatus } from '../../services/adminSummaryApi';

const STATUS_OPTIONS = ['PENDING', 'APPROVED', 'REJECTED'];

export default function AdminSummaries() {
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [editing, setEditing] = useState(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const data = await listSummaries();
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

  const handleDelete = async (summaryId) => {
    if (!window.confirm(`Xóa summary ${summaryId}?`)) return;
    setError('');
    try {
      await deleteSummary(summaryId);
      await load();
    } catch (e) {
      setError(handleAPIError(e).message);
    }
  };

  const selectedStatus = useMemo(() => editing?.status || 'PENDING', [editing]);

  return (
    <div className="admin-panel">
      <div className="admin-toolbar">
        <button type="button" className="admin-btn admin-btn-primary" onClick={load} disabled={loading}>
          Làm mới
        </button>
      </div>

      {error ? <div className="admin-alert admin-alert-error">{error}</div> : null}
      {loading ? <div className="admin-muted">Đang tải...</div> : null}

      <div className="admin-table-wrap">
        <table className="admin-table">
          <thead>
            <tr>
              <th>summaryId</th>
              <th>title</th>
              <th>status</th>
              <th>method</th>
              <th>grade</th>
              <th>readCount</th>
              <th>createdBy</th>
              <th>createdAt</th>
              <th />
            </tr>
          </thead>
          <tbody>
            {rows.map((s) => (
              <tr key={s.summaryId}>
                <td className="admin-cell-mono">{s.summaryId}</td>
                <td>{s.title || '—'}</td>
                <td>{s.status || 'PENDING'}</td>
                <td>{s.method || '—'}</td>
                <td>{s.grade || '—'}</td>
                <td>{Number(s.readCount ?? 0)}</td>
                <td className="admin-cell-mono">{s.createdByUserId || '—'}</td>
                <td>{s.createdAt ? new Date(s.createdAt).toLocaleString() : '—'}</td>
                <td className="admin-actions">
                  <button type="button" className="admin-btn admin-btn-sm" onClick={() => setEditing(s)}>
                    Sửa
                  </button>
                  <button
                    type="button"
                    className="admin-btn admin-btn-sm admin-btn-danger"
                    onClick={() => handleDelete(s.summaryId)}
                  >
                    Xóa
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {editing ? (
        <EditSummaryModal
          initial={editing}
          status={selectedStatus}
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

function EditSummaryModal({ initial, onClose, onSaved }) {
  const [title, setTitle] = useState(initial?.title || '');
  const [status, setStatus] = useState(initial?.status || 'PENDING');
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    if (!title.trim()) {
      setError('title không được trống');
      return;
    }
    setSaving(true);
    try {
      await updateSummaryTitleAndStatus(initial.summaryId, { title: title.trim(), status });
      await onSaved();
    } catch (e2) {
      setError(handleAPIError(e2).message);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="admin-modal-backdrop" role="presentation" onClick={onClose}>
      <div className="admin-modal" role="dialog" onClick={(ev) => ev.stopPropagation()}>
        <div className="admin-modal-head">
          <h2 className="admin-modal-title">Sửa summary</h2>
          <button type="button" className="admin-btn" onClick={onClose}>
            Đóng
          </button>
        </div>

        {error ? <div className="admin-alert admin-alert-error">{error}</div> : null}

        <form onSubmit={handleSubmit} className="admin-form">
          <label className="admin-field">
            <span>title</span>
            <input value={title} onChange={(e) => setTitle(e.target.value)} required />
          </label>

          <label className="admin-field">
            <span>status</span>
            <select value={status} onChange={(e) => setStatus(e.target.value)}>
              {STATUS_OPTIONS.map((st) => (
                <option key={st} value={st}>
                  {st}
                </option>
              ))}
            </select>
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

