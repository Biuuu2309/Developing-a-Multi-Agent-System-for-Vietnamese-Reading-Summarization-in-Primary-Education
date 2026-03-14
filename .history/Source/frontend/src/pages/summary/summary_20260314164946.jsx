import './summary.css';
import { GravityStarsBackground } from '../../components/animate-ui/components/backgrounds/gravity-stars';

import ParticlesBackground from '../../components/Particles';
import { MorphingNavigation } from "../../components/lightswind/morphing-navigation.tsx";
import { Home as HomeIcon, ShoppingBag, Info, HelpCircle, History, BookOpen, BookText } from "lucide-react";
import './Home.css';
import { AuroraTextEffect } from "../../components/lightswind/aurora-text-effect";
import { RippleButton, RippleButtonRipples } from '../../components/animate-ui/components/buttons/ripple';

export default function Summary() {
  return (
    <div style={{ width: '100%', minHeight: '100vh', position: 'relative' }}>
      <GravityStarsBackground 
        className="gravity-stars-bg"
        starsCount={300}
        starsSize={8}
        starsOpacity={0.8}
        glowIntensity={20}
        movementSpeed={0.4}
        mouseInfluence={150}
        mouseGravity="attract"
        gravityStrength={100}
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
