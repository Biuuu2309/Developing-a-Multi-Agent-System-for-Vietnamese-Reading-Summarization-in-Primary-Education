const ADMIN_AUTH_KEY = 'admin_auth';

export function isAdminAuthenticated() {
  return localStorage.getItem(ADMIN_AUTH_KEY) === 'true';
}

export function loginAdmin({ username, password }) {
  if (username === 'admin' && password === 'admin') {
    localStorage.setItem(ADMIN_AUTH_KEY, 'true');
    localStorage.setItem('admin_user', JSON.stringify({ username: 'admin' }));
    return { username: 'admin' };
  }
  throw new Error('Sai tài khoản admin hoặc mật khẩu');
}

export function logoutAdmin() {
  localStorage.removeItem(ADMIN_AUTH_KEY);
  localStorage.removeItem('admin_user');
}

