import { apiPost } from './api';
import { APIError } from './errorHandler';

const USER_STORAGE_KEY = 'auth_user';

export function getStoredUser() {
  try {
    const raw = localStorage.getItem(USER_STORAGE_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

export function setStoredUser(user) {
  if (user) {
    localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(user));
    localStorage.setItem('user_id', user.userId);
  } else {
    localStorage.removeItem(USER_STORAGE_KEY);
    localStorage.removeItem('user_id');
  }
}

export async function login(credentials) {
  const { username, password } = credentials;
  if (!username?.trim() || !password) {
    throw new APIError('Vui lòng nhập tên đăng nhập và mật khẩu', 400, null);
  }
  try {
    const data = await apiPost('/api/users/auth/login', { username: username.trim(), password });
    setStoredUser(data);
    return data;
  } catch (err) {
    if (err.status === 401) {
      throw new APIError('Sai tên đăng nhập hoặc mật khẩu', 401, null);
    }
    throw err;
  }
}

export async function register(userData) {
  const { username, password, email, fullName, role } = userData;
  if (!username?.trim() || !password || !email?.trim()) {
    throw new APIError('Vui lòng điền tên đăng nhập, mật khẩu và email', 400, null);
  }
  const payload = {
    username: username.trim(),
    password,
    email: email.trim(),
    role: role || 'CHILD',
    fullName: fullName?.trim() || null,
  };
  const data = await apiPost('/api/users', payload);
  return data;
}

export function logout() {
  setStoredUser(null);
}
