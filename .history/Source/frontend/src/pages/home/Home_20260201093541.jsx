import Particles from './Particles';

function Home() {
  return (
    <div style={{ width: '100%', height: '600px', position: 'relative' }}>
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

export default Home
