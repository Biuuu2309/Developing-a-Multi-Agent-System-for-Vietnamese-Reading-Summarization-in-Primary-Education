import './summary.css';
import { GravityStarsBackground } from '../../components/animate-ui/components/backgrounds/gravity-stars';
import { AuroraTextEffect } from "../../components/lightswind/aurora-text-effect";
import { RippleButton, RippleButtonRipples } from '../../components/animate-ui/components/buttons/ripple';
import { MorphingNavigation } from "../../components/lightswind/morphing-navigation.tsx";
import { Home as HomeIcon, History, BookOpen, BookText, Zap, MessageSquare, Settings } from "lucide-react";
import { useEffect, useState, useCallback, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import NormalMode from './components/NormalMode';
import ChatboxMode from './components/ChatboxMode';

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
        className="fixed-logo Logo"
        style={{
          display: 'flex',
          flexDirection: 'row',
          alignItems: 'center',
          justifyContent: 'center',
          opacity: isLogoHidden ? 0 : 1,
          transition: 'opacity 0.3s ease-in-out',
          pointerEvents: isLogoHidden ? 'none' : 'auto',
        }}
      >
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
      <div
        className="buttonNavigation"
        style={{
          display: 'flex',
          flexDirection: 'row',
          alignItems: 'center',
          justifyContent: 'flex-end',
          marginRight: '10px',
          marginTop: '30px',
          gap: '0.75rem',
        }}
      >
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
  );
}
