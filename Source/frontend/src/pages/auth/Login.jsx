import { useState } from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import { Loader2, AlertCircle, LogIn } from 'lucide-react';
import { login } from '../../services/authService';
import { handleAPIError } from '../../services/errorHandler';
import { GravityStarsBackground } from '../../components/animate-ui/components/backgrounds/gravity-stars';
import './auth.css';

export default function Login() {
  const navigate = useNavigate();
  const location = useLocation();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await login({ username, password });
      const from = location.state?.from?.pathname || new URLSearchParams(location.search).get('from') || '/';
      navigate(from, { replace: true });
    } catch (err) {
      const u = handleAPIError(err);
      setError(u.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <GravityStarsBackground
        className="auth-page-bg"
        starsCount={80}
        starsSize={3}
        starsOpacity={0.7}
        glowIntensity={15}
        movementSpeed={0.3}
      />
      <div className="auth-card">
        <h1 className="auth-title">
          <LogIn size={28} />
          Đăng nhập
        </h1>
        <form onSubmit={handleSubmit} className="auth-form">
          <div className="auth-field">
            <label htmlFor="login-username">Tên đăng nhập</label>
            <input
              id="login-username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Nhập tên đăng nhập"
              autoComplete="username"
              disabled={loading}
            />
          </div>
          <div className="auth-field">
            <label htmlFor="login-password">Mật khẩu</label>
            <input
              id="login-password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Nhập mật khẩu"
              autoComplete="current-password"
              disabled={loading}
            />
          </div>
          {error && (
            <div className="auth-error">
              <AlertCircle size={18} />
              <span>{error}</span>
            </div>
          )}
          <button type="submit" className="auth-submit" disabled={loading}>
            {loading ? (
              <>
                <Loader2 size={18} className="spinning" />
                <span>Đang đăng nhập...</span>
              </>
            ) : (
              'Đăng nhập'
            )}
          </button>
        </form>
        <p className="auth-footer">
          Chưa có tài khoản? <Link to="/register">Đăng ký</Link>
        </p>
      </div>
    </div>
  );
}
