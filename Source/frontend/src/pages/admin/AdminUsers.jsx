import { useCallback, useEffect, useState } from 'react';
import { handleAPIError } from '../../services/errorHandler';
import { createUser, deleteUser, listUsers, updateUserProfile } from '../../services/adminUserApi';

const ROLES = ['CHILD', 'CONTRIBUTOR', 'ADMIN'];

function pickActive(u) {
  if (typeof u.isActive === 'boolean') return u.isActive;
  if (typeof u.active === 'boolean') return u.active;
  return true;
}

export default function AdminUsers() {
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [createOpen, setCreateOpen] = useState(false);
  const [editUser, setEditUser] = useState(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const data = await listUsers();
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

  const handleDelete = async (userId) => {
    if (!window.confirm('Xóa user này?')) return;
    try {
      await deleteUser(userId);
      await load();
    } catch (e) {
      setError(handleAPIError(e).message);
    }
  };

  return (
    <div className="admin-panel">
      <div className="admin-toolbar">
        <button type="button" className="admin-btn admin-btn-primary" onClick={() => setCreateOpen(true)}>
          Thêm user
        </button>
        <button type="button" className="admin-btn" onClick={load} disabled={loading}>
          Làm mới
        </button>
      </div>

      {error ? <div className="admin-alert admin-alert-error">{error}</div> : null}

      {loading ? <div className="admin-muted">Đang tải...</div> : null}

      <div className="admin-table-wrap">
        <table className="admin-table">
          <thead>
            <tr>
              <th>userId</th>
              <th>username</th>
              <th>email</th>
              <th>role</th>
              <th>fullName</th>
              <th>phone</th>
              <th>active</th>
              <th />
            </tr>
          </thead>
          <tbody>
            {rows.map((u) => (
              <tr key={u.userId}>
                <td className="admin-cell-mono">{u.userId}</td>
                <td>{u.username}</td>
                <td>{u.email}</td>
                <td>{u.role}</td>
                <td>{u.fullName || '—'}</td>
                <td>{u.phoneNumber || '—'}</td>
                <td>{pickActive(u) ? 'yes' : 'no'}</td>
                <td className="admin-actions">
                  <button type="button" className="admin-btn admin-btn-sm" onClick={() => setEditUser(u)}>
                    Sửa
                  </button>
                  <button type="button" className="admin-btn admin-btn-sm admin-btn-danger" onClick={() => handleDelete(u.userId)}>
                    Xóa
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {createOpen ? (
        <UserFormModal
          title="Thêm user"
          mode="create"
          onClose={() => setCreateOpen(false)}
          onSaved={async () => {
            setCreateOpen(false);
            await load();
          }}
        />
      ) : null}

      {editUser ? (
        <UserFormModal
          title="Sửa user"
          mode="edit"
          initial={editUser}
          onClose={() => setEditUser(null)}
          onSaved={async () => {
            setEditUser(null);
            await load();
          }}
        />
      ) : null}
    </div>
  );
}

function UserFormModal({ title, mode, initial, onClose, onSaved }) {
  const [username, setUsername] = useState(initial?.username || '');
  const [password, setPassword] = useState('');
  const [email, setEmail] = useState(initial?.email || '');
  const [role, setRole] = useState(initial?.role || 'CHILD');
  const [fullName, setFullName] = useState(initial?.fullName || '');
  const [phoneNumber, setPhoneNumber] = useState(initial?.phoneNumber || '');
  const [avatarUrl, setAvatarUrl] = useState(initial?.avatarUrl || '');
  const [isActive, setIsActive] = useState(pickActive(initial || {}));
  const [err, setErr] = useState('');
  const [saving, setSaving] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErr('');
    setSaving(true);
    try {
      if (mode === 'create') {
        if (!username.trim() || !password || !email.trim()) {
          setErr('username, password, email là bắt buộc');
          setSaving(false);
          return;
        }
        await createUser({
          username: username.trim(),
          password,
          email: email.trim(),
          role,
          fullName: fullName.trim() || null,
          phoneNumber: phoneNumber.trim() || '',
          avatarUrl: avatarUrl.trim() || null,
          active: isActive,
        });
      } else {
        const id = initial.userId;
        const body = {
          username: username.trim(),
          email: email.trim(),
          role,
          fullName: fullName.trim() || null,
          phoneNumber: phoneNumber.trim() || '',
          avatarUrl: avatarUrl.trim() || null,
          active: isActive,
        };
        if (password.trim()) body.password = password.trim();
        await updateUserProfile(id, body);
      }
      await onSaved();
    } catch (e) {
      setErr(handleAPIError(e).message);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="admin-modal-backdrop" role="presentation" onClick={onClose}>
      <div className="admin-modal" role="dialog" onClick={(ev) => ev.stopPropagation()}>
        <div className="admin-modal-head">
          <h2 className="admin-modal-title">{title}</h2>
          <button type="button" className="admin-btn" onClick={onClose}>
            Đóng
          </button>
        </div>
        <form onSubmit={handleSubmit} className="admin-form">
          {err ? <div className="admin-alert admin-alert-error">{err}</div> : null}
          <label className="admin-field">
            <span>username</span>
            <input value={username} onChange={(e) => setUsername(e.target.value)} required />
          </label>
          <label className="admin-field">
            <span>{mode === 'create' ? 'password *' : 'password mới (để trống = giữ nguyên)'}</span>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="new-password"
              required={mode === 'create'}
            />
          </label>
          <label className="admin-field">
            <span>email</span>
            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
          </label>
          <label className="admin-field">
            <span>role</span>
            <select value={role} onChange={(e) => setRole(e.target.value)}>
              {ROLES.map((r) => (
                <option key={r} value={r}>
                  {r}
                </option>
              ))}
            </select>
          </label>
          <label className="admin-field">
            <span>fullName</span>
            <input value={fullName} onChange={(e) => setFullName(e.target.value)} />
          </label>
          <label className="admin-field">
            <span>phoneNumber</span>
            <input value={phoneNumber} onChange={(e) => setPhoneNumber(e.target.value)} />
          </label>
          <label className="admin-field">
            <span>avatarUrl</span>
            <input value={avatarUrl} onChange={(e) => setAvatarUrl(e.target.value)} />
          </label>
          <label className="admin-field admin-field-inline">
            <input type="checkbox" checked={isActive} onChange={(e) => setIsActive(e.target.checked)} />
            <span>isActive</span>
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
