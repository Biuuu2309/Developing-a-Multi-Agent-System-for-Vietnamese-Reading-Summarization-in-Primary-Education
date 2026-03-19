import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Home from './pages/home/Home.jsx';
import Summary from './pages/summary/summary.jsx';
import MASFlowPage from './pages/mas-flow/MASFlowPage.jsx';
import Login from './pages/auth/Login.jsx';
import Register from './pages/auth/Register.jsx';
import Story from './pages/story/Story.jsx';
import AdminLogin from './pages/admin/AdminLogin.jsx';
import AdminLayout from './pages/admin/AdminLayout.jsx';
import AdminRouteGuard from './pages/admin/AdminRouteGuard.jsx';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/summary" element={<Summary />} />
        <Route path="/story" element={<Story />} />
        <Route path="/mas-flow" element={<MASFlowPage />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/admin/login" element={<AdminLogin />} />
        <Route element={<AdminRouteGuard />}>
          <Route path="/admin" element={<AdminLayout />} />
          <Route path="/admin/:table" element={<AdminLayout />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
