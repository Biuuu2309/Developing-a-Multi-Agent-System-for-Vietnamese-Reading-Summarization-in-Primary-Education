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
          marginTop: '20px',
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
              <RippleButton variant="outline" size="lg" style={{ borderRadius: '10px', height: '40px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                Login
                <RippleButtonRipples />
              </RippleButton>
            </Link>
            <Link to="/register">
              <RippleButton variant="default" size="lg" style={{ borderRadius: '10px', height: '40px', opacity: '0.8' }}>
                Register
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
        <div style={{ padding: '6rem 2rem' }}>
          <div className="container-fluid" style={{ width: '90%', marginLeft: '5%', marginRight: '5%', marginTop: '2.5%', display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', zIndex: 1, borderRadius: '25px' }}>
            <div className="container-fluid HOME1" style={{ width: '100%', height: '100%', display: 'flex', justifyContent: 'center', alignItems: 'center', padding: '0', flexDirection: 'row' }}>
              <div className="container" style={{ padding: '0', backgroundColor: 'transparent', height: 'auto', width: '100%', display: 'flex', flexDirection: 'column' }}>
                <div className="container-fluid" style={{ display: 'flex', flexDirection: 'row', marginTop: '10%' }}>
                  <div className="container" style={{ padding: '0', backgroundColor: 'transparent', height: 'auto', width: '50%', display: 'flex', alignItems: 'center', justifyContent: 'flex-end', marginRight: '10px' }}>
                    <h1 style={{ margin: '0', fontSize: '3rem', fontWeight: 'bold', color: '#7dcb88', fontFamily: 'Merriweather' }}>Vì lợi ích</h1>
                  </div>
                  <div className="container" style={{ padding: '0', backgroundColor: 'transparent', height: 'auto', width: '100%', display: 'flex', justifyContent: 'flex-start', alignItems: 'center', fontFamily: 'Merriweather', fontSize: '3rem', fontStyle: 'italic', fontWeight: 'bold', color: '#55925d' }}>
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
                  <h1 style={{ margin: '0', fontSize: '2.2rem', color: '#000000', fontFamily: 'Merriweather', fontStyle: 'italic' }}>Chắt lọc tri thức – Nuôi dưỡng hiểu biết.</h1>
                </div>
                <div className="container-fluid" style={{ display: 'flex', justifyContent: 'flex-start', marginLeft: '3%', width: 'auto', marginRight: '3%', marginBottom: '1%' }}>
                  <ScrambledText
                    className="scrambled-text-demo m-0"
                    radius={50}
                    duration={1.2}
                    speed={0.5}
                    scrambleChars=".:">
                    <div style={{ margin: '0', fontSize: '1.5rem', color: '#000000', fontFamily: 'Merriweather', fontWeight: 'bold' }}>Hệ thống tích hợp trí tuệ nhân tạo hỗ trợ tóm tắt trích xuất và diễn giải các bài đọc tiếng Việt theo từng cấp lớp tiểu học.</div>
                  </ScrambledText>
                </div>
                <div className="container-fluid" style={{ display: 'flex', justifyContent: 'flex-start', marginLeft: '3%', width: 'auto', marginRight: '3%', marginBottom: '5%' }}>
                  <ScrambledText
                    className="scrambled-text-demo m-0"
                    radius={50}
                    duration={1.2}
                    speed={0.5}
                    scrambleChars=".:">
                    <div style={{ margin: '0', fontSize: '1.5rem', color: '#000000', fontFamily: 'Merriweather', fontWeight: 'bold' }}>Phần mềm giúp học sinh tiếp cận nội dung bài học một cách nhẹ nhàng, dễ hiểu, từ đó nâng cao khả năng đọc hiểu và hình thành tư duy học hiểu ngay từ những năm đầu.</div>
                  </ScrambledText>
                </div>
                <div className="container-fluid divbtn" style={{ display: 'flex', justifyContent: 'flex-start', marginLeft: '3%', width: 'auto', marginRight: '3%', marginBottom: '10%' }}>
                  <StarBorder
                    as="button"
                    className="custom-class"
                    color="#940cd5"
                    speed="3s">
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
                  <GlowingCard glowColor="#227568" className="space-y-5">
                    <InteractiveGradient
                      color="#227568"
                      glowColor="#ff4d5d"
                      followMouse={true}
                      hoverOnly={false}
                      intensity={100}
                      backgroundColor="#a8f19c"
                      width="100%"
                      height="100%"
                      borderRadius="1.5rem"
                    >
                      <div className="p-3 text-white rounded-xl" style={{ display: 'flex', flexDirection: 'row', alignItems: 'center' }} >
                        <img src="/images/problem.png" alt="" style={{ width: '12%', height: '12%', marginRight: '5px' }} />
                        <h3 style={{ color: '#277522', fontSize: '1.2rem', margin: '0' }}>Vấn đề thực tiễn</h3>
                      </div>
                    </InteractiveGradient>
                    <InteractiveGradient
                      color="#1890ff"
                      glowColor="#ff4d5d"
                      followMouse={true}
                      hoverOnly={false}
                      intensity={100}
                      backgroundColor="#d5f0d1"
                      width="100%"
                      height="100%"
                      borderRadius="1.5rem"
                    >
                      <div className="p-2 text-justify" style={{ fontSize: '1rem', fontFamily: 'Segoe UI' }}>
                        Hiện nay việc tiếp cận với khối lượng thông tin lớn từ sách vở, tài liệu và khả năng tập trung, đọc hiểu của các em trở nên khó khăn và còn nhiều hạn chế. <br /><br />
                        Ngày nay với sự phát triển của các mô hình và công cụ AI đã cho thấy khả năng tóm tắt văn bản với độ chính xác và mạch lạc cao. <br /><br />
                        Ứng dụng sẽ là một công cụ hỗ trợ học tập nhanh, dễ hiểu, tăng sự hứng thú đối với học và quá trình tiếp thu thông tin, giúp các em học sinh vượt qua rào cản đọc hiểu.
                      </div>
                    </InteractiveGradient>
                    </GlowingCard>
                  <GlowingCard glowColor="#8d2799" className="space-y-4">
                  <InteractiveGradient
                      color="#8d2799"
                      glowColor="#ffb261"
                      followMouse={true}
                      hoverOnly={false}
                      intensity={100}
                      backgroundColor="#efb9ff"
                      width="100%"
                      height="100%"
                      borderRadius="1.5rem"
                    >
                      <div className="p-3 text-white rounded-xl" style={{ display: 'flex', flexDirection: 'row', alignItems: 'center' }} >
                        <img src="/images/target.png" alt="" style={{ width: '12%', height: '12%', marginRight: '5px' }} />
                        <h3 style={{ color: '#940cd5', fontSize: '1.2rem', margin: '0' }}>Mục tiêu nghiên cứu</h3>
                      </div>
                    </InteractiveGradient>
                    <InteractiveGradient
                      color="#8d2799"
                      glowColor="#ffb261"
                      followMouse={true}
                      hoverOnly={false}
                      intensity={100}
                      backgroundColor="#f5e2e2"
                      width="100%"
                      height="100%"
                      borderRadius="1.5rem"
                    >
                      <div className="p-2 text-justify" style={{ fontSize: '1rem' }}>
                        Xây dựng ứng dụng AI tóm tắt văn bản tiếng Việt thông qua việc tinh chỉnh và finetuning các mô hình học sâu PhoBERT (trích xuất) và Vit5 (diễn giải). <br /><br />
                        Mô hình tạo ra bản tóm tắt phù hợp cả về nội dung, độ dài, từ vựng và cấu trúc ngữ pháp. Bản tóm tắt cam kết sẽ giữ được nội dung và ý nghĩa, từ vựng của văn bản gốc một cách chính xác. <br /><br />
                        Bên cạnh đó, thiết kế giao diện ứng dụng thân thiện, hiện đại và đơn giản giúp các em học sinh, giáo viên và phụ huynh dễ dàng sử dụng và tiếp cận.
                      </div>
                    </InteractiveGradient>
                  </GlowingCard>
                  <GlowingCard glowColor="#5e9fff" className="space-y-4">
                    <InteractiveGradient
                      color="#661010"
                      glowColor="#ee51be"
                      followMouse={true}
                      hoverOnly={false}
                      intensity={100}
                      backgroundColor="#b9beff"
                      width="100%"
                      height="100%"
                      borderRadius="1.5rem"
                    >
                      <div className="p-3 text-white rounded-xl" style={{ display: 'flex', flexDirection: 'row', alignItems: 'center' }} >
                        <img src="/images/energy-saving-light.png" alt="" style={{ width: '12%', height: '12%', marginRight: '5px' }} />
                        <h3 style={{ color: '#57729b', fontSize: '1.2rem', margin: '0' }}>Phương pháp nghiên cứu</h3>
                      </div>
                    </InteractiveGradient>
                    <InteractiveGradient
                      color="#661010"
                      glowColor="#ee51be"
                      followMouse={true}
                      hoverOnly={false}
                      intensity={100}
                      backgroundColor="#dfe1fc"
                      width="100%"
                      height="100%"
                      borderRadius="1.5rem"
                    >
                      <div className="p-2 text-justify" style={{ fontSize: '1rem' }}>
                        Cả hai bộ dữ liệu đã trải qua các bước tiền xử lý, sinh dữ liệu, chọn lọc và tổng hợp một cách cực kỳ chặt chẽ, rõ ràng, minh bạch dựa trên cơ sở khoa học và suy luận logic, đảm bảo tính khách quan và độ tin cậy cao.<br /><br />
                        Dựa trên hai bộ dữ liệu và bộ từ điển theo cấp lớp chuẩn sách giáo khoa được bộ giáo dục và đào tạo cung cấp. Mô hình được huấn luyện và tinh chỉnh sau khi optuna nhiều lần để đạt được độ chính xác cao nhất. Nhằm thu thập mô hình tốt nhất vả về chi phí và thời gian, độ chính xác và hiệu quả cao.
                      </div>
                    </InteractiveGradient>
                  </GlowingCard>
                </GlowingCards>
              </div>
              <div className="container-fluid" style={{ padding: '0', backgroundColor: 'transparent', height: 'auto', width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', marginTop: '2%', marginBottom: '3%' }}>
                <GlowingCards>
                  <GlowingCard glowColor="#ff1493" className="space-y-4">
                    <InteractiveGradient
                      color="#661010"
                      glowColor="#ff1493"
                      followMouse={true}
                      hoverOnly={false}
                      intensity={100}
                      backgroundColor="#f7dd8e"
                      width="100%"
                      height="100%"
                      borderRadius="1.5rem"
                    >
                      <div className="p-3 text-white rounded-xl" style={{ display: 'flex', flexDirection: 'row', alignItems: 'center', width: '100%', justifyContent: 'center' }} >
                        <img src="/images/evaluation.png" alt="" style={{ width: '5%', height: '5%', marginRight: '5px' }} />
                        <h3 style={{ color: '#73674c', fontSize: '1.2rem', margin: '0' }}>Đánh giá & Kết luận</h3>
                      </div>
                    </InteractiveGradient>
                    <InteractiveGradient
                      color="#661010"
                      glowColor="#ff1493"
                      followMouse={true}
                      hoverOnly={false}
                      intensity={100}
                      backgroundColor="#fafcb0"
                      width="100%"
                      height="100%"
                      borderRadius="1.5rem"
                    >
                      <div className="p-2 text-justify" style={{ fontSize: '1rem' }}>
                        Các chỉ số đánh giá hiệu suất, độ bao phủ của mô hình tóm tắt trích xuất đã có kết quả rất tốt và khả quan với F1 = , ROUGE-1 = , ROUGE-L = , BERTScore = . Kết quả cho thấy, mô hình đã chọn đúng câu trọng tâm và giữ được ngữ nghĩa cốt lõi. <br /><br />
                        Với mục tiêu tạo bản tóm tắt diễn giải chất lượng ngắn gọn, dễ hiểu, đầy đủ và chính xác phù hợp theo cấp lớp và được lọc và kiểm tra bởi bộ từ điển sách giáo khoa, mô hình tóm tắt diễn giải đã đạt được kết quả rất khả quan với F1 = , ROUGE-1 = , ROUGE-L = , BERTScore = . <br /><br />
                        Nhìn chung, các giáo viên đánh giá hệ thống là một công cụ hỗ trợ có ích và phù hợp cho giáo viên và học sinh. <br /><br />
                        Qua quá trình nghiên cứu và triển khai, đề tài đã đạt được những kết quả quan trọng cả về mặt lý thuyết lẫn thực tiễn. <br /><br />
                        Như vậy, có thể khẳng định rằng đề tài đã đạt được mục tiêu đặt ra: vừa mang tính khoa học khi khai thác các mô hình ngôn ngữ hiện đại vào tiếng Việt, vừa có tính ứng dụng khi tạo ra một hệ thống cụ thể, hữu ích cho học sinh, giáo viên và phụ huynh. Bên cạnh đó cho thấy, AI có tiềm năng lớn trong hỗ trợ giáo dục tiểu học tiếng Việt.
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
                    spread={120}
                    direction="left"
                    yoyo={false}
                    pauseOnHover={false}
                    disabled={false}
                  />
                </div>
                <div style={{ position: 'relative', zIndex: 2 }}>
                  <ScrollList
                    data={[
                      { title: 'Step 1: Hệ thống đa tác tử', description: 'Hệ thống đa tác tử sẽ xử lý hầu hết tất cả các nhiệm vụ chính của hệ thống. Đặc biệt, sử dụng đa tác tử giúp tăng tính linh hoạt, khả năng xử lý và đáp ứng nhu cầu người dùng một cách hiệu quả. Điều này đã được chứng minh và thực nghiệm qua rất cơ sở khoa học và ứng dụng thực tiễn như: OpenAI, Anthropic, Google, Meta, Microsoft, Nvidia, và nhiều tổ chức và công ty lớn khác.' },
                      { title: 'Step 2: Giới thiệu chung về hệ thống', description: 'Hệ thống đề cập về chức năng chính, lợi ích mang lại và quy trình hoạt động của hệ thống.' },
                      { title: 'Step 3: Lời chào', description: 'Hệ thống gửi lời chào thân thiện, cởi mở và đề cập về chức năng chính của hệ thống để người dùng hiểu và tiếp cận hệ thống một cách dễ dàng.' },
                      { title: 'Step 4: Phân loại yêu cầu của người dùng (Input Classifier Agent)', description: 'Phân loại yêu cầu của người dùng, chọn lọc phản hồi của người dùng và đưa ra câu trả lời phù hợp và hướng dẫn người dùng để hệ thống có thể hiểu và xử lý yêu cầu một cách chính xác.' },
                      { title: 'Step 5: Phân loại đầu vào văn bản (OCR và Spell Checker Agent)', description: 'Người dùng sẽ có những trường hợp và nhu cầu định dạng khác nhau. Việc thiết kế ứng dụng đa dạng góp phần trải nghiệm người dùng một cách tốt nhất. Bên cạnh đó sẽ được OCR và Spell Checker Agent xử lý để đảm bảo độ chính xác và độ tin cậy cao.' },
                      { title: 'Step 6: Tác tử điều phối', description: 'Coordinator Agent là tác tử chuyên điều phối và quản lý các tác tử con, xử lý các nhiệm vụ chính của hệ thống. Sau đó chọn lọc và đưa ra kết quả phản hồi tốt nhất cho người dùng.' },
                      { title: 'Step 7: Tác tử trích xuất và diễn giải', description: 'Extractor và Abstracter là 2 tác tử cốt lõi của hệ thống chuyên tạo bản tóm tắt trích xuất và diễn giải. Tác tử được liên kết với Coordinator Agent để xử lý nhiệm vụ trích xuất văn bản và diễn giải. Bên cạnh đó, các tác tử được liên kết và tích hợp với hai mô hình cốt lõi đã được huấn luyện và tinh chỉnh.' },
                      { title: 'Step 8: Quá trình phản hồi bản tóm tắt', description: 'Bản tóm tắt được tạo ra sẽ được kiểm tra, chọn lọc và đánh giá bởi Grade Calibrator Agent, Evaluator Agent. Bản tóm tắt đạt chuẩn được Aggregator Agent tổng hợp và đưa ra kết quả cuối cùng đáp ứng cả về chất lượng, độ dài, từ vựng và nội dung văn bản. Thêm vào đó để bản tóm tắt được rõ ràng, minh bạch và thuyết phục, kết quả sẽ được kiểm nghiệm qua các thang đo như: F1, ROUGE-1, ROUGE-L, BERTScore,...' },
                      { title: 'Step 9: Kết quả', description: 'Người dùng sẽ nhận được kết quả là bản tóm tắt cùng với các hình ảnh minh họa tiếp diễn theo mạch truyện. Vừa đáp ứng được nhu cầu người dùng, vừa đảm bảo độ chính xác, độ tin cậy và độ khách quan cao.' },
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
