import './summary.css';
import GravityStarsBackground from '../../components/GravityStarsBackground';

export default function Summary() {
  return (
    <div>
      <GravityStarsBackground />
    <div style={{ width: '100%', minHeight: '100vh', position: 'relative' }}>
      <div style={{ padding: '2rem' }}>
        <h1>Summary Page</h1>
          <p>This is the Summary page content.</p>
        </div>
      </div>
    </div>
  );
}
