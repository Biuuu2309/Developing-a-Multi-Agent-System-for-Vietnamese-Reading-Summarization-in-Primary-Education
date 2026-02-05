import ParticlesBackground from '../../components/Particles';
import { MorphingNavigation } from "../../components/lightswind/morphing-navigation.tsx"
import { Home as HomeIcon, ShoppingBag, Info, HelpCircle } from "lucide-react";
import './Home.css'
import { useEffect, useState } from "react";
import GradualBlur from '../../components/GradualBlur';

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
      <section style={{ position: 'relative', height: '100vh', overflow: 'hidden' }}>
        <div style={{ height: '100%', overflowY: 'auto', padding: '6rem 2rem' }}>
          <div className="container-fluid" style={{ width: '90%', marginLeft: '5%', marginRight: '5%', marginTop: '7%', display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', zIndex: 1 }}>
            <div className="container-fluid HOME1" style={{ width: '100%', height: '100%', display: 'flex', justifyContent: 'center', alignItems: 'center', padding: '0' }}>
              <div className="container" style={{ padding: '0', backgroundColor: 'transparent', height: '1000px' }}>
                <h1>Home</h1>
              </div>
            </div>
          </div>
        </div>

        <GradualBlur
          target="parent"
          position="bottom"
          height="7rem"
          strength={2}
          divCount={5}
          curve="bezier"
          exponential
          opacity={1}
        />
      </section>
    </div>
  );
}
