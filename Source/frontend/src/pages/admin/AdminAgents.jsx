import { useCallback, useEffect, useState } from 'react';
import { handleAPIError } from '../../services/errorHandler';
import { createAgent, deleteAgent, listAgents } from '../../services/adminAgentApi';

const AGENT_TYPES = [
  'INTENT',
  'CLARIFICATION',
  'PLANNING',
  'IMAGE2TEXT',
  'ABSTRACTER',
  'EXTRACTOR',
  'EVALUATION',
  'ORCHESTRATOR',
  'OTHER',
];

function formatDt(v) {
  if (v == null) return '—';
  if (Array.isArray(v)) {
    const [y, m, d, h = 0, mi = 0] = v;
    return `${y}-${String(m).padStart(2, '0')}-${String(d).padStart(2, '0')} ${String(h).padStart(2, '0')}:${String(mi).padStart(2, '0')}`;
  }
  return String(v);
}

function clip(s, n = 48) {
  if (s == null || s === '') return '—';
  const t = String(s);
  return t.length > n ? `${t.slice(0, n)}…` : t;
}

export default function AdminAgents() {
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [agentId, setAgentId] = useState('');
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [capabilities, setCapabilities] = useState('{}');
  const [agentType, setAgentType] = useState('OTHER');
  const [isActive, setIsActive] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const data = await listAgents();
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
    if (!name.trim()) {
      setError('Cần name');
      return;
    }
    let cap = capabilities.trim();
    if (cap) {
      try {
        JSON.parse(cap);
      } catch {
        setError('capabilities phải là JSON hợp lệ');
        return;
      }
    } else {
      cap = '{}';
    }
    const body = {
      name: name.trim(),
      description: description.trim(),
      capabilities: cap,
      agentType,
      isActive,
    };
    if (agentId.trim()) body.agentId = agentId.trim();
    setError('');
    setLoading(true);
    try {
      await createAgent(body);
      setAgentId('');
      setName('');
      setDescription('');
      setCapabilities('{}');
      setAgentType('OTHER');
      setIsActive(true);
      await load();
    } catch (e) {
      setError(handleAPIError(e).message);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (!id || !window.confirm(`Xóa agent ${id}?`)) return;
    setError('');
    try {
      await deleteAgent(id);
      await load();
    } catch (e) {
      setError(handleAPIError(e).message);
    }
  };

  return (
    <div className="admin-panel">
      <p className="admin-muted" style={{ marginBottom: 8 }}>Backend không có PUT — chỉ tạo/xóa.</p>
      <div className="admin-toolbar" style={{ marginBottom: 12 }}>
        <button type="button" className="admin-btn admin-btn-primary" onClick={load} disabled={loading}>
          Làm mới
        </button>
      </div>

      <div className="admin-form" style={{ display: 'grid', gap: 8, marginBottom: 16, maxWidth: 640 }}>
        <input
          className="admin-filter-input"
          value={agentId}
          onChange={(e) => setAgentId(e.target.value)}
          placeholder="agentId (để trống → server tạo UUID)"
        />
        <input
          className="admin-filter-input"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="name *"
        />
        <input
          className="admin-filter-input"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="description"
        />
        <textarea
          className="admin-filter-input"
          rows={3}
          value={capabilities}
          onChange={(e) => setCapabilities(e.target.value)}
          placeholder='capabilities (JSON), ví dụ: {}'
        />
        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', alignItems: 'center' }}>
          <select className="admin-filter-input" value={agentType} onChange={(e) => setAgentType(e.target.value)}>
            {AGENT_TYPES.map((t) => (
              <option key={t} value={t}>
                {t}
              </option>
            ))}
          </select>
          <label style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <input type="checkbox" checked={isActive} onChange={(e) => setIsActive(e.target.checked)} />
            isActive
          </label>
          <button type="button" className="admin-btn admin-btn-primary" onClick={handleCreate} disabled={loading}>
            Tạo
          </button>
        </div>
      </div>

      {error ? <div className="admin-alert admin-alert-error">{error}</div> : null}
      {loading ? <div className="admin-muted">Đang tải...</div> : null}

      <div className="admin-table-wrap">
        <table className="admin-table">
          <thead>
            <tr>
              <th>agentId</th>
              <th>name</th>
              <th>agentType</th>
              <th>isActive</th>
              <th>capabilities</th>
              <th>description</th>
              <th>createdAt</th>
              <th />
            </tr>
          </thead>
          <tbody>
            {rows.map((a, idx) => (
              <tr key={a.agentId || `a-${idx}`}>
                <td className="admin-cell-mono">{a.agentId || '—'}</td>
                <td>{a.name || '—'}</td>
                <td>{a.agentType || '—'}</td>
                <td>{a.isActive === false ? 'false' : 'true'}</td>
                <td title={a.capabilities || ''}>{clip(a.capabilities, 32)}</td>
                <td title={a.description || ''}>{clip(a.description, 40)}</td>
                <td>{formatDt(a.createdAt)}</td>
                <td className="admin-actions">
                  <button
                    type="button"
                    className="admin-btn admin-btn-sm admin-btn-danger"
                    onClick={() => handleDelete(a.agentId)}
                    disabled={!a.agentId}
                  >
                    Xóa
                  </button>
                </td>
              </tr>
            ))}
            {!loading && rows.length === 0 ? (
              <tr>
                <td colSpan={8} style={{ padding: 12, color: '#6b7280' }}>
                  Chưa có agent.
                </td>
              </tr>
            ) : null}
          </tbody>
        </table>
      </div>
    </div>
  );
}
