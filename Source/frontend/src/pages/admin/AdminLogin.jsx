import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { LogIn, AlertCircle } from 'lucide-react';
import './Admin.css';
import { loginAdmin } from '../../services/adminAuth';

export default function AdminLogin() {
  const navigate = useNavigate();
  const [username, setUsername] = useState('admin');
  const [password, setPassword] = useState('admin');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await new Promise((r) => setTimeout(r, 300)); // keep UI responsive
      loginAdmin({ username: username.trim(), password });
      navigate('/admin', { replace: true });
    } catch (err) {
      setError(err?.message || 'Đăng nhập admin thất bại');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="admin-auth-page">
      <div className="admin-auth-card">
        <h1 className="admin-auth-title">
          <LogIn size={26} />
          Admin Login
        </h1>

        <form onSubmit={handleSubmit} className="admin-auth-form">
          <div className="admin-auth-field">
            <label htmlFor="admin-username">Username</label>
            <input
              id="admin-username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="admin"
              autoComplete="username"
              disabled={loading}
            />
          </div>

          <div className="admin-auth-field">
            <label htmlFor="admin-password">Password</label>
            <input
              id="admin-password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="admin"
              autoComplete="current-password"
              disabled={loading}
            />
          </div>

          {error ? (
            <div className="admin-auth-error">
              <AlertCircle size={18} />
              <span>{error}</span>
            </div>
          ) : null}

          <button type="submit" className="admin-auth-submit" disabled={loading}>
            {loading ? 'Đang đăng nhập...' : 'Đăng nhập'}
          </button>

          <div className="admin-auth-note">Tạm thời: username = admin, password = admin</div>
        </form>
      </div>
    </div>
  );
}

