import './summary.css';
import { GravityStarsBackground } from '../../components/animate-ui/components/backgrounds/gravity-stars';
import { AuroraTextEffect } from "../../components/lightswind/aurora-text-effect";
import { RippleButton, RippleButtonRipples } from '../../components/animate-ui/components/buttons/ripple';
import { MorphingNavigation } from "../../components/lightswind/morphing-navigation.tsx";
import { Home as HomeIcon, BookOpen, BookText, Zap, MessageSquare, Settings, Menu } from "lucide-react";
import { useEffect, useState, useCallback, useMemo, useRef } from "react";
import { useNavigate, Link } from "react-router-dom";
import NormalMode from './components/NormalMode';
import ChatboxMode from './components/ChatboxMode';
import Sidebar from './components/Sidebar';
import { getStoredUser, logout } from '../../services/authService';
import { User as UserIcon, LogOut, Bell } from 'lucide-react';
import { getCurrentUserId } from '../../services/sessionService';
import { createSummarySession, getSessionsByUser, deleteSummarySession } from '../../services/summarySessionApi';
import { getHistoriesBySession } from '../../services/summaryHistoryApi';

export default function Summary() {
  const navigate = useNavigate();
  const [mode, setMode] = useState('normal');
  const [currentUser, setCurrentUser] = useState(() => getStoredUser());
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);
  const [isHistoryOpen, setIsHistoryOpen] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(() => {
    try {
      return localStorage.getItem('summary_sidebar_collapsed') === '1';
    } catch { return false; }
  });
  const [chatSessions, setChatSessions] = useState([]);
  const [activeChatSession, setActiveChatSession] = useState(null);
  const [sessionMessages, setSessionMessages] = useState(null);
  const [activityHistory, setActivityHistory] = useState([]);
  const [tempSessionId, setTempSessionId] = useState(null); // auto-delete if unused
  const loadSessionsSeqRef = useRef(0);
  const deletingSessionIdsRef = useRef(new Set());

  useEffect(() => {
    localStorage.setItem('summary_sidebar_collapsed', sidebarCollapsed ? '1' : '0');
  }, [sidebarCollapsed]);

  useEffect(() => {
    const onStorage = () => setCurrentUser(getStoredUser());
    window.addEventListener('storage', onStorage);
    return () => window.removeEventListener('storage', onStorage);
  }, []);

  const handleLogout = useCallback(() => {
    logout();
    setCurrentUser(null);
    setIsUserMenuOpen(false);
  }, []);

  // Handle navigation link clicks
  const handleLinkClick = useCallback((link) => {
    if (link.id === 'home') {
      navigate('/');
    } else if (link.id === 'summary') {
      navigate('/summary');
    } else if (link.id === 'story') {
      navigate('/story');
    } else if (link.id === 'mas-flow') {
      navigate('/mas-flow');
    }
    // Other links will use default scroll behavior handled by MorphingNavigation
  }, [navigate]);

  // Load activity history (read-only) on mount
  useEffect(() => {
    const saved = localStorage.getItem('summary_sessions');
    if (saved) {
      try {
        setActivityHistory(JSON.parse(saved));
      } catch (e) {
        console.error('Failed to load activity history:', e);
      }
    }
  }, []);

  const pushActivity = useCallback((event) => {
    const item = { id: Date.now().toString(), timestamp: new Date().toISOString(), ...event };
    const next = [item, ...activityHistory].slice(0, 50);
    setActivityHistory(next);
    localStorage.setItem('summary_sessions', JSON.stringify(next));
  }, [activityHistory]);

  const loadSessions = useCallback(async () => {
    const userId = getCurrentUserId();
    const seq = ++loadSessionsSeqRef.current;
    try {
      const list = await getSessionsByUser(userId);
      if (seq === loadSessionsSeqRef.current) setChatSessions(list);
    } catch (e) {
      console.error('Load summary sessions:', e);
    }
  }, []);

  useEffect(() => {
    loadSessions();
  }, [loadSessions]);

  const handleSelectChatSession = useCallback(async (session) => {
    // If current active temp session unused, delete it
    if (tempSessionId && activeChatSession?.sessionId === tempSessionId) {
      try {
        await deleteSummarySession(tempSessionId);
        setChatSessions((prev) => prev.filter((s) => s.sessionId !== tempSessionId));
      } catch (e) {
        console.warn('Auto delete temp session failed:', e);
      } finally {
        setTempSessionId(null);
      }
    }

    setMode('chatbox');
    setIsSidebarOpen(false);
    try {
      const histories = await getHistoriesBySession(session.sessionId);
      const built = [];
      let lastConvId = null;
      let lastMasId = null;
      histories.forEach((h) => {
        if (h.userInput) built.push({ id: `u-${h.historyId}`, role: 'user', content: h.userInput });
        built.push({
          id: `a-${h.historyId}`,
          role: 'assistant',
          content: h.summaryContent || '',
          result: (h.summaryContent || h.summaryImageUrl) ? { summary: h.summaryContent, summaryImageUrl: h.summaryImageUrl, evaluation: h.evaluation } : null,
        });
        if (h.conversationId) lastConvId = h.conversationId;
        if (h.masSessionId) lastMasId = h.masSessionId;
      });
      setSessionMessages(built.length ? built : null);
      setActiveChatSession({ ...session, conversationId: lastConvId ?? session.conversationId, masSessionId: lastMasId ?? session.masSessionId });
    } catch {
      setSessionMessages(null);
      setActiveChatSession(session);
    }
  }, []);

  const handleNewChatSession = useCallback(async () => {
    const userId = getCurrentUserId();
    try {
      const created = await createSummarySession({ userId, content: '' });
      const session = {
        sessionId: created.sessionId,
        content: created.content,
        timestamp: created.timestamp,
        createdBy: created.createdBy,
      };
      setChatSessions((prev) => [session, ...prev]);
      setActiveChatSession(session);
      setSessionMessages(null);
      setMode('chatbox');
      setIsSidebarOpen(false);
      setTempSessionId(created.sessionId); // created via sidebar button => temporary until first action
    } catch (e) {
      console.error('Create summary session:', e);
    }
  }, []);

  const handleDeleteChatSession = useCallback(async (summarySessionId) => {
    const idNum = Number(summarySessionId);
    const idKey = String(idNum);
    if (deletingSessionIdsRef.current.has(idKey)) return;
    deletingSessionIdsRef.current.add(idKey);

    // Optimistic UI: remove immediately, then call API
    let removed = null;
    setChatSessions((prev) => {
      removed = prev.find((s) => Number(s.sessionId) === idNum) || null;
      return prev.filter((s) => Number(s.sessionId) !== idNum);
    });
    if (Number(activeChatSession?.sessionId) === idNum) {
      setActiveChatSession(null);
      setSessionMessages(null);
    }
    if (Number(tempSessionId) === idNum) setTempSessionId(null);

    try {
      await deleteSummarySession(idNum);
      loadSessions();
    } catch (e) {
      // Restore if API failed (e.g. FK constraints)
      if (removed) {
        setChatSessions((prev) => [removed, ...prev]);
      }
      console.error('Delete summary session:', e);
    } finally {
      deletingSessionIdsRef.current.delete(idKey);
    }
  }, [activeChatSession?.sessionId, tempSessionId, loadSessions]);

  const handleNormalSubmit = useCallback((data) => {
    if (data?.kind === 'session_created') {
      const session = { sessionId: data.summarySessionId, content: '', timestamp: new Date().toString() };
      setChatSessions((prev) => [session, ...prev]);
      setActiveChatSession(session);
      if (data.source === 'sidebar_new') setTempSessionId(data.summarySessionId);
      loadSessions();
      return;
    }
    pushActivity({
      type: 'normal_summary',
      summaryType: data.summaryType,
      gradeLevel: data.gradeLevel,
      text: data.text,
      result: data.result,
      sessionId: data.sessionId,
      summarySessionId: data.summarySessionId,
    });
    if (data.summarySessionId && tempSessionId === data.summarySessionId) setTempSessionId(null);
    loadSessions();
  }, [pushActivity, loadSessions, tempSessionId]);

  const handleChatboxSubmit = useCallback((data) => {
    if (data?.kind === 'session_created') {
      const session = { sessionId: data.summarySessionId, content: '', timestamp: new Date().toString() };
      setChatSessions((prev) => [session, ...prev]);
      setActiveChatSession(session);
      if (data.source === 'sidebar_new') setTempSessionId(data.summarySessionId);
      loadSessions();
      return;
    }
    if (data?.kind && data.kind !== 'message') return;

    pushActivity({ type: 'chat_message', text: data.message, summarySessionId: data.summarySessionId });
    if (data.conversationId != null || data.masSessionId != null) {
      setActiveChatSession((prev) => (prev ? { ...prev, conversationId: data.conversationId ?? prev.conversationId, masSessionId: data.masSessionId ?? prev.masSessionId } : prev));
    }
    setSessionMessages(data.messages ?? null);
    loadSessions();
    // Once user sends first message, temp session becomes permanent
    if (tempSessionId && data.summarySessionId === tempSessionId) setTempSessionId(null);
  }, [pushActivity, loadSessions]);

  // Auto-delete temp session when switching away from chatbox
  useEffect(() => {
    if (mode === 'chatbox') return;
    if (!tempSessionId) return;
    (async () => {
      const idNum = Number(tempSessionId);
      const idKey = String(idNum);
      if (deletingSessionIdsRef.current.has(idKey)) return;
      deletingSessionIdsRef.current.add(idKey);
      // Optimistic remove
      setChatSessions((prev) => prev.filter((s) => Number(s.sessionId) !== idNum));
      if (Number(activeChatSession?.sessionId) === idNum) setActiveChatSession(null);
      try {
        await deleteSummarySession(idNum);
        loadSessions();
      } catch (e) {
        console.warn('Auto delete temp session failed:', e);
        // If failed, reload from server to show the real list
        loadSessions();
      } finally {
        setTempSessionId(null);
        deletingSessionIdsRef.current.delete(idKey);
      }
    })();
  }, [mode, tempSessionId, activeChatSession?.sessionId, loadSessions]);

  // Auto-delete temp session when leaving page
  useEffect(() => {
    return () => {
      const id = tempSessionId;
      if (!id) return;
      // fire-and-forget
      deleteSummarySession(id).catch(() => {});
    };
  }, [tempSessionId]);

  // Memoize links để tránh re-render không cần thiết
  const navLinks = useMemo(() => [
    { id: 'home', label: 'Home', href: '/', icon: <HomeIcon size={30} /> },
    { id: 'summary', label: 'Summary', href: '/summary', icon: <BookOpen size={30} /> },
    { id: 'story', label: 'Story', href: '/story', icon: <BookText size={30} /> },
    { id: 'mas-flow', label: 'MAS Flow', href: '/mas-flow', icon: <Zap size={30} /> }
  ], []);

  return (
    <div style={{ width: '100%', minHeight: '100vh', position: 'relative' }}>
      <GravityStarsBackground 
        className="gravity-stars-bg"
        starsCount={100}
        starsSize={4}
        starsOpacity={0.8}
        glowIntensity={20}
        movementSpeed={0.4}
        mouseInfluence={150}
        mouseGravity="attract"
        gravityStrength={100}
      />
      <MorphingNavigation
        links={navLinks}
        theme="custom"
        backgroundColor="#ffffff00"
        textColor="#0000ff"
        borderColor="rgba(59, 130, 246, 0.9)"
        onLinkClick={handleLinkClick}
        scrollThreshold={150}
        animationDuration={1.5}
        enablePageBlur={true}
        glowIntensity={5}
        onMenuToggle={(isOpen) => console.log('Menu:', isOpen)}
      />
      <div
        className="buttonNavigation"
        style={{
          display: 'flex',
          flexDirection: 'row',
          alignItems: 'center',
          justifyContent: 'space-between',
          marginRight: '10px',
          marginTop: '20px',
          gap: '0.75rem',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginLeft: '20px' }}>
        <img src="/images/logo.png" alt="" style={{ width: '80px', height: '80px' }} />
          <AuroraTextEffect
            text="VUSUMMARY"
            fontSize="clamp(3rem, 5vw, 3rem)"
            colors={{
              first: "bg-cyan-400",
              second: "bg-yellow-400",
              third: "bg-green-400",
              fourth: "bg-purple-500"
            }}
            blurAmount="blur-lg"
            className="aurora-text-effect ml-3"
          />
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginRight: '20px', position: 'relative' }}>
        {currentUser ? (
          <>
            {/* Activity history bell (read-only) */}
            <button
              type="button"
              onClick={() => setIsHistoryOpen((v) => !v)}
              style={{
                width: '44px',
                height: '44px',
                borderRadius: '12px',
                background: 'rgba(255,255,255,0.95)',
                border: '1px solid rgba(0,0,0,0.1)',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                backdropFilter: 'blur(10px)',
              }}
              title="Lịch sử hoạt động"
            >
              <Bell size={18} />
            </button>

            {isHistoryOpen && (
              <div
                style={{
                  position: 'absolute',
                  top: '52px',
                  right: '250px',
                  width: '320px',
                  maxHeight: '420px',
                  overflowY: 'auto',
                  background: 'rgba(255,255,255,0.98)',
                  border: '1px solid rgba(0,0,0,0.08)',
                  borderRadius: '12px',
                  boxShadow: '0 12px 24px rgba(0,0,0,0.12)',
                  padding: '10px',
                  zIndex: 1200,
                }}
              >
                <div style={{ fontSize: '12px', color: '#6B7280', fontWeight: 600, marginBottom: '8px' }}>Lịch sử hoạt động</div>
                {activityHistory.length === 0 ? (
                  <div style={{ fontSize: '13px', color: '#9CA3AF', padding: '10px' }}>Chưa có lịch sử.</div>
                ) : (
                  activityHistory.slice(0, 20).map((h) => (
                    <div key={h.id} style={{ padding: '10px', borderRadius: '10px', border: '1px solid #E5E7EB', background: '#fff', marginBottom: '8px' }}>
                      <div style={{ fontSize: '12px', color: '#6B7280' }}>{new Date(h.timestamp).toLocaleString('vi-VN')}</div>
                      <div style={{ fontSize: '13px', fontWeight: 600, color: '#374151', marginTop: '4px' }}>
                        {h.type === 'normal_summary' ? 'Tóm tắt (Normal)' : 'Chat message'}
                      </div>
                      {h.text && <div style={{ fontSize: '13px', color: '#6B7280', marginTop: '4px' }}>{String(h.text).slice(0, 80)}{String(h.text).length > 80 ? '...' : ''}</div>}
                    </div>
                  ))
                )}
              </div>
            )}

            <button
              type="button"
              onClick={() => setIsUserMenuOpen((v) => !v)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '10px',
                padding: '8px 12px',
                background: 'rgba(255,255,255,0.95)',
                border: '1px solid rgba(0,0,0,0.1)',
                borderRadius: '12px',
                cursor: 'pointer',
                backdropFilter: 'blur(10px)',
              }}
              title={currentUser.role || 'User'}
            >
              {currentUser.avatarUrl ? (
                <img
                  src={currentUser.avatarUrl}
                  alt=""
                  style={{ width: '28px', height: '28px', borderRadius: '999px', objectFit: 'cover' }}
                />
              ) : (
                <div style={{ width: '28px', height: '28px', borderRadius: '999px', background: '#E5E7EB', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <UserIcon size={16} />
                </div>
              )}
              <span style={{ fontWeight: 600, color: '#374151', fontSize: '14px' }}>{currentUser.username}</span>
            </button>

            {isUserMenuOpen && (
              <div
                style={{
                  position: 'absolute',
                  top: '48px',
                  right: 0,
                  width: '220px',
                  background: 'rgba(255,255,255,0.98)',
                  border: '1px solid rgba(0,0,0,0.08)',
                  borderRadius: '12px',
                  boxShadow: '0 12px 24px rgba(0,0,0,0.12)',
                  padding: '8px',
                  zIndex: 1100,
                }}
              >
                <div style={{ padding: '8px 10px', color: '#6B7280', fontSize: '12px' }}>
                  Role: <b style={{ color: '#374151' }}>{currentUser.role || 'CHILD'}</b>
                </div>
                <button
                  type="button"
                  onClick={handleLogout}
                  style={{
                    width: '100%',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '10px',
                    padding: '10px',
                    border: 'none',
                    background: 'transparent',
                    borderRadius: '10px',
                    cursor: 'pointer',
                    color: '#EF4444',
                    fontWeight: 600,
                  }}
                >
                  <LogOut size={16} />
                  Đăng xuất
                </button>
              </div>
            )}
          </>
        ) : (
          <>
            <Link to="/login">
              <RippleButton variant="outline" size="lg" style={{ borderRadius: '10px', height: '40px' }}>
                Login
                <RippleButtonRipples />
              </RippleButton>
            </Link>
            <Link to="/register">
              <RippleButton variant="default" size="lg" style={{ borderRadius: '10px', height: '40px', opacity: '0.8' }}>
                Register
                <RippleButtonRipples />
              </RippleButton>
            </Link>
          </>
        )}
        </div>
      </div>

      {/* Left Sidebar - ChatGPT style */}
      <Sidebar
        sessions={chatSessions}
        selectedSessionId={activeChatSession?.sessionId}
        onSelectSession={handleSelectChatSession}
        onDeleteSession={handleDeleteChatSession}
        onNewSession={handleNewChatSession}
        onCollapse={() => setSidebarCollapsed((c) => !c)}
        collapsed={sidebarCollapsed}
        onClose={() => setIsSidebarOpen(false)}
        isOpen={isSidebarOpen}
      />

      <div
        className={`summary-main-wrap ${sidebarCollapsed ? 'sidebar-collapsed' : ''}`}
        style={{ marginLeft: sidebarCollapsed ? '72px' : '280px' }}
      >
      {/* Mobile: menu button to open sidebar */}
      <button
        type="button"
        className="summary-sidebar-toggle"
        onClick={() => setIsSidebarOpen(true)}
        aria-label="Mở danh sách phiên"
      >
        <Menu size={22} />
      </button>

      {/* Button Group - Bottom Right */}
      <div className="summary-bottom-actions">
        {/* Mode Toggle Button */}
        <button
          onClick={() => setMode(mode === 'normal' ? 'chatbox' : 'normal')}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            padding: '12px 20px',
            backgroundColor: 'rgba(255, 255, 255, 0.95)',
            backdropFilter: 'blur(10px)',
            border: '1px solid rgba(0, 0, 0, 0.1)',
            borderRadius: '12px',
            cursor: 'pointer',
            fontSize: '14px',
            fontWeight: 600,
            color: '#374151',
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
            transition: 'all 0.2s ease',
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.backgroundColor = '#F3F4F6';
            e.currentTarget.style.transform = 'translateY(-2px)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.backgroundColor = 'rgba(255, 255, 255, 0.95)';
            e.currentTarget.style.transform = 'translateY(0)';
          }}
          title={mode === 'normal' ? 'Chuyển sang chế độ Chatbox' : 'Chuyển sang chế độ Normal'}
        >
          {mode === 'normal' ? (
            <>
              <MessageSquare size={18} />
              <span>Chatbox</span>
            </>
          ) : (
            <>
              <Settings size={18} />
              <span>Normal</span>
            </>
          )}
        </button>
      </div>

      {/* Content Area */}
      <div
        className="summary-content-area"
        style={{
          padding: '2rem',
          paddingTop: '120px',
          minHeight: '100vh',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'flex-start',
        }}
      >
        {mode === 'normal' ? (
          <NormalMode
            onSubmit={handleNormalSubmit}
            initialData={null}
            summarySessionId={activeChatSession?.sessionId ?? null}
          />
        ) : (
          <ChatboxMode
            summarySessionId={activeChatSession?.sessionId ?? null}
            onSubmit={handleChatboxSubmit}
            initialData={
              activeChatSession?.sessionId
                ? {
                    messages: sessionMessages ?? undefined,
                    conversationId: activeChatSession.conversationId ?? null,
                    masSessionId: activeChatSession.masSessionId ?? null,
                  }
                : null
            }
          />
        )}
      </div>
      </div>
    </div>
  );
}
