import './summary.css';
import { GravityStarsBackground } from '../../components/animate-ui/components/backgrounds/gravity-stars';

export default function Summary() {
  return (
    <div style={{ width: '100%', minHeight: '100vh', position: 'relative' }}>
      <GravityStarsBackground 
        className="gravity-stars-bg"
        starsCount={300}
        starsSize={4}
        starsOpacity={0.8}
        glowIntensity={20}
        movementSpeed={0.4}
        mouseInfluence={150}
        mouseGravity="attract"
        gravityStrength={100}
      />
      <div style={{ position: 'relative', zIndex: 1, padding: '2rem' }}>
        <h1>Summary Page</h1>
        <p>This is the Summary page content.</p>
      </div>
    </div>
  );
}
