import Home from './pages/home/Home.jsx'
import Particles from './components/Particles.jsx'
export default function App() {
  return (
    <div className="w-full h-full relative">
      <Particles
        particleColors={["#ffffff"]}
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
