import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Loader2, AlertCircle, UserPlus } from 'lucide-react';
import { register } from '../../services/authService';
import { handleAPIError } from '../../services/errorHandler';
import { GravityStarsBackground } from '../../components/animate-ui/components/backgrounds/gravity-stars';
import './auth.css';

export default function Register() {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    username: '',
    password: '',
    email: '',
    fullName: '',
    role: 'CHILD',
  });
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const update = (key, value) => setForm((f) => ({ ...f, [key]: value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await register(form);
      navigate('/login', { replace: true });
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
      <div className="auth-card auth-card-wide">
        <h1 className="auth-title">
          <UserPlus size={28} />
          Đăng ký
        </h1>
        <form onSubmit={handleSubmit} className="auth-form">
          <div className="auth-row">
            <div className="auth-field">
              <label htmlFor="reg-username">Tên đăng nhập *</label>
              <input
                id="reg-username"
                type="text"
                value={form.username}
                onChange={(e) => update('username', e.target.value)}
                placeholder="Tên đăng nhập"
                autoComplete="username"
                disabled={loading}
              />
            </div>
            <div className="auth-field">
              <label htmlFor="reg-email">Email *</label>
              <input
                id="reg-email"
                type="email"
                value={form.email}
                onChange={(e) => update('email', e.target.value)}
                placeholder="email@example.com"
                autoComplete="email"
                disabled={loading}
              />
            </div>
          </div>
          <div className="auth-field">
            <label htmlFor="reg-password">Mật khẩu *</label>
            <input
              id="reg-password"
              type="password"
              value={form.password}
              onChange={(e) => update('password', e.target.value)}
              placeholder="Mật khẩu"
              autoComplete="new-password"
              disabled={loading}
            />
          </div>
          <div className="auth-row">
            <div className="auth-field">
              <label htmlFor="reg-fullName">Họ tên</label>
              <input
                id="reg-fullName"
                type="text"
                value={form.fullName}
                onChange={(e) => update('fullName', e.target.value)}
                placeholder="Họ và tên"
                disabled={loading}
              />
            </div>
            <div className="auth-field">
              <label htmlFor="reg-role">Vai trò</label>
              <select
                id="reg-role"
                value={form.role}
                onChange={(e) => update('role', e.target.value)}
                disabled={loading}
              >
                <option value="CHILD">Học sinh</option>
                <option value="CONTRIBUTOR">Người đóng góp</option>
                <option value="ADMIN">Quản trị</option>
              </select>
            </div>
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
                <span>Đang đăng ký...</span>
              </>
            ) : (
              'Đăng ký'
            )}
          </button>
        </form>
        <p className="auth-footer">
          Đã có tài khoản? <Link to="/login">Đăng nhập</Link>
        </p>
      </div>
    </div>
  );
}
