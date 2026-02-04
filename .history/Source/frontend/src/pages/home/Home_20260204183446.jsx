import ParticlesBackground from '../../components/Particles';
import { MorphingNavigation } from "../../components/lightswind/morphing-navigation.tsx"
import { Home as HomeIcon, ShoppingBag, Info, HelpCircle } from "lucide-react";
import './Home.css'
import { useEffect, useState } from "react";

export default function Home() {
  const [isScrolled, setIsScrolled] = useState(false);

  useEffect(() => {
    const onScroll = () => {
      setIsScrolled(window.scrollY > 20);
    };
    window.addEventListener('scroll', onScroll);
    onScroll();
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  return (
    <div style={{ width: '100%', minHeight: '100vh', position: 'relative' }}>
      <ParticlesBackground
        particleColors={['#00ffff', '#ff00ff', '#ffaa00', '#0000ff', '#00ff00', '#ff0000']}
        particleBaseSize={400}
        particleCount={150}
        particleSpread={15}
        speed={0.15}
        className="particles-bg"
      />
      {isScrolled && <div className="scroll-overlay" />}
      <MorphingNavigation
        links={[
          { id: 'home', label: 'Home', href: '#home', icon: <HomeIcon size={30} /> },
          { id: 'shop', label: 'Shop', href: '#shop', icon: <ShoppingBag size={30} /> },
          { id: 'about', label: 'About', href: '#about', icon: <Info size={30} /> },
          { id: 'help', label: 'Help', href: '#help', icon: <HelpCircle size={30} /> }
        ]}
        theme="custom"
        backgroundColor="#ffffff00"
        textColor="#0000ff"
        borderColor="rgba(59, 130, 246, 0.9)"
        scrollThreshold={150}
        animationDuration={1.5}
        enablePageBlur={true}
        glowIntensity={5}
        onLinkClick={(link) => console.log('Clicked:', link)}
        onMenuToggle={(isOpen) => console.log('Menu:', isOpen)}
      />
      <div className="container-fluid" style={{ width: '80%', marginLeft: '5%', marginRight: '5%', marginTop: '7%', display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', zIndex: 1 }}>
        <div className="container HOME1" style={{ width: '100%', height: '100%', display: 'flex', justifyContent: 'center', alignItems: 'center', padding: '0' }}>
          <div className="container">
          </div>
          <div className="container" style = {{ padding: '0', backgroundColor: 'transparent'}}>
            <img src="/images/flat-university-background.png" alt="" style={{ width: '100%', height: '100%', objectFit: 'cover', background: 'transparent' }} />
          </div>
        </div>
      </div>
      <div className="container-fluid" style={{ width: '80%', marginLeft: '10%', marginRight: '10%', marginTop: '7%', display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', zIndex: 1 }}>
        <div className="container HOME1" style={{ width: '100%', height: '100%', display: 'flex', justifyContent: 'center', alignItems: 'center', padding: '0' }}>
          <div className="container">
          </div>
          <div className="container" style = {{ padding: '0', backgroundColor: 'transparent'}}>
            <img src="/images/flat-university-background.png" alt="" style={{ width: '100%', height: '100%', objectFit: 'cover', background: 'transparent' }} />
          </div>
        </div>
      </div>
      <div className="container-fluid" style={{ width: '80%', marginLeft: '10%', marginRight: '10%', marginTop: '7%', display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', zIndex: 1 }}>
        <div className="container HOME1" style={{ width: '100%', height: '100%', display: 'flex', justifyContent: 'center', alignItems: 'center', padding: '0' }}>
          <div className="container">
          </div>
          <div className="container" style = {{ padding: '0', backgroundColor: 'transparent'}}>
            <img src="/images/flat-university-background.png" alt="" style={{ width: '100%', height: '100%', objectFit: 'cover', background: 'transparent' }} />
          </div>
        </div>
      </div>
    </div>
  );
}
