import { useCallback, useEffect, useMemo, useState } from 'react';
import { handleAPIError } from '../../services/errorHandler';
import {
  deleteSummaryHistory,
  listSummaryHistoriesBySession,
  updateSummaryHistory,
} from '../../services/adminSummaryHistoryApi';

const METHOD_OPTIONS = ['PHOBERT', 'T5_DIEN_GIAI', 'EXTRACTIVE', 'ABSTRACTIVE'];

function clampText(s, maxLen = 120) {
  const v = typeof s === 'string' ? s : '';
  if (v.length <= maxLen) return v;
  return v.slice(0, maxLen) + '...';
}

export default function AdminSummaryHistory() {
  const [sessionId, setSessionId] = useState('');
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [editing, setEditing] = useState(null);

  const load = useCallback(async () => {
    if (!sessionId.trim()) {
      setRows([]);
      return;
    }
    setLoading(true);
    setError('');
    try {
      const data = await listSummaryHistoriesBySession(sessionId.trim());
      setRows(Array.isArray(data) ? data : []);
    } catch (e) {
      setError(handleAPIError(e).message);
      setRows([]);
    } finally {
      setLoading(false);
    }
  }, [sessionId]);

  useEffect(() => {
    // Không tự load cho tới khi user nhập sessionId và bấm Load
  }, []);

  const handleDelete = async (historyId) => {
    if (!window.confirm(`Xóa summary_history ${historyId}?`)) return;
    setError('');
    setLoading(true);
    try {
      await deleteSummaryHistory(historyId);
      await load();
    } catch (e) {
      setError(handleAPIError(e).message);
    } finally {
      setLoading(false);
    }
  };

  const editingMethod = useMemo(() => editing?.method || '', [editing]);

  return (
    <div className="admin-panel">
      <div className="admin-toolbar">
        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
          <input
            className="admin-filter-input"
            style={{ minWidth: 280 }}
            value={sessionId}
            onChange={(e) => setSessionId(e.target.value)}
            placeholder="sessionId (ví dụ: 1)"
          />
          <button type="button" className="admin-btn" onClick={load} disabled={loading}>
            Load
          </button>
        </div>
      </div>

      {error ? <div className="admin-alert admin-alert-error">{error}</div> : null}
      {loading ? <div className="admin-muted">Đang tải...</div> : null}

      <div className="admin-table-wrap">
        <table className="admin-table">
          <thead>
            <tr>
              <th>historyId</th>
              <th>sessionId</th>
              <th>method</th>
              <th>isAccepted</th>
              <th>timestamp</th>
              <th>summaryContent</th>
              <th>userInput</th>
              <th>evaluation</th>
              <th />
            </tr>
          </thead>
          <tbody>
            {rows.map((h) => (
              <tr key={h.historyId}>
                <td className="admin-cell-mono">{h.historyId}</td>
                <td className="admin-cell-mono">{h.sessionId ?? '—'}</td>
                <td>{h.method || '—'}</td>
                <td>{h.isAccepted ? 'yes' : 'no'}</td>
                <td className="admin-cell-mono">{h.timestamp || '—'}</td>
                <td>{clampText(h.summaryContent, 110) || '—'}</td>
                <td>{clampText(h.userInput, 110) || '—'}</td>
                <td>{clampText(h.evaluation, 110) || '—'}</td>
                <td className="admin-actions">
                  <button type="button" className="admin-btn admin-btn-sm" onClick={() => setEditing(h)}>
                    Sửa
                  </button>
                  <button
                    type="button"
                    className="admin-btn admin-btn-sm admin-btn-danger"
                    onClick={() => handleDelete(h.historyId)}
                  >
                    Xóa
                  </button>
                </td>
              </tr>
            ))}
            {!loading && rows.length === 0 ? (
              <tr>
                <td colSpan={9} style={{ padding: 12, color: '#6b7280' }}>
                  Chưa có dữ liệu. Nhập `sessionId` và bấm Load.
                </td>
              </tr>
            ) : null}
          </tbody>
        </table>
      </div>

      {editing ? (
        <EditSummaryHistoryModal
          initial={editing}
          methodOptions={METHOD_OPTIONS}
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

function EditSummaryHistoryModal({ initial, methodOptions, onClose, onSaved }) {
  const [method, setMethod] = useState(initial?.method || '');
  const [summaryContent, setSummaryContent] = useState(initial?.summaryContent || '');
  const [isAccepted, setIsAccepted] = useState(!!initial?.isAccepted);
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    if (!method.trim()) {
      setError('method không được trống');
      return;
    }
    setSaving(true);
    try {
      await updateSummaryHistory(initial.historyId, {
        method: method.trim(),
        summaryContent,
        isAccepted,
      });
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
          <h2 className="admin-modal-title">Sửa summary_history</h2>
          <button type="button" className="admin-btn" onClick={onClose}>
            Đóng
          </button>
        </div>
        {error ? <div className="admin-alert admin-alert-error">{error}</div> : null}

        <form onSubmit={handleSubmit} className="admin-form">
          <label className="admin-field">
            <span>method</span>
            <select value={method} onChange={(e) => setMethod(e.target.value)}>
              {methodOptions.map((m) => (
                <option key={m} value={m}>
                  {m}
                </option>
              ))}
            </select>
          </label>

          <label className="admin-field">
            <span>summaryContent</span>
            <textarea
              value={summaryContent}
              onChange={(e) => setSummaryContent(e.target.value)}
              rows={6}
              style={{ width: '100%', padding: 8, borderRadius: 8, border: '1px solid #e5e7eb' }}
            />
          </label>

          <label className="admin-field admin-field-inline">
            <input type="checkbox" checked={isAccepted} onChange={(e) => setIsAccepted(e.target.checked)} />
            <span>isAccepted</span>
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

