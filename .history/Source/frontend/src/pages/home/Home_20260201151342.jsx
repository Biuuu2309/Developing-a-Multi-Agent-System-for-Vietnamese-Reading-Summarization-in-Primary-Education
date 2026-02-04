import Iridescence from '../../components/Iridescence.jsx'
import { MorphingNavigation } from "../../components/lightswind/morphing-navigation.tsx"
import { Home as HomeIcon, ShoppingBag, Info, HelpCircle } from "lucide-react";
import './Home.css'
import { DynamicNavigation } from "../../components/lightswind/dynamic-navigation.tsx";
import { Home as HomeIconNew, ShoppingCart, Info as InfoIcon, Phone as PhoneIcon } from "lucide-react";

export default function Home() {
  return (
    <div style={{ width: '100%', height: '100vh', position: 'relative' }}>
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
        backgroundColor="rgba(59, 130, 246, 0.08)"
        textColor="#dfdee0d9"
        borderColor="rgba(59, 130, 246, 0.3)"
        scrollThreshold={150}
        animationDuration={1.5}
        enablePageBlur={true}
        glowIntensity={5}
        onLinkClick={(link) => console.log('Clicked:', link)}
        onMenuToggle={(isOpen) => console.log('Menu:', isOpen)}
      />
    </div>
  )
}
