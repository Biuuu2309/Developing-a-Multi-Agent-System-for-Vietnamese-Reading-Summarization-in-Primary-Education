import { useEffect, useMemo } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { logoutAdmin } from '../../services/adminAuth';
import AdminUsers from './AdminUsers.jsx';
import AdminSummaries from './AdminSummaries.jsx';
import AdminSummarySessions from './AdminSummarySessions.jsx';
import AdminSummaryHistory from './AdminSummaryHistory.jsx';
import AdminReadHistory from './AdminReadHistory.jsx';
import AdminConversations from './AdminConversations.jsx';
import AdminAgents from './AdminAgents.jsx';
import AdminMasSessions from './AdminMasSessions.jsx';
import AdminMasStates from './AdminMasStates.jsx';
import AdminMessages from './AdminMessages.jsx';
import AdminAgentLogs from './AdminAgentLogs.jsx';
import AdminMasPlans from './AdminMasPlans.jsx';
import AdminMasEvaluations from './AdminMasEvaluations.jsx';
import AdminMasGoals from './AdminMasGoals.jsx';
import AdminMasAgentMemories from './AdminMasAgentMemories.jsx';
import AdminMasNegotiations from './AdminMasNegotiations.jsx';
import AdminMasAgentConfidences from './AdminMasAgentConfidences.jsx';
import './Admin.css';

const ADMIN_TABLES = [
  { id: 'users', label: 'users' },
  { id: 'summaries', label: 'summaries' },
  { id: 'summary_sessions', label: 'summary_sessions' },
  { id: 'summary_history', label: 'summary_history' },
  { id: 'read_history', label: 'read_history' },
  { id: 'conversations', label: 'conversations' },
  { id: 'agents', label: 'agents' },
  { id: 'mas_sessions', label: 'mas_sessions' },
  { id: 'mas_states', label: 'mas_states (read-only)' },
  { id: 'messages', label: 'messages' },
  { id: 'agent_logs', label: 'agent_logs' },
  { id: 'mas_plans', label: 'mas_plans (via mas_states)' },
  { id: 'mas_evaluations', label: 'mas_evaluations (via mas_states)' },
  { id: 'mas_goals', label: 'mas_goals (via mas_states)' },
  { id: 'mas_agent_memories', label: 'mas_agent_memories (via mas_states)' },
  { id: 'mas_negotiations', label: 'mas_negotiations (via mas_states)' },
  { id: 'mas_agent_confidences', label: 'mas_agent_confidences (via mas_states)' },
];

export default function AdminLayout() {
  const navigate = useNavigate();
  const params = useParams();
  const tableId = params.table || ADMIN_TABLES[0].id;

  const selected = useMemo(() => ADMIN_TABLES.find((t) => t.id === tableId) || ADMIN_TABLES[0], [tableId]);

  useEffect(() => {
    if (!params.table) navigate(`/admin/${ADMIN_TABLES[0].id}`, { replace: true });
  }, [navigate, params.table]);

  const handleLogout = () => {
    logoutAdmin();
    navigate('/admin/login', { replace: true });
  };

  return (
    <div className="admin-layout">
      <aside className="admin-sidebar">
        <div className="admin-sidebar-title">Admin</div>
        <div className="admin-sidebar-sub">Tables</div>
        <nav className="admin-nav">
          {ADMIN_TABLES.map((t) => (
            <button
              key={t.id}
              type="button"
              className={`admin-nav-item ${t.id === selected.id ? 'active' : ''}`}
              onClick={() => navigate(`/admin/${t.id}`)}
            >
              {t.label}
            </button>
          ))}
        </nav>
      </aside>

      <main className="admin-content">
        <header className="admin-content-head">
          <div>
            <div className="admin-content-title">Admin CRUD</div>
            <div className="admin-content-sub">Bảng đang chọn: {selected.label}</div>
          </div>
          <button type="button" className="admin-logout-btn" onClick={handleLogout}>
            Logout
          </button>
        </header>

        {selected.id === 'users' ? (
          <AdminUsers />
        ) : selected.id === 'summaries' ? (
          <AdminSummaries />
        ) : selected.id === 'summary_sessions' ? (
          <AdminSummarySessions />
        ) : selected.id === 'summary_history' ? (
          <AdminSummaryHistory />
        ) : selected.id === 'read_history' ? (
          <AdminReadHistory />
        ) : selected.id === 'conversations' ? (
          <AdminConversations />
        ) : selected.id === 'agents' ? (
          <AdminAgents />
        ) : selected.id === 'mas_sessions' ? (
          <AdminMasSessions />
        ) : selected.id === 'mas_states' ? (
          <AdminMasStates />
        ) : selected.id === 'messages' ? (
          <AdminMessages />
        ) : selected.id === 'agent_logs' ? (
          <AdminAgentLogs />
        ) : selected.id === 'mas_plans' ? (
          <AdminMasPlans />
        ) : selected.id === 'mas_evaluations' ? (
          <AdminMasEvaluations />
        ) : selected.id === 'mas_goals' ? (
          <AdminMasGoals />
        ) : selected.id === 'mas_agent_memories' ? (
          <AdminMasAgentMemories />
        ) : selected.id === 'mas_negotiations' ? (
          <AdminMasNegotiations />
        ) : selected.id === 'mas_agent_confidences' ? (
          <AdminMasAgentConfidences />
        ) : (
          <section className="admin-placeholder">
            <div className="admin-placeholder-title">Chưa triển khai</div>
            <div className="admin-placeholder-desc">
              Bảng này sẽ chỉ hiển thị dữ liệu hoặc CRUD tùy endpoint backend (bước tiếp theo).
            </div>
            <div className="admin-placeholder-desc">({selected.label})</div>
          </section>
        )}
      </main>
    </div>
  );
}

