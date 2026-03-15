import './summary.css';
import { GravityStarsBackground } from '../../components/animate-ui/components/backgrounds/gravity-stars';
import { AuroraTextEffect } from "../../components/lightswind/aurora-text-effect";
import { RippleButton, RippleButtonRipples } from '../../components/animate-ui/components/buttons/ripple';
import { MorphingNavigation } from "../../components/lightswind/morphing-navigation.tsx";
import { Home as HomeIcon, History, BookOpen, BookText, Zap, MessageSquare, Settings, Menu } from "lucide-react";
import { useEffect, useState, useCallback, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import NormalMode from './components/NormalMode';
import ChatboxMode from './components/ChatboxMode';
import Sidebar from './components/Sidebar';

function throttle(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

export default function Summary() {
  const navigate = useNavigate();
  const [isLogoHidden, setIsLogoHidden] = useState(false);
  const [mode, setMode] = useState('normal'); // 'normal' or 'chatbox'
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [sessions, setSessions] = useState([]);

  const handleScroll = useCallback(() => {
    setIsLogoHidden(window.scrollY > 50);
  }, []);

  useEffect(() => {
    const throttledScroll = throttle(handleScroll, 16);
    window.addEventListener('scroll', throttledScroll, { passive: true });
    handleScroll();
    return () => window.removeEventListener('scroll', throttledScroll);
  }, [handleScroll]);

  // Handle navigation link clicks
  const handleLinkClick = useCallback((link) => {
    if (link.id === 'home') {
      navigate('/');
    } else if (link.id === 'summary') {
      navigate('/summary');
    } else if (link.id === 'mas-flow') {
      navigate('/mas-flow');
    }
    // Other links will use default scroll behavior handled by MorphingNavigation
  }, [navigate]);

  // Load sessions from localStorage on mount
  useEffect(() => {
    const savedSessions = localStorage.getItem('summary_sessions');
    if (savedSessions) {
      try {
        const parsed = JSON.parse(savedSessions);
        setSessions(parsed);
      } catch (e) {
        console.error('Failed to load sessions:', e);
      }
    }
  }, []);

  // Save session to localStorage
  const saveSession = useCallback((sessionData) => {
    const newSession = {
      id: Date.now().toString(),
      ...sessionData,
      timestamp: new Date().toISOString(),
      createdAt: new Date().toISOString(),
    };

    const updatedSessions = [newSession, ...sessions];
    setSessions(updatedSessions);
    localStorage.setItem('summary_sessions', JSON.stringify(updatedSessions));
  }, [sessions]);

  // Delete session
  const handleDeleteSession = useCallback((sessionId) => {
    const updated = sessions.filter((s) => s.id !== sessionId);
    setSessions(updated);
    localStorage.setItem('summary_sessions', JSON.stringify(updated));
  }, [sessions]);

  // Select session to load
  const handleSelectSession = useCallback((session) => {
    if (session.mode) {
      setMode(session.mode);
    }
    setIsSidebarOpen(false); // Close sidebar after selection
    // TODO: Load session data into form/chatbox
  }, []);

  // Handle normal mode submit
  const handleNormalSubmit = useCallback((data) => {
    console.log('Normal mode submit:', data);
    saveSession({
      mode: 'normal',
      summaryType: data.summaryType,
      gradeLevel: data.gradeLevel,
      text: data.text,
    });
    // TODO: Call API to process summary
  }, [saveSession]);

  // Handle chatbox mode submit
  const handleChatboxSubmit = useCallback((data) => {
    console.log('Chatbox mode submit:', data);
    saveSession({
      mode: 'chatbox',
      messages: data.messages,
      text: data.message,
    });
    // TODO: Call API to process chat
  }, [saveSession]);

  // Memoize links để tránh re-render không cần thiết
  const navLinks = useMemo(() => [
    { id: 'home', label: 'Home', href: '/', icon: <HomeIcon size={30} /> },
    { id: 'summary', label: 'Summary', href: '/summary', icon: <BookOpen size={30} /> },
    { id: 'story', label: 'Story', href: '#story', icon: <BookText size={30} /> },
    { id: 'history', label: 'History', href: '#history', icon: <History size={30} /> },
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
          marginTop: '30px',
          gap: '0.75rem',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
        <img src="/images/logo.png" alt="" style={{ width: '100px', height: '100px' }} />
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
        <div>
        <RippleButton variant="outline" size="lg" style={{ borderRadius: '10px', height: '40px' }}>
          Login
          <RippleButtonRipples />
        </RippleButton>
        <RippleButton variant="default" size="lg" style={{ borderRadius: '10px', height: '40px', opacity: '0.8' }}>
          Register
          <RippleButtonRipples />
        </RippleButton>
        </div>
      </div>

      {/* Sidebar Toggle Button */}
      <button
        onClick={() => setIsSidebarOpen(!isSidebarOpen)}
        style={{
          position: 'fixed',
          top: '24px',
          left: '24px',
          zIndex: 1001,
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
          marginTop: '100px',
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.backgroundColor = '#F3F4F6';
          e.currentTarget.style.transform = 'translateY(-2px)';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.backgroundColor = 'rgba(255, 255, 255, 0.95)';
          e.currentTarget.style.transform = 'translateY(0)';
        }}
        title="Mở lịch sử"
      >
        <Menu size={18} />
        <span>Lịch sử</span>
      </button>

      {/* Sidebar */}
      <Sidebar
        isOpen={isSidebarOpen}
        onClose={() => setIsSidebarOpen(false)}
        sessions={sessions}
        onSelectSession={handleSelectSession}
        onDeleteSession={handleDeleteSession}
      />

      {/* Mode Toggle Button */}
      <button
        onClick={() => setMode(mode === 'normal' ? 'chatbox' : 'normal')}
        style={{
          position: 'fixed',
          bottom: '24px',
          right: '24px',
          zIndex: 1000,
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

      {/* Content Area */}
      <div
        style={{
          padding: '2rem',
          paddingTop: '120px',
          minHeight: '100vh',
          display: 'flex',
          justifyContent: 'center',
          alignItems: mode === 'chatbox' ? 'flex-start' : 'flex-start',
        }}
      >
        {mode === 'normal' ? (
          <NormalMode
            onSubmit={handleNormalSubmit}
          />
        ) : (
          <ChatboxMode
            onSubmit={handleChatboxSubmit}
          />
        )}
      </div>
    </div>
  );
}
