import { useEffect, useState } from 'react';
import Iridescence from '../../components/Iridescence.jsx';
import { MorphingNavigation } from "../../components/lightswind/morphing-navigation.tsx";
import { Home as HomeIcon, ShoppingBag, Info, HelpCircle } from "lucide-react";
import './Home.css';

export default function Home() {
  const [hideContent, setHideContent] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      const threshold = window.innerHeight * 0.1; // 10% chiều cao màn hình
      setHideContent(window.scrollY > threshold);
    };

    window.addEventListener('scroll', handleScroll);
    handleScroll(); // chạy 1 lần khi mount

    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <div style={{ width: '100%', minHeight: '100vh', position: 'relative' }}>
      <Iridescence
        color={[0.5, 0.6, 0.8]}
        mouseReact
        amplitude={0.1}
        speed={1}
      />
      <MorphingNavigation
        links={[
          { id: 'home', label: 'Home', href: '#home' },
          { id: 'shop', label: 'Shop', href: '#shop' },
          { id: 'about', label: 'About', href: '#about' },
          { id: 'help', label: 'Help', href: '#help' }
        ]}
        glowIntensity={5}
        onLinkClick={(link) => console.log('Clicked:', link)}
      />

      <MorphingNavigation
        links={[
          { id: 'home', label: 'Home', href: '#home', icon: <HomeIcon size={30} /> },
          { id: 'shop', label: 'Shop', href: '#shop', icon: <ShoppingBag size={30} /> },
          { id: 'about', label: 'About', href: '#about', icon: <Info size={30} /> },
          { id: 'help', label: 'Help', href: '#help', icon: <HelpCircle size={30} /> }
        ]}
        theme="custom"
        backgroundColor="rgba(59, 130, 246, 0.15)"
        textColor="#dfdee0d9"
        borderColor="rgba(59, 130, 246, 0.3)"
        scrollThreshold={150}
        animationDuration={1.5}
        enablePageBlur={true}
        glowIntensity={5}
        onLinkClick={(link) => console.log('Clicked:', link)}
        onMenuToggle={(isOpen) => console.log('Menu:', isOpen)}
      />
      <div
        className={`container-fluid home-content ${hideContent ? 'home-content-hidden' : ''}`}
        style={{
          width: '80%',
          marginLeft: '10%',
          marginRight: '10%',
          marginTop: '6%',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'center',
          zIndex: 1,
        }}
      >
        <div className="container" style={{ width: '20%', height: '20%', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
          <h1 className="text-4xl font-bold">Home</h1>
        </div>
        <div className="container" style={{ width: '20%', height: '20%', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
          <h1 className="text-4xl font-bold">Home</h1>
        </div>
        <div className="container" style={{ width: '20%', height: '20%', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
          <h1 className="text-4xl font-bold">Home</h1>
        </div>
        <div className="container" style={{ width: '20%', height: '20%', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
          <h1 className="text-4xl font-bold">Home</h1>
        </div>
        <div className="container" style={{ width: '20%', height: '20%', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
          <h1 className="text-4xl font-bold">Home</h1>
        </div>
        <div className="container" style={{ width: '20%', height: '20%', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
          <h1 className="text-4xl font-bold">Home</h1>
        </div>
        <div className="container" style={{ width: '20%', height: '20%', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
          <h1 className="text-4xl font-bold">Home</h1>
        </div>
        <div className="container" style={{ width: '20%', height: '20%', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
          <h1 className="text-4xl font-bold">Home</h1>
        </div>
        <div className="container" style={{ width: '20%', height: '20%', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
          <h1 className="text-4xl font-bold">Home</h1>
        </div>
        <div className="container" style={{ width: '20%', height: '20%', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
          <h1 className="text-4xl font-bold">Home</h1>
        </div>
        <div className="container" style={{ width: '20%', height: '20%', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
          <h1 className="text-4xl font-bold">Home</h1>
        </div>
        <div className="container" style={{ width: '20%', height: '20%', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
          <h1 className="text-4xl font-bold">Home</h1>
        </div>
      </div>
    </div>
  );
}
