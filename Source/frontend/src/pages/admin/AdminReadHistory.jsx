import { useCallback, useState } from 'react';
import { handleAPIError } from '../../services/errorHandler';
import { listReadHistoryByUser, logReadHistory } from '../../services/adminReadHistoryApi';

export default function AdminReadHistory() {
  const [userId, setUserId] = useState('');
  const [summaryIdForLog, setSummaryIdForLog] = useState('');
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
      const data = await listReadHistoryByUser(userId.trim());
      setRows(Array.isArray(data) ? data : []);
    } catch (e) {
      setError(handleAPIError(e).message);
      setRows([]);
    } finally {
      setLoading(false);
    }
  }, [userId]);

  const handleLog = async () => {
    if (!userId.trim() || !summaryIdForLog.trim()) {
      setError('Cần userId và summaryId để ghi log');
      return;
    }
    setError('');
    setLoading(true);
    try {
      await logReadHistory(userId.trim(), summaryIdForLog.trim());
      setSummaryIdForLog('');
      await load();
    } catch (e) {
      setError(handleAPIError(e).message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="admin-panel">
      <p className="admin-muted" style={{ marginBottom: 12 }}>
        Backend: chỉ có xem theo user và POST log. Không có API xóa/sửa.
      </p>
      <div className="admin-toolbar">
        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
          <input
            style={{ minWidth: 240 }}
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
          style={{ minWidth: 280, flex: 1 }}
          className="admin-filter-input"
          value={summaryIdForLog}
          onChange={(e) => setSummaryIdForLog(e.target.value)}
          placeholder="summaryId (ghi thêm lượt đọc cho userId đã nhập)"
        />
        <button type="button" className="admin-btn admin-btn-primary" onClick={handleLog} disabled={loading}>
          Ghi log đọc
        </button>
      </div>

      {error ? <div className="admin-alert admin-alert-error">{error}</div> : null}
      {loading ? <div className="admin-muted">Đang tải...</div> : null}

      <div className="admin-table-wrap">
        <table className="admin-table">
          <thead>
            <tr>
              <th>id</th>
              <th>userId</th>
              <th>summaryId</th>
              <th>title</th>
              <th>imageUrl</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.id}>
                <td className="admin-cell-mono">{r.id}</td>
                <td className="admin-cell-mono">{r.userId || '—'}</td>
                <td className="admin-cell-mono">{r.summaryId || '—'}</td>
                <td>{r.title || '—'}</td>
                <td className="admin-cell-mono" style={{ maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis' }}>
                  {r.imageUrl || '—'}
                </td>
              </tr>
            ))}
            {!loading && rows.length === 0 ? (
              <tr>
                <td colSpan={5} style={{ padding: 12, color: '#6b7280' }}>
                  Chưa có dữ liệu. Nhập userId và Load.
                </td>
              </tr>
            ) : null}
          </tbody>
        </table>
      </div>
    </div>
  );
}
