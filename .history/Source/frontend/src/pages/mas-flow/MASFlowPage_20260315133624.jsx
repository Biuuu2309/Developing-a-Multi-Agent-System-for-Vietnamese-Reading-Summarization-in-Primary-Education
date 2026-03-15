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
      intent: JSON.stringify({
        summarization_type: 'abstractive',
        grade_level: 1,
        intent: 'summarize',
      }),
      agent_memories: JSON.stringify({
        intent_agent: { has_memory: true },
        planning_agent: { has_memory: true },
        abstractive_agent: { has_memory: true },
      }),
    });
  };

  // Mock response with extractive agent
  const handleTestExtractive = () => {
    setMasResponse({
      agent_confidences: {
        intent_agent: 0.93,
        planning_agent: 0.85,
        extractive_agent: 0.90,
        evaluation_agent: 0.82,
      },
      clarification_needed: false,
      intent: JSON.stringify({
        summarization_type: 'extractive',
        intent: 'summarize',
      }),
      agent_memories: JSON.stringify({
        intent_agent: { has_memory: true },
        planning_agent: { has_memory: true },
        extractive_agent: { has_memory: true },
      }),
    });
  };

  // Mock response with OCR
  const handleTestOCR = () => {
    setMasResponse({
      agent_confidences: {
        intent_agent: 0.94,
        planning_agent: 0.87,
        image2text_agent: 0.91,
        abstractive_agent: 0.89,
        evaluation_agent: 0.84,
      },
      clarification_needed: false,
      intent: JSON.stringify({
        summarization_type: 'abstractive',
        grade_level: 2,
        intent: 'summarize',
      }),
      image_path: '/path/to/image.jpg',
      agent_memories: JSON.stringify({
        intent_agent: { has_memory: true },
        planning_agent: { has_memory: true },
        image2text_agent: { has_memory: true },
        abstractive_agent: { has_memory: true },
      }),
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
        <div style={{ display: 'flex', gap: '8px' }}>
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
            Test Abstractive
          </button>
          <button
            onClick={handleTestExtractive}
            style={{
              padding: '8px 16px',
              backgroundColor: '#10B981',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '14px',
            }}
          >
            Test Extractive
          </button>
          <button
            onClick={handleTestOCR}
            style={{
              padding: '8px 16px',
              backgroundColor: '#F59E0B',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '14px',
            }}
          >
            Test with OCR
          </button>
        </div>
      </div>
      <div style={{ flex: 1, position: 'relative' }}>
        <MASFlow masResponse={masResponse} />
      </div>
    </div>
  );
}
