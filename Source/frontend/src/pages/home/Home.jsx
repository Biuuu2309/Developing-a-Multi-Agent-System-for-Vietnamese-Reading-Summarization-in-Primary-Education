import ParticlesBackground from '../../components/Particles';
import { MorphingNavigation } from "../../components/lightswind/morphing-navigation.tsx";
import { Home as HomeIcon, ShoppingBag, Info, HelpCircle, BookOpen, BookText } from "lucide-react";
import './Home.css';
import { useEffect, useState, useCallback, useMemo } from "react";
import { useNavigate, Link } from "react-router-dom";
import GradualBlur from '../../components/GradualBlur';
import RotatingText from '../../components/RotatingText';
import SplashCursor from '../../components/SplashCursor';
import StarBorder from '../../components/StarBorder';
import GradientText from '../../components/GradientText';
import ScrambledText from '../../components/ScrambledText';
import { GlowingCards, GlowingCard } from "../../components/lightswind/glowing-cards";
import { Zap, Sparkles, Crown } from "lucide-react";
import { AuroraTextEffect } from "../../components/lightswind/aurora-text-effect";
import ShinyText from '../../components/ShinyText';
import { InteractiveGradient } from "../../components/lightswind/interactive-gradient-card";
import ScrollList from '../../components/lightswind/scroll-list';
import MetaBalls from '../../components/MetaBalls';
import { PlusIcon } from 'lucide-react';
import { RippleButton, RippleButtonRipples } from '../../components/animate-ui/components/buttons/ripple';
import { getStoredUser, logout } from '../../services/authService';
import { User as UserIcon, LogOut } from 'lucide-react';

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

