import Iridescence from '../../components/Iridescence.jsx'
import { MorphingNavigation } from "../../components/lightswind/morphing-navigation.tsx"
import { Home as HomeIcon, ShoppingBag, Info, HelpCircle } from "lucide-react";
import 'Home.css'

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
        onLinkClick={(link) => console.log('Clicked:', link)}
      />

      <MorphingNavigation
        links={[
          { id: 'home', label: 'Home', href: '#home', icon: <HomeIcon size={14} /> },
          { id: 'shop', label: 'Shop', href: '#shop', icon: <ShoppingBag size={14} /> },
          { id: 'about', label: 'About', href: '#about', icon: <Info size={14} /> },
          { id: 'help', label: 'Help', href: '#help', icon: <HelpCircle size={14} /> }
        ]}
        theme="custom"
        backgroundColor="rgba(59, 130, 246, 0.1)"
        textColor="#3b82f6"
        borderColor="rgba(59, 130, 246, 0.3)"
        scrollThreshold={150}
        animationDuration={1.5}
        enablePageBlur={true}
        onLinkClick={(link) => console.log('Clicked:', link)}
        onMenuToggle={(isOpen) => console.log('Menu:', isOpen)}
      />
    </div>
  )
}
