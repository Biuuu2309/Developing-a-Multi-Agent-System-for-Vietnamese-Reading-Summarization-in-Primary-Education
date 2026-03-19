import { useState } from 'react';
import { handleAPIError } from '../../services/errorHandler';
import { listMasStatesBySession } from '../../services/adminMasStateApi';

function formatDate(v) {
  if (!v) return '—';
  if (Array.isArray(v)) {
    const [y, m, d, h = 0, mm = 0, s = 0] = v;
    return `${y}-${String(m).padStart(2, '0')}-${String(d).padStart(2, '0')} ${String(h).padStart(2, '0')}:${String(mm).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
  }
  return String(v);
}

function shortText(v, n = 90) {
  if (!v) return '—';
  const s = String(v);
  return s.length > n ? `${s.slice(0, n)}...` : s;
}

export default function AdminMasAgentConfidences() {
  const [userId, setUserId] = useState('');
  const [sessionId, setSessionId] = useState('');
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleLoad = async () => {
    if (!userId.trim() || !sessionId.trim()) {
      setError('Vui long nhap userId va sessionId');
      return;
    }
    setLoading(true);
    setError('');
    try {
      const states = await listMasStatesBySession(sessionId.trim(), userId.trim());
      const filtered = (Array.isArray(states) ? states : []).filter((s) => s?.agentConfidences);
      setRows(filtered);
    } catch (e) {
      setRows([]);
      setError(handleAPIError(e).message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="admin-panel">
      <p className="admin-muted" style={{ marginBottom: 12 }}>Read-only. Du lieu lay tu mas_states (field agentConfidences).</p>

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
          <button type="button" className="admin-btn admin-btn-primary" onClick={handleLoad} disabled={loading}>
            Load confidences
          </button>
        </div>
      </div>

      {error ? <div className="admin-alert admin-alert-error">{error}</div> : null}
      {loading ? <div className="admin-muted">Dang tai...</div> : null}

      <div className="admin-table-wrap">
        <table className="admin-table">
          <thead>
            <tr>
              <th>stateId</th>
              <th>messageId</th>
              <th>agentConfidences</th>
              <th>negotiationResult</th>
              <th>createdAt</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r, idx) => (
              <tr key={r.stateId || `ac-${idx}`}>
                <td className="admin-cell-mono">{r.stateId || '—'}</td>
                <td className="admin-cell-mono">{r.messageId || '—'}</td>
                <td title={r.agentConfidences || ''}>{shortText(r.agentConfidences)}</td>
                <td title={r.negotiationResult || ''}>{shortText(r.negotiationResult, 70)}</td>
                <td>{formatDate(r.createdAt)}</td>
              </tr>
            ))}
            {!loading && rows.length === 0 ? (
              <tr>
                <td colSpan={5} style={{ padding: 12, color: '#6b7280' }}>
                  Chua co du lieu agentConfidences.
                </td>
              </tr>
            ) : null}
          </tbody>
        </table>
      </div>
    </div>
  );
}