// Function to generate random color
const generateRandomColor = () => {
  // Generate random RGB values for light/pastel colors
  const r = Math.floor(Math.random() * 100) + 150; // 150-250 (light colors)
  const g = Math.floor(Math.random() * 100) + 150;
  const b = Math.floor(Math.random() * 100) + 150;
  return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`;
};

// Function to generate a complementary/light color for cursor
const generateCursorColor = () => {
  // Return white or a very light color for cursor
  return '#ffffff';
};

export default function Home() {
  const [currentUser, setCurrentUser] = useState(() => getStoredUser());
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);

  useEffect(() => {
    const onStorage = () => setCurrentUser(getStoredUser());
    window.addEventListener('storage', onStorage);
    return () => window.removeEventListener('storage', onStorage);
  }, []);

  const handleLogout = useCallback(() => {
    logout();
    setCurrentUser(null);
    setIsUserMenuOpen(false);
  }, []);
  const navigate = useNavigate();
  const [isScrolled, setIsScrolled] = useState(false);
  const [isLogoHidden, setIsLogoHidden] = useState(false);

  // Generate random colors for MetaBalls (memoized to keep them consistent)
  const metaBallsColor = useMemo(() => generateRandomColor(), []);
  const metaBallsCursorColor = useMemo(() => generateCursorColor(), []);

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

  // Handle navigation link clicks
  const handleLinkClick = useCallback((link) => {
    if (link.id === 'summary') {
      navigate('/summary');
    } else if (link.id === 'story') {
      navigate('/story');
    } else if (link.id === 'mas-flow') {
      navigate('/mas-flow');
    }
    // Other links will use default scroll behavior handled by MorphingNavigation
  }, [navigate]);

  // Memoize links để tránh re-render không cần thiết
  const navLinks = useMemo(() => [
    { id: 'home', label: 'Home', href: '#home', icon: <HomeIcon size={30} /> },
    { id: 'summary', label: 'Summary', href: '/summary', icon: <BookOpen size={30} /> },
    { id: 'story', label: 'Story', href: '/story', icon: <BookText size={30} /> },
    { id: 'mas-flow', label: 'MAS Flow', href: '/mas-flow', icon: <Zap size={30} /> }
  ], []);

  return (
    <div style={{ width: '100%', minHeight: '100vh', position: 'relative' }}>
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
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginLeft: '20px' }}>
        <img src="/images/logo.png" alt="" style={{ width: '80px', height: '70px' }} />
          <AuroraTextEffect
            text="VUSUMMARY"
            fontSize="clamp(3rem, 5vw, 3rem)"
            style={{
              margin: 0,
              fontFamily: "ui-serif",
              fontWeight: "bold",
            }}
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
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginRight: '20px', position: 'relative' }}>
        {currentUser ? (
          <>
            <button
              type="button"
              onClick={() => setIsUserMenuOpen((v) => !v)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '10px',
                padding: '8px 12px',
                background: 'rgba(255,255,255,0.95)',
                border: '1px solid rgba(0,0,0,0.1)',
                borderRadius: '12px',
                cursor: 'pointer',
                backdropFilter: 'blur(10px)',
              }}
              title={currentUser.role || 'User'}
            >
              {currentUser.avatarUrl ? (
                <img
                  src={currentUser.avatarUrl}
                  alt=""
                  style={{ width: '28px', height: '28px', borderRadius: '999px', objectFit: 'cover' }}
                />
              ) : (
                <div style={{ width: '28px', height: '28px', borderRadius: '999px', background: '#E5E7EB', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <UserIcon size={16} />
                </div>
              )}
              <span style={{ fontWeight: 600, color: '#374151', fontSize: '14px' }}>{currentUser.username}</span>
            </button>

            {isUserMenuOpen && (
              <div
                style={{
                  position: 'absolute',
                  top: '48px',
                  right: 0,
                  width: '220px',
                  background: 'rgba(255,255,255,0.98)',
                  border: '1px solid rgba(0,0,0,0.08)',
                  borderRadius: '12px',
                  boxShadow: '0 12px 24px rgba(0,0,0,0.12)',
                  padding: '8px',
                  zIndex: 1000,
                }}
              >
                <div style={{ padding: '8px 10px', color: '#6B7280', fontSize: '12px' }}>
                  Role: <b style={{ color: '#374151' }}>{currentUser.role || 'CHILD'}</b>
                </div>
                <button
                  type="button"
                  onClick={handleLogout}
                  style={{
                    width: '100%',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '10px',
                    padding: '10px',
                    border: 'none',
                    background: 'transparent',
                    borderRadius: '10px',
                    cursor: 'pointer',
                    color: '#EF4444',
                    fontWeight: 600,
                  }}
                >
                  <LogOut size={16} />
                  Đăng xuất
                </button>
              </div>
            )}
          </>
        ) : (
          <>
            <Link to="/login">
              <RippleButton variant="outline" size="lg" style={{ borderRadius: '10px', height: '40px' }}>
                <div style={{ fontFamily: "none", fontWeight: "bold" }}>Login</div>
                <RippleButtonRipples />
              </RippleButton>
            </Link>
            <Link to="/register">
              <RippleButton variant="default" size="lg" style={{ borderRadius: '10px', height: '40px', opacity: '0.8' }}>
                <div style={{ fontFamily: "none", fontWeight: "bold" }}>Register</div>
                <RippleButtonRipples />
              </RippleButton>
            </Link>
          </>
        )}
        </div>
      </div>
      {/* <SplashCursor /> */}
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
        onLinkClick={handleLinkClick}
        scrollThreshold={150}
        animationDuration={1.5}
        enablePageBlur={true}
        glowIntensity={5}
        onMenuToggle={(isOpen) => console.log('Menu:', isOpen)}
      />


      <section style={{ position: 'relative', minHeight: '100vh' }}>
        <div style={{ padding: '1rem 2rem' }}>
          <div className="container-fluid" style={{ width: '90%', marginLeft: '5%', marginRight: '5%', marginTop: '2.5%', display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', zIndex: 1, borderRadius: '25px' }}>
            <div className="container-fluid HOME1" style={{ width: '100%', height: '100%', display: 'flex', justifyContent: 'center', alignItems: 'center', padding: '0', flexDirection: 'row' }}>
              <div className="container" style={{ padding: '0', backgroundColor: 'transparent', height: 'auto', width: '100%', display: 'flex', flexDirection: 'column' }}>
                <div className="container-fluid" style={{ display: 'flex', flexDirection: 'row', marginTop: '10%' }}>
                  <div className="container" style={{ padding: '0', backgroundColor: 'transparent', height: 'auto', width: '50%', display: 'flex', alignItems: 'center', justifyContent: 'flex-end', marginRight: '10px' }}>
                    <h1 style={{ margin: '0', fontSize: '3.5rem', fontWeight: 'bold', color: '#7dcb88', fontFamily: 'Merriweather' }}>Vì lợi ích</h1>
                  </div>
                  <div className="container" style={{ padding: '0', backgroundColor: 'transparent', height: 'auto', width: '100%', display: 'flex', justifyContent: 'flex-start', alignItems: 'center', fontFamily: 'Merriweather', fontSize: '3.5rem', fontStyle: 'italic', fontWeight: 'bold', color: '#55925d' }}>
                    <RotatingText
                      texts={['mười năm trồng cây', 'trăm năm trồng người']}
                      mainClassName="px-2 sm:px-2 md:px-3 overflow-hidden py-0.5 sm:py-1 md:py-3 justify-center rounded-lg"
                      staggerFrom={"first"}
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
                  <h1 style={{ margin: '0', fontSize: '2.5rem', color: '#000000', fontFamily: 'Merriweather', fontStyle: 'italic' }}>Chắt lọc tri thức – Nuôi dưỡng hiểu biết.</h1>
                </div>
                <div className="container-fluid" style={{ display: 'flex', justifyContent: 'flex-start', marginLeft: '3%', width: 'auto', marginRight: '3%', marginBottom: '1%', textAlign: 'justify' }}>
                  <ScrambledText
                    className="scrambled-text-demo m-0"
                    radius={50}
                    duration={1.2}
                    speed={0.5}
                    scrambleChars=".:">
                    <div
                      style={{
                        margin: '0',
                        fontSize: '2rem',
                        color: '#000000',
                        fontFamily: 'Merriweather',
                        textAlign: 'justify',
                      }}
                    >
                      Phần mềm giúp học sinh tiếp cận nội dung bài học một cách nhẹ nhàng, dễ hiểu, từ đó nâng cao khả năng đọc hiểu và hình thành tư duy học hiểu ngay từ những năm đầu.
                    </div>
                  </ScrambledText>
                </div>
                <div className="container-fluid" style={{ display: 'flex', justifyContent: 'flex-start', marginLeft: '3%', width: 'auto', marginRight: '3%', marginBottom: '5%', textAlign: 'justify' }}>
                  <ScrambledText
                    className="scrambled-text-demo m-0"
                    radius={50}
                    duration={1.2}
                    speed={0.5}
                    scrambleChars=".:">
                    <div
                      style={{
                        margin: '0',
                        fontSize: '2rem',
                        color: '#000000',
                        fontFamily: 'Merriweather',
                        textAlign: 'justify',
                      }}
                    >
                      Hệ thống tích hợp trí tuệ nhân tạo hỗ trợ tóm tắt trích xuất và diễn giải truyện, văn bản, bài đọc tiếng Việt theo từng cấp lớp tiểu học.
                    </div>
                  </ScrambledText>
                </div>
                <div className="container-fluid divbtn" style={{ display: 'flex', justifyContent: 'flex-start', marginLeft: '3%', width: 'auto', marginRight: '3%', marginBottom: '10%' }}>
                  <StarBorder
                    as="button"
                    className="custom-class"
                    color="#940cd5"
                    speed="3s"
                    onClick={() => navigate('/summary')}>
                    <GradientText
                      colors={["#ff3838", "#1eb528", "#21bbca", "#ad38ff", "#ff38c1"]}
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
              <div className="container" style={{ padding: '0', backgroundColor: 'transparent', height: 'auto', width: '100%' }}>
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
                  <GlowingCard glowColor="#eb3743" className="space-y-5">
                    <InteractiveGradient
                      color="#ffc8a4"
                      glowColor="#eb6770"
                      followMouse={true}
                      hoverOnly={false}
                      intensity={100}
                      backgroundColor="#ffe4d2"
                      width="100%"
                      height="100%"
                      borderRadius="1.5rem"
                    >
                      <div className="p-3 text-white rounded-xl" style={{ display: 'flex', flexDirection: 'row', alignItems: 'center' }} >
                        <img src="/images/problem.png" alt="" style={{ width: '12%', height: '12%', marginRight: '5px' }} />
                        <h3 style={{ color: '#df8144', fontSize: '1.2rem', margin: '0' }}>Tóm tắt trong thực tiễn</h3>
                      </div>
                    </InteractiveGradient>
                    <InteractiveGradient
                      color="#1890ff"
                      glowColor="#eb6770"
                      followMouse={true}
                      hoverOnly={false}
                      intensity={100}
                      backgroundColor="#ffe4d2"
                      width="100%"
                      height="100%"
                      borderRadius="1.5rem"
                    >
                      <div className="p-2 text-justify" style={{ fontSize: '1rem', fontFamily: 'Segoe UI', margin: '10px' }}>
                        Tóm tắt văn bản là một bài toán trong lĩnh vực xử lý ngôn ngữ tự nhiên (NLP), nhằm rút gọn nội dung văn bản gốc thành một phiên bản ngắn gọn hơn nhưng vẫn đảm bảo các ý chính quan trọng và dễ hiểu. Quá trình tóm tắt không chỉ dừng lại ở việc giảm độ dài văn bản mà còn yêu cầu tính đúng đắn về ngữ pháp, chính tả, sự mạch lạc trong bố cục cũng như sự phù hợp về phong cách và ngữ nghĩa diễn đạt. <br /><br />
                        Trong lĩnh vực giáo dục, đặc biệt là ở bậc tiểu học, tóm tắt văn bản có tiềm năng lớn và vai trò quan trọng trong việc hỗ trợ nâng cao kỹ năng đọc hiểu, giúp học sinh tiếp cận nội dung học tập một cách hiệu quả hơn. Nhất là khi, các em phải xử lý các văn bản dài hoặc do vốn từ vựng hạn chế và khả năng tập trung chưa phát triển đầy đủ.
                      </div>
                    </InteractiveGradient>
                    </GlowingCard>
                  <GlowingCard glowColor="#2c2c2c" className="space-y-4">
                  <InteractiveGradient
                      color="#8d2799"
                      glowColor="#ffffff"
                      followMouse={true}
                      hoverOnly={false}
                      intensity={100}
                      backgroundColor="#d8d8d8"
                      width="100%"
                      height="100%"
                      borderRadius="1.5rem"
                    >
                      <div className="p-3 text-white rounded-xl" style={{ display: 'flex', flexDirection: 'row', alignItems: 'center' }} >
                        <img src="/images/target.png" alt="" style={{ width: '12%', height: '12%', marginRight: '5px' }} />
                        <h3 style={{ color: '#000000', fontSize: '1.2rem', margin: '0' }}>Mục tiêu nghiên cứu</h3>
                      </div>
                    </InteractiveGradient>
                    <InteractiveGradient
                      color="#8d2799"
                      glowColor="#ffffff"
                      followMouse={true}
                      hoverOnly={false}
                      intensity={100}
                      backgroundColor="#d8d8d8"
                      width="100%"
                      height="100%"
                      borderRadius="1.5rem"
                    >
                      <div className="p-2 text-justify" style={{ fontSize: '1rem', margin: '10px' }}>
                      1. Nghiên cứu về hệ thống đa tác tử (multi-agent systems), các giải pháp kỹ thuật về giao tiếp giữa các tác tử, bao gồm cơ chế chia sẻ dữ liệu và cải thiện quy trình hợp tác của các tác tử cho tóm tắt văn bản tiếng Việt. <br /><br />
                      2. Thiết kế các tác tử, tiền xử lý, tinh chỉnh, huấn luyện các mô hình tóm tắt trích xuất, diễn giải và tích hợp vào kiến trúc hệ thống đa tác tử. Chọn lọc, kiểm tra và đánh giá chất lượng bản tóm tắt thông qua BERTScore (so với văn bản gốc), từ điển cấp lớp và các đặc trưng độ khó văn bản. <br /><br />
                      3. Xây dựng ứng dụng đa tác tử có giao diện web hỗ trợ tóm tắt bài đọc tiếng Việt bậc tiểu học, cho phép điều chỉnh tóm tắt phù hợp cấp lớp.
                      </div>
                    </InteractiveGradient>
                  </GlowingCard>
                  <GlowingCard glowColor="#ffcc33" className="space-y-4">
                    <InteractiveGradient
                      color="#661010"
                      glowColor="#ffbf00"
                      followMouse={true}
                      hoverOnly={false}
                      intensity={100}
                      backgroundColor="#ffe8a4"
                      width="100%"
                      height="100%"
                      borderRadius="1.5rem"
                    >
                      <div className="p-3 text-white rounded-xl" style={{ display: 'flex', flexDirection: 'row', alignItems: 'center' }} >
                        <img src="/images/energy-saving-light.png" alt="" style={{ width: '12%', height: '12%', marginRight: '5px' }} />
                        <h3 style={{ color: '#a57d05', fontSize: '1.2rem', margin: '0' }}>Phương pháp nghiên cứu</h3>
                      </div>
                    </InteractiveGradient>
                    <InteractiveGradient
                      color="#661010"
                      glowColor="#ffbf00"
                      followMouse={true}
                      hoverOnly={false}
                      intensity={100}
                      backgroundColor="#ffe8a4"
                      width="100%"
                      height="100%"
                      borderRadius="1.5rem"
                    >
                      <div className="p-2 text-justify" style={{ fontSize: '1rem', margin: '10px' }}>
                        Dữ liệu được thu thập từ các nguồn sách uy tín, đảm bảo tính chính xác và độ tin cậy cao. Quá trình xử lý dữ liệu được kiểm soát nghiêm ngặt qua nhiều bước và ràng buộc khác nhau để tạo nên bộ dữ liệu đồng bộ, chất lượng và chính xác. <br /><br />
                        Hai mô hình tóm tắt trích xuất và diễn giải được tinh chỉnh với tham số tối ưu nhất từ rất nhiều lần tìm kiếm tham số bằng Optuna. Nhằm đạt được độ chính xác cao nhất và về chi phí và thời gian, độ chính xác và hiệu quả cao. <br /><br />
                        Kiến trúc hệ thống đa tác tử được thiết kế với các tác tử chuyên biệt theo từng bước. Kết quả đầu ra được đánh giá và kiểm tra thông qua BERTScore, từ điển cấp lớp và các đặc trưng độ khó văn bản.
                      </div>
                    </InteractiveGradient>
                  </GlowingCard>
                </GlowingCards>
              </div>
              <div className="container-fluid" style={{ padding: '0', backgroundColor: 'transparent', height: 'auto', width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', marginTop: '1%', marginBottom: '3%' }}>
                <GlowingCards
                  enableGlow={true}
                  glowRadius={30}
                  glowOpacity={0.8}
                  animationDuration={500}
                  gap="3rem"
                  responsive={true}
                >
                  <GlowingCard glowColor="#2d7cff" className="space-y-4">
                    <InteractiveGradient
                      color="#2d7cff"
                      glowColor="#41d1ff"
                      followMouse={true}
                      hoverOnly={false}
                      intensity={100}
                      backgroundColor="#d9ebff"
                      width="100%"
                      height="100%"
                      borderRadius="1.5rem"
                    >
                      <div className="p-3 text-white rounded-xl" style={{ display: 'flex', flexDirection: 'row', alignItems: 'center' }} >
                        <img src="/images/connection.png" alt="" style={{ width: '12%', height: '12%', marginRight: '5px' }} />
                        <h3 style={{ color: '#2d5fa8', fontSize: '1.2rem', margin: '0' }}>Hệ thống đa tác tử</h3>
                      </div>
                    </InteractiveGradient>
                    <InteractiveGradient
                      color="#2d7cff"
                      glowColor="#41d1ff"
                      followMouse={true}
                      hoverOnly={false}
                      intensity={100}
                      backgroundColor="#edf5ff"
                      width="100%"
                      height="100%"
                      borderRadius="1.5rem"
                    >
                      <div className="p-2 text-justify" style={{ fontSize: '1rem', margin: '10px' }}>
                        Hệ thống MAS điều phối nhiều tác tử chuyên trách theo từng bước: hiểu yêu cầu, lập kế hoạch, sinh kết quả và kiểm tra chất lượng. Cách tiếp cận này giúp nâng cao tính ổn định, khả năng mở rộng và minh bạch trong quá trình tạo tóm tắt. <br /><br />
                        Hệ thống đa tác tử được tổ chức theo hai tầng chức năng gồm Hệ thống 1 và Hệ thống 2, nhằm tách biệt lõi xử lý mô hình và lớp điều phối – tương tác. Hệ thống 1 với hai tác tử có nhiệm vụ tóm tắt trích xuất và diễn giải, trong khi Orchestrator quyết định luồng xử lý, lựa chọn tác tử phù hợp. Cách tổ chức này giúp cô lập phần tính toán nặng, đồng thời đảm bảo tính nhất quán trong quá trình sinh văn bản. Hệ thống 2 là tầng tương tác và điều phối mở rộng, chịu trách nhiệm giao tiếp tự nhiên với người dùng, phân loại ý định (intent), chuẩn hóa dữ liệu đầu vào, kiểm tra tính hợp lệ và kích hoạt Hệ thống 1 khi cần thiết. Tầng này còn gọi đánh giá chất lượng (BERTScore so với văn bản gốc, tỷ lệ từ vựng theo cấp lớp) và xử lý các yêu cầu bổ sung liên quan đến hệ thống. <br /><br />
                        Cách tiếp cận này hướng đến việc nâng cao tính thích ứng theo từng trình độ, đồng thời cải thiện chất lượng đầu ra so với mô hình đơn lẻ. Nghiên cứu vì vậy không chỉ đề xuất một công cụ ứng dụng, mà còn gợi mở một hướng tiếp cận có tính hệ thống cho việc phát triển các giải pháp AI phù hợp với giáo dục tiểu học trong bối cảnh chuyển đổi số. 
                      </div>
                    </InteractiveGradient>
                  </GlowingCard>

                  <GlowingCard glowColor="#22a06b" className="space-y-4">
                    <InteractiveGradient
                      color="#22a06b"
                      glowColor="#99f2c8"
                      followMouse={true}
                      hoverOnly={false}
                      intensity={100}
                      backgroundColor="#d6f7e7"
                      width="100%"
                      height="100%"
                      borderRadius="1.5rem"
                    >
                      <div className="p-3 text-white rounded-xl" style={{ display: 'flex', flexDirection: 'row', alignItems: 'center' }} >
                        <img src="/images/predictive.png" alt="" style={{ width: '12%', height: '12%', marginRight: '5px' }} />
                        <h3 style={{ color: '#21714f', fontSize: '1.2rem', margin: '0' }}>Mô hình tóm tắt trích xuất</h3>
                      </div>
                    </InteractiveGradient>
                    <InteractiveGradient
                      color="#22a06b"
                      glowColor="#99f2c8"
                      followMouse={true}
                      hoverOnly={false}
                      intensity={100}
                      backgroundColor="#ebfff5"
                      width="100%"
                      height="100%"
                      borderRadius="1.5rem"
                    >
                      <div className="p-2 text-justify" style={{ fontSize: '1rem', margin: '10px' }}>
                        Mô hình thực hiện tóm tắt văn bản bằng cách trích xuất các câu quan trọng từ văn bản gốc dựa trên các tiêu chí như tần suất từ khóa, vị trí câu và đặc trưng ngữ nghĩa, sau đó kết hợp chúng để tạo thành bản tóm tắt. Nội dung được giữ nguyên cấu trúc và cách diễn đạt ban đầu nên hạn chế sai lệch thông tin. Tuy nhiên, do các câu được trích chọn rời rạc, bản tóm tắt có thể thiếu tính liên kết và mạch lạc. <br /><br />
                        Mô hình được Optuna qua 14 lần tìm kiếm tham số với bộ dữ liệu gồm hơn 10.000 văn bản tiếng Việt đảm bảo tính đa dạng và độ tin cậy. PhoBERT được tinh chỉnh trên hơn 200.000 mẫu câu đã gắn nhãn (hơn 10.000 bài) để phân loại câu quan trọng (nhãn 0/1) cho tóm tắt trích xuất. Dữ liệu được chia 80% huấn luyện, 10% kiểm định, 10% kiểm tra. Siêu tham số tối ưu bằng Optuna: <br />
                        - learning_rate: 1.8508569223777847e-05 <br />
                        - batch_size: 16 <br />
                        - max_len: 256 <br />
                        - num_epochs: 2 <br />
                        - warmup_ratio: 0.09771605700633802.<br /><br />
                        Với mẫu kiểm tra, PhoBERT đạt: <br />
                        - ROUGE-1-F1: 0.5 <br />
                        - ROUGE-L-F1: 0.41 <br />
                        - BERTScore-F1: 0.85 <br /> <br />
                        Nhìn chung, mô hình đã đạt được độ chính xác cao, vừa tối ưu về chi phí và thời gian, vừa đảm bảo tính hiệu quả và chất lượng đầu ra.
                      </div>
                    </InteractiveGradient>
                  </GlowingCard>

                  <GlowingCard glowColor="#b04bff" className="space-y-4">
                    <InteractiveGradient
                      color="#b04bff"
                      glowColor="#ff9ad5"
                      followMouse={true}
                      hoverOnly={false}
                      intensity={100}
                      backgroundColor="#f2ddff"
                      width="100%"
                      height="100%"
                      borderRadius="1.5rem"
                    >
                      <div className="p-3 text-white rounded-xl" style={{ display: 'flex', flexDirection: 'row', alignItems: 'center' }} >
                        <img src="/images/knowledge.png" alt="" style={{ width: '12%', height: '12%', marginRight: '5px' }} />
                        <h3 style={{ color: '#7e35b4', fontSize: '1.2rem', margin: '0' }}>Mô hình tóm tắt diễn giải</h3>
                      </div>
                    </InteractiveGradient>
                    <InteractiveGradient
                      color="#b04bff"
                      glowColor="#ff9ad5"
                      followMouse={true}
                      hoverOnly={false}
                      intensity={100}
                      backgroundColor="#f9eeff"
                      width="100%"
                      height="100%"
                      borderRadius="1.5rem"
                    >
                      <div className="p-2 text-justify" style={{ fontSize: '1rem', margin: '10px' }}>
                        Phương pháp diễn giải tạo bản tóm tắt bằng cách hiểu nội dung tổng thể và diễn đạt lại các ý chính trong một văn bản mới, tương tự cách con người tóm lược. Thường dựa trên các mô hình học sâu, đặc biệt là mô hình ngôn ngữ lớn, phương pháp này cho phép tạo ra nội dung ngắn gọn, mạch lạc và tự nhiên. Tuy nhiên, nếu không được kiểm soát phù hợp, hệ thống có thể phát sinh sai lệch hoặc bổ sung thông tin không có trong văn bản gốc. <br /><br />
                        Mô hình được Optuna qua 13 lần cho phiên bản 1 và 19 lần cho phiên bản 2, ViT5 được tinh chỉnh trên hơn 20.000 văn bản tóm tắt. Dữ liệu được chia 80% huấn luyện, 10% kiểm định, 10% kiểm tra. Siêu tham số tối ưu bằng Optuna: <br />
                        - max_input_len: 768 <br />
                        - max_target_len: 256 <br />
                        - learning_rate: 0.00014854565680664033 <br />
                        - batch_size: 8 <br />
                        - grad_acc: 2 <br />
                        - num_train_epochs: 5 <br />
                        - weight_decay: 0.0016483963466136164 <br />
                        - warmup_ratio: 0.1 <br />
                        Trên mẫu kiểm tra, ViT5 đạt: <br />
                        - eval_rouge1: 0.847 <br />
                        - eval_rouge2: 0.607 <br />
                        - eval_rougeL: 0.603 <br /> <br />
                        Nhìn chung, mô hình đã nắm bắt được hầu hết từ khóa quan trọng từ văn bản gốc. Model sinh văn bản mạch lạc, cấu trúc câu tự nhiên, không bị rời rạc hay lộn xộn
                      </div>
                    </InteractiveGradient>
                  </GlowingCard>
                </GlowingCards>
              </div>
            </div>
            <div className="container-fluid HOME3" style={{ width: '100%', height: '100%', display: 'flex', justifyContent: 'center', alignItems: 'center', padding: '0', flexDirection: 'column' }}>
              <div className="container" style={{ padding: '0', backgroundColor: 'transparent', height: 'auto', width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', marginTop: '4%', fontFamily: 'Merriweather', fontSize: '3rem', fontWeight: 'bold', flexDirection: 'row', marginBottom: '4%', position: 'relative', paddingBottom: '4%' }}>
                <div style={{ position: 'absolute', width: '100%', height: '100%', zIndex: 1, marginRight: '70%' }}>
                  <MetaBalls
                    color={metaBallsColor}
                    cursorBallColor={metaBallsCursorColor}
                    cursorBallSize={2}
                    ballCount={15}
                    animationSize={25}
                    enableMouseInteraction
                    enableTransparency={true}
                    hoverSmoothness={0.15}
                    clumpFactor={1}
                    speed={0.3}
                  />
                </div>
                <div style={{ position: 'relative', zIndex: 2, width: '38%' }}>
                  <ShinyText
                    text="Quy trình hoạt động của hệ thống"
                    speed={3.3}
                    delay={0}
                    color="#f9a967"
                    shineColor="#ff55da"
                    spread={100}
                    direction="left"
                    yoyo={false}
                    pauseOnHover={false}
                    disabled={false}
                  />
                </div>
                <div style={{ position: 'relative', zIndex: 2 }}>
                  <ScrollList
                    data={[
                      { title: '1. Người dùng', description: 'Nhập yêu cầu trên giao diện web (trang tóm tắt / chat MAS).' },
                      { title: '2. Ứng dụng frontend', description: 'Gửi HTTP POST /api/mas/chat kèm userId, sessionId (nếu có), conversationId, userInput tới backend Spring Boot (cổng mặc định 8081, theo biến môi trường).' },
                      { title: '3. Spring Boot', description: 'MASSystemController → MasSystemService tạo mới hoặc tải phiên làm việc MAS và ghi bản ghi vào bảng mas_sessions.' },
                      { title: '4. Spring Boot', description: 'Lưu tin nhắn người dùng vào bảng messages (trạng thái chờ xử lý).' },
                      { title: '5. Spring Boot', description: 'Chuyển tiếp cùng payload tới API Flask bằng RestTemplate: POST {mas.flask.api.url}/api/mas/chat (mặc định http://localhost:5000).' },
                      { title: '6. Flask', description: 'Khởi tạo/khôi phục bộ nhớ phiên (SessionMemory) và gọi ConversationManager.chat, bên trong thực thi đồ thị LangGraph (graph.invoke) — tức Hệ thống 2 (MAS System 2).' },
                      { title: '7. System 2', description: 'Lần lượt chạy các nút: nhận diện ý định → làm rõ (nếu thiếu thông tin thì dừng, trả câu hỏi) → lập kế hoạch → OCR ảnh (nếu kế hoạch có bước OCR) → tóm tắt → đánh giá; có thể lặp lại lập kế hoạch khi cần cải thiện chất lượng tóm tắt.' },
                      { title: '8. Trong bước tóm tắt', description: 'Hệ thống 1 — Orchestrator — được gọi để chạy mô hình trích xuất hoặc diễn giải theo ý định đã xác định; kết quả trả về cho System 2.' },
                      { title: '9. Flask ', description: 'Trả JSON cho Spring: final_output, intent, plan, summary, evaluation, các trường mở rộng (goal, negotiation, confidence, …).' },
                      { title: '10. Spring Boot', description: 'Ghi trạng thái MAS vào mas_states, tách dữ liệu sang mas_plans, mas_evaluations, mas_goals, mas_negotiations, mas_agent_confidences, mas_agent_memories khi có.' },
                      { title: '11. Spring Boot', description: 'Cập nhật messages (tin trợ lý, hoàn tất / lỗi) và ghi agent_logs khi phù hợp.' },
                      { title: '12. Trong trường hợp', description: 'Nếu không cần làm rõ và có nội dung tóm tắt, Spring tạo bản ghi trong summaries (có thể kèm sinh ảnh minh họa và cập nhật URL).' },
                      { title: '13. Người dùng', description: 'Nhận phản hồi trên frontend; có thể gọi thêm API (ví dụ lịch sử phiên, summary-histories) để tra cứu dữ liệu đã lưu.' },
                    ]}
                    renderItem={(item) => (
                      <div>
                        <h3 className="font-semibold text-justify" style={{ fontSize: '1.2rem', fontFamily: 'sans-serif', fontWeight: 'bold', color: '#000000' }}>{item.title}</h3>
                        <p className="text-justify" style={{ fontSize: '1rem', fontFamily: 'sans-serif', fontWeight: 'normal', color: '#000000' }}>{item.description}</p>
                      </div>
                    )}
                    itemSpacing={24}
                  />
                  <div style={{ position: 'absolute', width: '100%', zIndex: 1, marginTop: '5%', display: 'flex', justifyContent: 'center', alignItems: 'center', fontWeight: 'normal', fontSize: '1.5rem', fontFamily: 'sans-serif', color: '#000000', flexDirection: 'column' }}>
                    <ShinyText
                      text="Scroll down to see more"
                      speed={3.3}
                      delay={0}
                      color="#000000"
                      shineColor="#ffffff"
                      spread={120}
                      direction="left"
                      yoyo={false}
                      pauseOnHover={false}
                      disabled={false}
                    />
                    <img src="/images/arrow.png" alt="" style={{ width: '3%', height: '3%' }} />
                  </div>
                </div>
              </div>
            </div>
            <div className="container-fluid HOME4" style={{ width: '100%', height: '100%', display: 'flex', justifyContent: 'center', alignItems: 'center', padding: '0', flexDirection: 'column' }}>
              <div className="container-fluid" style={{ padding: '0', backgroundColor: 'transparent', height: 'auto', width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '3%', flexDirection: 'column' }}>
                <InteractiveGradient
                  color="#661010"
                  glowColor="#ff8080"
                  followMouse={true}
                  hoverOnly={false}
                  intensity={50}
                  backgroundColor="transparent"
                  width="100%"
                  height="100%"
                  borderRadius="1.5rem 1.5rem 0 0"
                >
                  <div className="p-3 text-white rounded-xl" style={{ display: 'flex', flexDirection: 'row', alignItems: 'center', width: '100%', justifyContent: 'center', height: '100px', fontFamily: 'Merriweather', fontSize: '3rem', fontWeight: 'bold' }} >
                    <img src="/images/evaluation.png" alt="" style={{ width: '60px', height: '60px', marginRight: '20px' }} />
                    <ShinyText
                      text="Đánh giá & Kết luận"
                      speed={3.3}
                      delay={0}
                      color="#f9a967"
                      shineColor="#ff55da"
                      spread={50}
                      direction="left"
                      yoyo={false}
                      pauseOnHover={false}
                      disabled={false}
                    />
                  </div>
                </InteractiveGradient>
                <div style={{ marginTop: '40px', width: '100%' }}>
                <GlowingCards>
                  <GlowingCard glowColor="#ff6161" className="space-y-4">
                    <InteractiveGradient
                      color="#661010"
                      glowColor="#ff8080"
                      followMouse={true}
                      hoverOnly={false}
                      intensity={100}
                      backgroundColor="#e0ffcb"
                      width="100%"
                      height="100%"
                      borderRadius="1.5rem"
                    >
                      <div className="p-2 text-justify" style={{ fontSize: '1rem', margin: '10px' }}>
                        Nghiên cứu này đã đề xuất và triển khai một hệ thống tóm tắt văn bản tiếng Việt cho học sinh tiểu học dựa trên kiến trúc đa tác tử kết hợp giữa mô hình học sâu và cơ chế kiểm soát đầu ra theo cấp lớp. Về mặt công nghệ, hệ thống tích hợp các mô hình ngôn ngữ đã được tinh chỉnh cho hai hướng tiếp cận trích xuất và diễn giải, cơ chế tối ưu siêu tham số bằng Optuna, bộ từ điển phân tầng theo khối lớp; phần ứng dụng triển khai dùng BERTScore (so với văn bản gốc) và kiểm tra từ vựng theo cấp lớp (không dùng ROUGE vì không có bản tóm tắt tham chiếu). Kiến trúc triển khai theo hướng phân tách Frontend (React), Backend (Spring Boot) và AI Service độc lập (Flask-based MAS) giúp đảm bảo tính mô-đun và khả năng mở rộng. <br /><br />
                        Trong thử nghiệm có bản tóm tắt tham chiếu, các chỉ số đánh giá hiệu suất, độ bao phủ của mô hình tóm tắt trích xuất đạt kết quả tốt trên tập test 10 văn bản ngẫu nhiên với ROUGE-1 F1 = 0.744697863, ROUGE-L F1 = 0.744697863, BERTScore F1 = 0.849169618. Kết quả cho thấy mô hình chọn đúng câu trọng tâm và giữ được ngữ nghĩa cốt lõi. <br />
                        Cùng điều kiện có tham chiếu, mô hình tóm tắt diễn giải đạt ROUGE-1 F1 = 0.586668157, ROUGE-L F1 = 0.56622815, BERTScore F1 = 0.82366181; ứng dụng thực tế bổ sung ràng buộc từ điển theo cấp lớp như mô tả ở trên. <br /><br />
                        Về lợi ích, mô hình MAS cho phép phân tách rõ vai trò giữa các tác tử: sinh tóm tắt, đánh giá, phân loại ý định, chuẩn hóa đầu vào và điều phối xử lý. Cách tiếp cận này giúp tăng tính linh hoạt, dễ bảo trì và có thể mở rộng thêm các chức năng như phản hồi học tập hoặc cá nhân hóa nội dung trong tương lai. Ngoài ra, việc xây dựng bộ dữ liệu chuyên biệt cho bậc tiểu học đóng góp một nguồn tài nguyên có giá trị cho nghiên cứu xử lý ngôn ngữ tự nhiên tiếng Việt trong lĩnh vực giáo dục. Tuy nhiên, hệ thống hiện vẫn tồn tại một số hạn chế. Thứ nhất, thời gian sinh tóm tắt chưa được tối ưu trên môi trường thử nghiệm do giới hạn về cấu hình phần cứng. Thứ hai, việc đánh giá chủ yếu dựa trên thang đo tự động; các đánh giá định tính từ giáo viên và học sinh chưa được thực hiện đầy đủ. <br /><br />
                        Nghiên cứu đã xây dựng một hệ thống hỗ trợ tóm tắt văn bản tiếng Việt cho học sinh tiểu học dựa trên kiến trúc đa tác tử, kết hợp hai phương pháp trích xuất và diễn giải. Hệ thống tích hợp các mô hình học sâu đã tinh chỉnh, tối ưu siêu tham số bằng Optuna; đánh giá trên ứng dụng dùng BERTScore và từ điển cấp lớp. Bộ dữ liệu được xây dựng với cơ chế kiểm soát từ vựng theo cấp lớp, giúp bản tóm tắt phù hợp với năng lực đọc hiểu của học sinh lớp 1–5. Kiến trúc hệ thống được triển khai theo mô hình phân tách React (Frontend), Spring Boot (Backend) và AI Service độc lập, đảm bảo tính mô-đun và khả năng mở rộng. Kết quả thực nghiệm cho thấy hệ thống đạt hiệu quả ổn định, cho thấy tiềm năng của kiến trúc đa tác tử trong bài toán tóm tắt văn bản giáo dục tiếng Việt.
                      </div>
                    </InteractiveGradient>
                  </GlowingCard>
                </GlowingCards>
                </div>
              </div>
            </div>
          </div>
        </div>
        <GradualBlur
          target="page"        
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
