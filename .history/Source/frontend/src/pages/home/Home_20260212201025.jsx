import ParticlesBackground from '../../components/Particles';
import { MorphingNavigation } from "../../components/lightswind/morphing-navigation.tsx"
import { Home as HomeIcon, ShoppingBag, Info, HelpCircle } from "lucide-react";
import './Home.css'
import { useEffect, useState, useCallback, useMemo } from "react";
import GradualBlur from '../../components/GradualBlur';
import RotatingText from '../../components/RotatingText'
import SplashCursor from '../../components/SplashCursor'
import StarBorder from '../../components/StarBorder'
import GradientText from '../../components/GradientText'
import ScrambledText from '../../components/ScrambledText';
import { GlowingCards, GlowingCard } from "../../components/lightswind/glowing-cards"
import { Zap, Sparkles, Crown } from "lucide-react";
import { AuroraTextEffect } from "../../components/lightswind/aurora-text-effect"
import ShinyText from '../../components/ShinyText';

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

export default function Home() {
  const [isScrolled, setIsScrolled] = useState(false);
  const [isLogoHidden, setIsLogoHidden] = useState(false);
  
  const handleScroll = useCallback(() => {
    setIsScrolled(window.scrollY > 20);
    setIsLogoHidden(window.scrollY > 50);
  }, []);

  useEffect(() => {
    const throttledScroll = throttle(handleScroll, 16); // ~60fps
    window.addEventListener('scroll', throttledScroll, { passive: true });
    handleScroll();
    return () => window.removeEventListener('scroll', throttledScroll);
  }, [handleScroll]);

  // Memoize links để tránh re-render không cần thiết
  const navLinks = useMemo(() => [
    { id: 'home', label: 'Home', href: '#home', icon: <HomeIcon size={30} /> },
    { id: 'shop', label: 'Shop', href: '#shop', icon: <ShoppingBag size={30} /> },
    { id: 'about', label: 'About', href: '#about', icon: <Info size={30} /> },
    { id: 'help', label: 'Help', href: '#help', icon: <HelpCircle size={30} /> }
  ], []);

  return (
    <div style={{ width: '100%', minHeight: '100vh', position: 'relative' }}>
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
      <SplashCursor />
      <ParticlesBackground
        particleColors={['#00ffff', '#ff00ff', '#ffaa00', '#0000ff', '#00ff00', '#ff0000']}
        particleBaseSize={400}
        particleCount={80}
        particleSpread={15}
        speed={0.15}
        className="particles-bg"
      />
      {isScrolled && <div className="scroll-overlay" />}
      <MorphingNavigation
        links={navLinks}
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
          <div className="container-fluid" style={{ width: '90%', marginLeft: '5%', marginRight: '5%', marginTop: '5.5%', display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', zIndex: 1, borderRadius: '25px' }}>
            <div className="container-fluid HOME1" style={{ width: '100%', height: '100%', display: 'flex', justifyContent: 'center', alignItems: 'center', padding: '0', flexDirection: 'row' }}>
              <div className="container" style={{ padding: '0', backgroundColor: 'transparent', height: 'auto', width: '100%', display: 'flex', flexDirection: 'column' }}>
                <div className="container-fluid" style={{ display: 'flex', flexDirection: 'row', marginTop: '10%' }}>
                  <div className="container" style={{ padding: '0', backgroundColor: 'transparent', height: 'auto', width: '50%', display: 'flex', alignItems: 'center', justifyContent: 'flex-end', marginRight: '10px' }}>
                    <h1 style={{ margin: '0', fontSize: '3rem', fontWeight: 'bold', color: '#7dcb88', fontFamily: 'Merriweather'}}>Vì lợi ích</h1>
                  </div>
                  <div className="container" style={{ padding: '0', backgroundColor: 'transparent', height: 'auto', width: '100%', display: 'flex', justifyContent: 'flex-start', alignItems: 'center', fontFamily: 'Merriweather', fontSize: '3rem', fontStyle: 'italic', fontWeight: 'bold', color: '#55925d' }}>
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
                  <ScrambledText
                    className="scrambled-text-demo m-0"
                    radius={50}
                    duration={1.2}
                    speed={0.5}
                    scrambleChars=".:">
                    <h1 style={{ margin: '0', fontSize: '1.5rem', color: '#000000', fontFamily: 'Merriweather' }}>Hệ thống tích hợp trí tuệ nhân tạo hỗ trợ tóm tắt trích xuất và diễn giải các bài đọc tiếng Việt theo từng cấp lớp tiểu học.</h1>
                  </ScrambledText>
                </div>
                <div className="container-fluid" style={{ display: 'flex', justifyContent: 'flex-start', marginLeft: '3%', width: 'auto', marginRight: '3%', marginBottom: '5%' }}>
                  <ScrambledText
                    className="scrambled-text-demo m-0"
                    radius={50}
                    duration={1.2}
                    speed={0.5}
                    scrambleChars=".:">
                    <h1 style={{ margin: '0', fontSize: '1.5rem', color: '#000000', fontFamily: 'Merriweather' }}>Phần mềm giúp học sinh tiếp cận nội dung bài học một cách nhẹ nhàng, dễ hiểu, từ đó nâng cao khả năng đọc hiểu và hình thành tư duy học hiểu ngay từ những năm đầu.</h1>
                  </ScrambledText>
                </div>
                <div className="container-fluid divbtn" style={{ display: 'flex', justifyContent: 'flex-start', marginLeft: '3%', width: 'auto', marginRight: '3%', marginBottom: '10%' }}>
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
                        <h3 style={{ display: 'flex', flexDirection: 'row', alignItems: 'center', justifyContent: 'center' }}>Bắt đầu ngay 
                          <img src="/images/next-button.png" alt="" style={{ height: '30px', marginLeft: '10px', marginTop: '4px' }} />
                        </h3>
                    </GradientText>
                  </StarBorder>
                </div>
              </div>
              <div className="container" style={{ padding: '0', backgroundColor: 'transparent', height: 'auto', width: '100%'}}>
                <img 
                  src="/images/image-thumnail.png" 
                  style={{ opacity: "0.9", willChange: 'opacity', transform: 'translateZ(0)' }} 
                  alt="" 
                  loading="lazy"
                />
              </div>
            </div>
            <div className="container-fluid HOME2" style={{ width: '100%', height: '100%', display: 'flex', justifyContent: 'center', alignItems: 'center', padding: '0', flexDirection: 'column' }}>
              <div className="container" style={{ padding: '0', backgroundColor: 'transparent', height: 'auto', width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', marginTop: '2%', fontFamily: 'Merriweather', fontSize: '3rem', fontWeight: 'bold' }}>
                <ShinyText
                  text="Về hệ thống ?"
                  speed={3.3}
                  delay={0}
                  color="#eb6770"
                  shineColor="#fad784"
                  spread={120}
                  direction="left"
                  yoyo={false}
                  pauseOnHover={false}
                  disabled={false}
                />
              </div>
              <div className="container-fluid" style={{ padding: '0', backgroundColor: 'transparent', height: 'auto', width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', marginTop: '2%' }}>
                <GlowingCards
                  enableGlow={true}
                  glowRadius={30}
                  glowOpacity={0.8}
                  animationDuration={500}
                  gap="3rem"
                  responsive={true}
                >
                  <GlowingCard glowColor="#f59e0b" className="space-y-4">
                    <div className="container" style={{ padding: '0', backgroundColor: 'transparent', height: 'auto', width: '100%', display: 'flex', flexDirection: 'row', alignItems: 'center' }}>
                      <img src="/images/problem.png" alt="" style={{ width: '12%', height: '12%' }} />
                      <h3 style={{ marginLeft: '10px', color: '#e2b85c', fontSize: '1.3rem' }}>Vấn đề thực tiễn</h3>
                    </div>
                    <p>
                      Hiện nay việc tiếp cận với khối lượng thông tin lớn từ sách vở, tài liệu và khả năng tập trung, đọc hiểu của các em trở nên khó khăn và còn nhiều hạn chế. <br /><br />
                      Ngày nay với sự phát triển của các mô hình và công cụ AI đã cho thấy khả năng tóm tắt văn bản với độ chính xác và mạch lạc cao. <br /><br />
                      Ứng dụng sẽ là một công cụ hỗ trợ học tập nhanh, dễ hiểu, tăng sự hứng thú đối với học và quá trình tiếp thu thông tin, giúp các em học sinh vượt qua rào cản đọc hiểu.
                    </p>
                  </GlowingCard>
                  <GlowingCard glowColor="#f59e0b" className="space-y-4">
                    <div className="container" style={{ padding: '0', backgroundColor: 'transparent', height: 'auto', width: '100%', display: 'flex', flexDirection: 'row', alignItems: 'center' }}>
                      <img src="/images/target.png" alt="" style={{ width: '12%', height: '12%' }} />
                      <h3 style={{ marginLeft: '10px', color: '#e2b85c', fontSize: '1.3rem' }}>Mục tiêu nghiên cứu</h3>
                    </div>
                    <p>
                      Xây dựng ứng dụng AI tóm tắt văn bản tiếng Việt thông qua việc ứng dụng các mô hình học sâu PhoBERT(trích xuất) và Vit5(diễn giải). <br /><br />
                      Mô hình được tinh chỉnh để tạo ra bản tóm tắt phù hợp cả về nội dung, độ dài, từ vựng và cấu trúc ngữ pháp. Bên cạnh đó, thiết kế giao diện ứng dụng thân thiện, hiện đại và đơn giản giúp các em học sinh dễ dàng sử dụng và tiếp cận.
                    </p>  
                  </GlowingCard>
                  <GlowingCard glowColor="#f59e0b" className="space-y-4">
                    <div className="container" style={{ padding: '0', backgroundColor: 'transparent', height: 'auto', width: '100%', display: 'flex', flexDirection: 'row', alignItems: 'center' }}>
                      <img src="/images/energy-saving-light.png" alt="" style={{ width: '12%', height: '12%' }} />
                      <h3 style={{ marginLeft: '10px', color: '#e2b85c', fontSize: '1.3rem' }}>Phương pháp nghiên cứu</h3>
                    </div>
                    <p>Enterprise-grade components...</p>
                  </GlowingCard>
                </GlowingCards>
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
