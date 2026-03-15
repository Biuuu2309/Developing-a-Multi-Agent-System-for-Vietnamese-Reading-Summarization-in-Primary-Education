import { useState } from 'react';
import { Copy, Check, Download, Image as ImageIcon, Star } from 'lucide-react';
import './SummaryResult.css';

export default function SummaryResult({ result }) {
  const [copied, setCopied] = useState(false);

  if (!result) {
    return null;
  }
  
  // Check if we have summary text or summary_image_url
  const hasSummary = result.summary || result.summaryImageUrl;
  if (!hasSummary) {
    return null;
  }

  const handleCopy = async () => {
    try {
      // Get full summary text from all cards or fallback to result.summary
      let fullText = '';
      if (summaryCards.length > 0) {
        fullText = summaryCards.map(card => card.text).join('\n\n');
      } else {
        fullText = result.summary || '';
      }
      
      await navigator.clipboard.writeText(fullText);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  // Parse summary_image_url to create cards
  let summaryCards = [];
  
  try {
    if (result.summaryImageUrl) {
      const mapping = typeof result.summaryImageUrl === 'string'
        ? JSON.parse(result.summaryImageUrl)
        : result.summaryImageUrl;
      
      if (Array.isArray(mapping) && mapping.length > 0) {
        // Create cards from mapping
        summaryCards = mapping.map((item, index) => ({
          id: index,
          imageUrl: item.url || item.imageUrl,
          text: item.part || item.text || '',
        }));
      }
    }
    
    // Fallback: if no mapping but have summary text, create single card without image
    if (summaryCards.length === 0 && result.summary) {
      summaryCards = [{
        id: 0,
        imageUrl: null,
        text: result.summary,
      }];
    }
  } catch (e) {
    console.warn('Failed to parse summary_image_url:', e);
    // Fallback to single card with full summary
    if (result.summary) {
      summaryCards = [{
        id: 0,
        imageUrl: null,
        text: result.summary,
      }];
    }
  }

  // Parse agent confidences for display
  let confidences = {};
  try {
    if (result.agentConfidences) {
      confidences = typeof result.agentConfidences === 'string'
        ? JSON.parse(result.agentConfidences)
        : result.agentConfidences;
    }
  } catch (e) {
    console.warn('Failed to parse agent confidences:', e);
  }

  const getConfidenceDisplay = () => {
    const entries = Object.entries(confidences);
    if (entries.length === 0) return null;
    
    return (
      <div className="confidence-scores">
        <h4>Độ tin cậy của các Agent:</h4>
        <div className="confidence-list">
          {entries.map(([agent, confidence]) => (
            <div key={agent} className="confidence-item">
              <span className="agent-name">{agent.replace('_', ' ')}</span>
              <div className="confidence-bar-container">
                <div 
                  className="confidence-bar" 
                  style={{ width: `${(confidence * 100)}%` }}
                />
                <span className="confidence-value">{Math.round(confidence * 100)}%</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  };

  return (
    <div className="summary-result-container">
      <div className="result-header">
        <h3>Kết quả tóm tắt</h3>
        <div className="result-actions">
          <button 
            onClick={handleCopy} 
            className="action-btn"
            title="Sao chép"
          >
            {copied ? <Check size={18} /> : <Copy size={18} />}
            <span>{copied ? 'Đã sao chép' : 'Sao chép'}</span>
          </button>
        </div>
      </div>

      <div className="result-metadata">
        <div className="metadata-item">
          <span className="metadata-label">Loại tóm tắt:</span>
          <span className="metadata-value">
            {result.summaryType === 'abstractive' ? 'Tóm tắt diễn giải' : 'Tóm tắt trích xuất'}
          </span>
        </div>
        {result.gradeLevel && (
          <div className="metadata-item">
            <span className="metadata-label">Cấp lớp:</span>
            <span className="metadata-value">Lớp {result.gradeLevel}</span>
          </div>
        )}
        {result.status && (
          <div className="metadata-item">
            <span className="metadata-label">Trạng thái:</span>
            <span className={`metadata-value status-${result.status.toLowerCase()}`}>
              {result.status}
            </span>
          </div>
        )}
      </div>

      {/* Summary Cards */}
      {summaryCards.length > 0 && (
        <div className="result-content">
          <div className="summary-cards-container">
            {summaryCards.map((card) => (
              <div key={card.id} className="summary-card">
                {card.imageUrl && (
                  <div className="summary-card-image">
                    <img 
                      src={card.imageUrl} 
                      alt={`Summary part ${card.id + 1}`}
                      onError={(e) => {
                        e.target.style.display = 'none';
                        e.target.nextSibling.style.display = 'flex';
                      }}
                    />
                    <div className="image-placeholder" style={{ display: 'none' }}>
                      <ImageIcon size={48} />
                      <span>Không thể tải hình ảnh</span>
                    </div>
                  </div>
                )}
                {card.text && (
                  <div className="summary-card-text">
                    {card.text}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Agent Confidences */}
      {getConfidenceDisplay()}

      {/* Evaluation (if available) */}
      {result.evaluation && (
        <div className="result-evaluation">
          <h4>
            <Star size={18} />
            Đánh giá
          </h4>
          <div className="evaluation-content">
            {typeof result.evaluation === 'string' ? (
              <pre>{result.evaluation}</pre>
            ) : (
              <pre>{JSON.stringify(result.evaluation, null, 2)}</pre>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
