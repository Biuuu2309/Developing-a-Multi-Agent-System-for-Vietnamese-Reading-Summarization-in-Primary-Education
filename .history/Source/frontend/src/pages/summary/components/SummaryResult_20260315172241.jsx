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

  // Parse evaluation for display
  let evaluationData = null;
  try {
    if (result.evaluation) {
      evaluationData = typeof result.evaluation === 'string'
        ? JSON.parse(result.evaluation)
        : result.evaluation;
    }
  } catch (e) {
    console.warn('Failed to parse evaluation:', e);
  }

  const getEvaluationDisplay = () => {
    if (!evaluationData) return null;

    // Important metrics to highlight
    const importantMetrics = {
      rouge1_f1: evaluationData.rouge1_f1,
      rougeL_f1: evaluationData.rougeL_f1,
      bertscore_f1: evaluationData.bertscore_f1,
      difficulty_level: evaluationData.difficulty_level,
    };

    // Other metrics
    const otherMetrics = Object.entries(evaluationData)
      .filter(([key]) => !['rouge1_f1', 'rougeL_f1', 'bertscore_f1', 'difficulty_level'].includes(key))
      .filter(([, value]) => value !== null && value !== undefined);

    return (
      <div className="result-evaluation">
        <h4>
          <Star size={18} />
          Đánh giá
        </h4>
        
        {/* Important Metrics */}
        <div className="important-metrics">
          {importantMetrics.rouge1_f1 !== undefined && importantMetrics.rouge1_f1 !== null && (
            <div className="metric-card important">
              <div className="metric-label">ROUGE-1 F1</div>
              <div className="metric-value">{typeof importantMetrics.rouge1_f1 === 'number' 
                ? (importantMetrics.rouge1_f1 * 100).toFixed(2) + '%' 
                : importantMetrics.rouge1_f1}</div>
            </div>
          )}
          {importantMetrics.rougeL_f1 !== undefined && importantMetrics.rougeL_f1 !== null && (
            <div className="metric-card important">
              <div className="metric-label">ROUGE-L F1</div>
              <div className="metric-value">{typeof importantMetrics.rougeL_f1 === 'number' 
                ? (importantMetrics.rougeL_f1 * 100).toFixed(2) + '%' 
                : importantMetrics.rougeL_f1}</div>
            </div>
          )}
          {importantMetrics.bertscore_f1 !== undefined && importantMetrics.bertscore_f1 !== null && (
            <div className="metric-card important">
              <div className="metric-label">BERTScore F1</div>
              <div className="metric-value">{typeof importantMetrics.bertscore_f1 === 'number' 
                ? (importantMetrics.bertscore_f1 * 100).toFixed(2) + '%' 
                : importantMetrics.bertscore_f1}</div>
            </div>
          )}
          {importantMetrics.difficulty_level !== undefined && importantMetrics.difficulty_level !== null && (
            <div className="metric-card important">
              <div className="metric-label">Độ khó</div>
              <div className="metric-value">{importantMetrics.difficulty_level}</div>
            </div>
          )}
        </div>

        {/* Other Metrics */}
        {otherMetrics.length > 0 && (
          <div className="other-metrics">
            <details className="other-metrics-details">
              <summary className="other-metrics-summary">Các chỉ số khác</summary>
              <div className="other-metrics-grid">
                {otherMetrics.map(([key, value]) => (
                  <div key={key} className="metric-item">
                    <span className="metric-item-label">{key.replace(/_/g, ' ')}</span>
                    <span className="metric-item-value">
                      {typeof value === 'number' 
                        ? (value < 1 && value > 0 ? (value * 100).toFixed(2) + '%' : value.toFixed(2))
                        : String(value)}
                    </span>
                  </div>
                ))}
              </div>
            </details>
          </div>
        )}
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

      {/* Evaluation */}
      {getEvaluationDisplay()}
    </div>
  );
}
