import Home from './pages/home/Home.jsx'
import Particles from './components/Particles.jsx'
export default function App() {
  return (
    <div style={{ width: '100%', height: '100vh', position: 'relative' }}>
      <Particles
        particleColors={["#00CBFF91", "#00FF0091", "#0000FF91", "#FF000091", "#FFFF0091", "#FF00FF91", "#00FFFF91"]}
        particleCount={700}
        particleSpread={10}
        speed={0.2}
        particleBaseSize={100}
        moveParticlesOnHover
        alphaParticles={false}
        disableRotation={false}
        pixelRatio={1}
      />
    </div>
  )
}
