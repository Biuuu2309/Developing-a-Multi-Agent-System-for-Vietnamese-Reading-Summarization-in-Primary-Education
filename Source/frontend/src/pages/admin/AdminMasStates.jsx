import { useCallback, useState } from 'react';
import { handleAPIError } from '../../services/errorHandler';
import { getLatestMasState, listMasStatesBySession } from '../../services/adminMasStateApi';

function fmtDate(v) {
  if (!v) return '—';
  if (Array.isArray(v)) {
    const [y, m, d, h = 0, mm = 0, s = 0] = v;
    return `${y}-${String(m).padStart(2, '0')}-${String(d).padStart(2, '0')} ${String(h).padStart(2, '0')}:${String(mm).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
  }
  return String(v);
}

function shortText(v, max = 56) {
  if (!v) return '—';
  const s = String(v);
  return s.length > max ? `${s.slice(0, max)}...` : s;
}

export default function AdminMasStates() {
  const [userId, setUserId] = useState('');
  const [sessionId, setSessionId] = useState('');
  const [rows, setRows] = useState([]);
  const [latest, setLatest] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const canLoad = userId.trim() && sessionId.trim();

  const loadHistory = useCallback(async () => {
    if (!canLoad) {
      setError('Vui lòng nhập userId và sessionId');
      return;
    }
    setLoading(true);
    setError('');
    try {
      const data = await listMasStatesBySession(sessionId.trim(), userId.trim());
      setRows(Array.isArray(data) ? data : []);
    } catch (e) {
      setRows([]);
      setError(handleAPIError(e).message);
    } finally {
      setLoading(false);
    }
  }, [canLoad, sessionId, userId]);

  const loadLatest = useCallback(async () => {
    if (!canLoad) {
      setError('Vui lòng nhập userId và sessionId');
      return;
    }
    setLoading(true);
    setError('');
    try {
      const data = await getLatestMasState(sessionId.trim(), userId.trim());
      setLatest(data || null);
    } catch (e) {
      setLatest(null);
      setError(handleAPIError(e).message);
    } finally {
      setLoading(false);
    }
  }, [canLoad, sessionId, userId]);

  return (
    <div className="admin-panel">
      <p className="admin-muted" style={{ marginBottom: 12 }}>Bảng read-only. Không có API sửa/xóa mas_states.</p>
      <div className="admin-toolbar">
        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
          <input
            className="admin-filter-input"
            style={{ minWidth: 220 }}
            value={userId}
            onChange={(e) => setUserId(e.target.value)}
            placeholder="userId"
          />
          <input
            className="admin-filter-input"
            style={{ minWidth: 320, flex: 1 }}
            value={sessionId}
            onChange={(e) => setSessionId(e.target.value)}
            placeholder="sessionId"
          />
          <button type="button" className="admin-btn" onClick={loadHistory} disabled={loading}>
            Load history
          </button>
          <button type="button" className="admin-btn admin-btn-primary" onClick={loadLatest} disabled={loading}>
            Load latest
          </button>
        </div>
      </div>

      {error ? <div className="admin-alert admin-alert-error">{error}</div> : null}
      {loading ? <div className="admin-muted">Dang tai...</div> : null}

      {latest ? (
        <div style={{ marginBottom: 12, padding: 10, border: '1px solid #e5e7eb', borderRadius: 8 }}>
          <div className="admin-muted">Latest state</div>
          <div style={{ marginTop: 4 }}>
            <span className="admin-cell-mono">{latest.stateId}</span> | intent: {shortText(latest.intent, 80)} |
            needsImprovement: {latest.needsImprovement ? 'true' : 'false'}
          </div>
        </div>
      ) : null}

      <div className="admin-table-wrap">
        <table className="admin-table">
          <thead>
            <tr>
              <th>stateId</th>
              <th>messageId</th>
              <th>intent</th>
              <th>clarificationNeeded</th>
              <th>needsImprovement</th>
              <th>createdAt</th>
              <th>finalOutput</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r, idx) => (
              <tr key={r.stateId || `state-${idx}`}>
                <td className="admin-cell-mono">{r.stateId || '—'}</td>
                <td className="admin-cell-mono">{r.messageId || '—'}</td>
                <td title={r.intent || ''}>{shortText(r.intent)}</td>
                <td>{r.clarificationNeeded ? 'true' : 'false'}</td>
                <td>{r.needsImprovement ? 'true' : 'false'}</td>
                <td>{fmtDate(r.createdAt)}</td>
                <td title={r.finalOutput || ''}>{shortText(r.finalOutput)}</td>
              </tr>
            ))}
            {!loading && rows.length === 0 ? (
              <tr>
                <td colSpan={7} style={{ padding: 12, color: '#6b7280' }}>
                  Chua co du lieu. Nhap userId, sessionId va Load.
                </td>
              </tr>
            ) : null}
          </tbody>
        </table>
      </div>
    </div>
  );
}
