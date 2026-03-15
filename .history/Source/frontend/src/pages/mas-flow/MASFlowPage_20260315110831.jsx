import { useState } from 'react';
import MASFlow from '../../components/MASFlowVisualization/MASFlow';
import './MASFlowPage.css';

export default function MASFlowPage() {
  const [masResponse, setMasResponse] = useState(null);

  // Mock MAS response for testing
  const handleTestFlow = () => {
    setMasResponse({
      agent_confidences: {
        intent_agent: 0.95,
        planning_agent: 0.88,
        abstractive_agent: 0.92,
        evaluation_agent: 0.85,
      },
      clarification_needed: false,
    });
  };

  return (
    <div style={{ width: '100%', height: '100vh', display: 'flex', flexDirection: 'column' }}>
      <div
        style={{
          padding: '16px',
          backgroundColor: '#FFFFFF',
          borderBottom: '1px solid #E5E7EB',
          display: 'flex',
          gap: '12px',
          alignItems: 'center',
        }}
      >
        <h1 style={{ margin: 0, fontSize: '24px', fontWeight: 600 }}>MAS Flow Visualization</h1>
        <button
          onClick={handleTestFlow}
          style={{
            padding: '8px 16px',
            backgroundColor: '#3B82F6',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer',
            fontSize: '14px',
          }}
        >
          Test Flow
        </button>
      </div>
      <div style={{ flex: 1, position: 'relative' }}>
        <MASFlow masResponse={masResponse} />
      </div>
    </div>
  );
}
