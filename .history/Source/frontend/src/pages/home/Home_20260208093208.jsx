import ParticlesBackground from '../../components/Particles';
import { MorphingNavigation } from "../../components/lightswind/morphing-navigation.tsx"
import { Home as HomeIcon, ShoppingBag, Info, HelpCircle } from "lucide-react";
import './Home.css'
import { useEffect, useState } from "react";
import GradualBlur from '../../components/GradualBlur';
import RotatingText from '../../components/RotatingText'
import SplashCursor from '../../components/SplashCursor'
import StarBorder from '../../components/StarBorder'
import GradientText from '../../components/GradientText'

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
      <div className="fixed-logo">
        <img src="/images/logo.png" alt="" />
      </div>
      <SplashCursor />
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
      <section style={{ position: 'relative', minHeight: '100vh' }}>
        <div style={{ padding: '6rem 2rem' }}>
          <div className="container-fluid" style={{ width: '90%', marginLeft: '5%', marginRight: '5%', marginTop: '4%', display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', zIndex: 1, borderRadius: '25px' }}>
            <div className="container-fluid HOME1" style={{ width: '100%', height: '100%', display: 'flex', justifyContent: 'center', alignItems: 'center', padding: '0', flexDirection: 'row' }}>
              <div className="container" style={{ padding: '0', backgroundColor: 'transparent', height: 'auto', width: '100%', display: 'flex', flexDirection: 'column' }}>
                <div className="container-fluid" style={{ display: 'flex', flexDirection: 'row', marginTop: '10%' }}>
                  <div className="container" style={{ padding: '0', backgroundColor: 'transparent', height: 'auto', width: '50%', display: 'flex', alignItems: 'center', justifyContent: 'flex-end', marginRight: '10px' }}>
                    <h1 style={{ margin: '0', fontSize: '3rem', fontWeight: 'bold', color: '#000000', fontFamily: 'Merriweather'}}>Vì lợi ích</h1>
                  </div>
                  <div className="container" style={{ padding: '0', backgroundColor: 'transparent', height: 'auto', width: '100%', display: 'flex', justifyContent: 'flex-start', alignItems: 'center', fontFamily: 'Merriweather', fontSize: '3rem', fontStyle: 'italic', fontWeight: 'bold' }}>
                    <RotatingText
                      texts={['mười năm trồng cây', 'trăm năm trồng người']}
                      mainClassName="px-2 sm:px-2 md:px-3 overflow-hidden py-0.5 sm:py-1 md:py-3 justify-center rounded-lg"
                      staggerFrom={"last"}
                      initial={{ y: "100%" }}
                      animate={{ y: 0 }}
                      exit={{ y: "-120%" }}
                      staggerDuration={0.025}
                      splitLevelClassName="overflow-hidden pb-0.5 sm:pb-1 md:pb-1"
                      transition={{ type: "spring", damping: 30, stiffness: 400 }}
                      rotationInterval={5000}
                    />
                  </div>
                </div>
                <div className="container-fluid" style={{ display: 'flex', justifyContent: 'center', marginBottom: '5%' }}>
                  <h1 style={{ margin: '0', fontSize: '2.2rem', color: '#000000', fontFamily: 'Merriweather', fontStyle: 'italic'}}>Chắt lọc tri thức – Nuôi dưỡng hiểu biết.</h1>
                </div>
                <div className="container-fluid" style={{ display: 'flex', justifyContent: 'flex-start', marginLeft: '3%', width: 'auto', marginRight: '3%', marginBottom: '1%' }}>
                  <h1 style={{ margin: '0', fontSize: '1.5rem', color: '#000000', fontFamily: 'Merriweather' }}>Hệ thống tích hợp trí tuệ nhân tạo hỗ trợ tóm tắt trích xuất và diễn giải các bài đọc tiếng Việt theo từng cấp lớp tiểu học.</h1>
                </div>
                <div className="container-fluid" style={{ display: 'flex', justifyContent: 'flex-start', marginLeft: '3%', width: 'auto', marginRight: '3%', marginBottom: '5%' }}>
                  <h1 style={{ margin: '0', fontSize: '1.5rem', color: '#000000', fontFamily: 'Merriweather' }}>Phần mềm giúp học sinh tiếp cận nội dung bài học một cách nhẹ nhàng, dễ hiểu, từ đó nâng cao khả năng đọc hiểu và hình thành tư duy học hiểu ngay từ những năm đầu.</h1>
                </div>
                <div className="container-fluid" style={{ display: 'flex', justifyContent: 'flex-start', marginLeft: '3%', width: 'auto', marginRight: '3%', marginBottom: '10%' }}>
                  <StarBorder
                    as="button"
                    className="custom-class"
                    color="#940cd5"
                    speed="3s">
                    <GradientText
                      colors={["#ff3838", "#1eb528", "#21bbca","#ad38ff", "#ff38c1"]}
                      animationSpeed={8}
                      showBorder={false}
                      className="custom-class">
                        <h3>Bắt đầu ngay</h3>
                    </GradientText>
                  </StarBorder>
                </div>
              </div>
              <div className="container" style={{ padding: '0', backgroundColor: 'transparent', height: 'auto', width: '100%'}}>
                <h1 style={{ margin: '0'}}>Home</h1>
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
