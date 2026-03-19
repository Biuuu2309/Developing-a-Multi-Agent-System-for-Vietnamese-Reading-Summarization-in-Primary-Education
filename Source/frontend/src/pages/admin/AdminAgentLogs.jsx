import { useState } from 'react';
import { handleAPIError } from '../../services/errorHandler';
import { getAgentLogById, getAgentLogsByAgent, getAgentLogsByMessage } from '../../services/adminAgentLogApi';

function formatDate(v) {
  if (!v) return '—';
  if (Array.isArray(v)) {
    const [y, m, d, h = 0, mm = 0, s = 0] = v;
    return `${y}-${String(m).padStart(2, '0')}-${String(d).padStart(2, '0')} ${String(h).padStart(2, '0')}:${String(mm).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
  }
  return String(v);
}

function shortText(v, n = 72) {
  if (!v) return '—';
  const s = String(v);
  return s.length > n ? `${s.slice(0, n)}...` : s;
}

export default function AdminAgentLogs() {
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [messageId, setMessageId] = useState('');
  const [agentId, setAgentId] = useState('');
  const [logId, setLogId] = useState('');

  const handleByMessage = async () => {
    if (!messageId.trim()) {
      setError('Vui long nhap messageId');
      return;
    }
    setLoading(true);
    setError('');
    try {
      const data = await getAgentLogsByMessage(messageId.trim());
      setRows(Array.isArray(data) ? data : []);
    } catch (e) {
      setRows([]);
      setError(handleAPIError(e).message);
    } finally {
      setLoading(false);
    }
  };

  const handleByAgent = async () => {
    if (!agentId.trim()) {
      setError('Vui long nhap agentId');
      return;
    }
    setLoading(true);
    setError('');
    try {
      const data = await getAgentLogsByAgent(agentId.trim());
      setRows(Array.isArray(data) ? data : []);
    } catch (e) {
      setRows([]);
      setError(handleAPIError(e).message);
    } finally {
      setLoading(false);
    }
  };

  const handleById = async () => {
    if (!logId.trim()) {
      setError('Vui long nhap logId');
      return;
    }
    setLoading(true);
    setError('');
    try {
      const data = await getAgentLogById(logId.trim());
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
      <p className="admin-muted" style={{ marginBottom: 12 }}>Read-only. Backend khong co API xoa/sua agent_log.</p>

      <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: 8 }}>
        <input
          className="admin-filter-input"
          style={{ minWidth: 280, flex: 1 }}
          value={messageId}
          onChange={(e) => setMessageId(e.target.value)}
          placeholder="messageId"
        />
        <button type="button" className="admin-btn" onClick={handleByMessage} disabled={loading}>
          Load by messageId
        </button>
      </div>

      <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: 8 }}>
        <input
          className="admin-filter-input"
          style={{ minWidth: 280, flex: 1 }}
          value={agentId}
          onChange={(e) => setAgentId(e.target.value)}
          placeholder="agentId"
        />
        <button type="button" className="admin-btn" onClick={handleByAgent} disabled={loading}>
          Load by agentId
        </button>
      </div>

      <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: 12 }}>
        <input
          className="admin-filter-input"
          style={{ minWidth: 280, flex: 1 }}
          value={logId}
          onChange={(e) => setLogId(e.target.value)}
          placeholder="logId"
        />
        <button type="button" className="admin-btn admin-btn-primary" onClick={handleById} disabled={loading}>
          Load by logId
        </button>
      </div>

      {error ? <div className="admin-alert admin-alert-error">{error}</div> : null}
      {loading ? <div className="admin-muted">Dang tai...</div> : null}

      <div className="admin-table-wrap">
        <table className="admin-table">
          <thead>
            <tr>
              <th>logId</th>
              <th>sessionId</th>
              <th>messageId</th>
              <th>agentId</th>
              <th>status</th>
              <th>durationMs</th>
              <th>input</th>
              <th>output</th>
              <th>createdAt</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r, idx) => (
              <tr key={r.logId || `log-${idx}`}>
                <td className="admin-cell-mono">{r.logId || '—'}</td>
                <td className="admin-cell-mono">{r.sessionId || '—'}</td>
                <td className="admin-cell-mono">{r.messageId || '—'}</td>
                <td className="admin-cell-mono">{r.agentId || '—'}</td>
                <td>{r.status || '—'}</td>
                <td>{r.durationMs ?? '—'}</td>
                <td title={r.input || ''}>{shortText(r.input)}</td>
                <td title={r.output || ''}>{shortText(r.output)}</td>
                <td>{formatDate(r.createdAt)}</td>
              </tr>
            ))}
            {!loading && rows.length === 0 ? (
              <tr>
                <td colSpan={9} style={{ padding: 12, color: '#6b7280' }}>
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
