import Home from './pages/home/Home.jsx'
import Particles from './components/Particles.jsx'
import Iridescence from './components/Iridescence.jsx'
export default function App() {
  return (
    <div style={{ width: '100%', height: '100vh', position: 'relative' }}>
      <Iridescence
        color={[0.5, 0.6, 0.8]}
        mouseReact
        amplitude={0.1}
        speed={1}
      />
    </div>
  )
}
