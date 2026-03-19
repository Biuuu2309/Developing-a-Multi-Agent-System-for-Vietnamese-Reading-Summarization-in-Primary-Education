import { Navigate, Outlet } from 'react-router-dom';
import { isAdminAuthenticated } from '../../services/adminAuth';

export default function AdminRouteGuard() {
  const authed = isAdminAuthenticated();
  if (!authed) return <Navigate to="/admin/login" replace />;
  return <Outlet />;
}

