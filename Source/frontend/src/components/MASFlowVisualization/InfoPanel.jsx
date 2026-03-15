import { X, Clock, CheckCircle, AlertCircle } from 'lucide-react';
import { useState, useEffect } from 'react';
import { NODE_STATES } from './utils/masFlowConfig';
import './InfoPanel.css';

export default function InfoPanel({ activeNode, masResponse, onClose }) {
  const [confidence, setConfidence] = useState(null);
  const [executionTime, setExecutionTime] = useState(null);

  useEffect(() => {
    if (!activeNode || !masResponse) {
      setConfidence(null);
      setExecutionTime(null);
      return;
    }

    // Parse confidence from agent_confidences
    try {
      const agentConfs = masResponse.agent_confidences;
      if (agentConfs) {
        const confidences =
          typeof agentConfs === 'string' ? JSON.parse(agentConfs) : agentConfs;

        // Map node ID to agent name
        const nodeToAgentMap = {
          intent: 'intent_agent',
          planning: 'planning_agent',
          abstractive: 'abstractive_agent',
          extractive: 'extractive_agent',
          evaluate: 'evaluation_agent',
          ocr: 'image2text_agent',
        };

        const agentName = nodeToAgentMap[activeNode.id];
        if (agentName && confidences[agentName] !== undefined) {
          setConfidence(confidences[agentName]);
        }
      }
    } catch (e) {
      console.warn('Failed to parse confidence:', e);
    }

    // Mock execution time (in real app, this would come from MAS response)
    if (activeNode.data?.estimatedTime) {
      setExecutionTime(activeNode.data.estimatedTime);
    }
  }, [activeNode, masResponse]);

  if (!activeNode) return null;

  const state = activeNode.data?.state || NODE_STATES.IDLE;
  const isActive = state === NODE_STATES.ACTIVE;
  const isCompleted = state === NODE_STATES.COMPLETED;
  const hasError = state === NODE_STATES.ERROR;

  return (
    <div className="mas-flow-info-panel">
      <div className="mas-flow-info-panel-header">
        <div className="mas-flow-info-panel-title">
          {activeNode.data?.icon && (
            <span style={{ fontSize: '20px', marginRight: '8px' }}>
              {activeNode.data.icon}
            </span>
          )}
          <span>{activeNode.data?.label || activeNode.id}</span>
        </div>
        <button
          className="mas-flow-info-panel-close"
          onClick={onClose}
          title="Đóng"
        >
          <X size={16} />
        </button>
      </div>

      <div className="mas-flow-info-panel-content">
        {activeNode.data?.description && (
          <div className="mas-flow-info-panel-section">
            <div className="mas-flow-info-panel-label">Mô tả</div>
            <div className="mas-flow-info-panel-value">
              {activeNode.data.description}
            </div>
          </div>
        )}

        <div className="mas-flow-info-panel-section">
          <div className="mas-flow-info-panel-label">Trạng thái</div>
          <div className="mas-flow-info-panel-value">
            <div className="mas-flow-info-panel-status">
              {isActive && (
                <>
                  <Clock size={14} className="mas-flow-info-panel-icon-active" />
                  <span>Đang xử lý...</span>
                </>
              )}
              {isCompleted && (
                <>
                  <CheckCircle size={14} className="mas-flow-info-panel-icon-completed" />
                  <span>Hoàn thành</span>
                </>
              )}
              {hasError && (
                <>
                  <AlertCircle size={14} className="mas-flow-info-panel-icon-error" />
                  <span>Lỗi</span>
                </>
              )}
              {!isActive && !isCompleted && !hasError && (
                <span>Chưa chạy</span>
              )}
            </div>
          </div>
        </div>

        {confidence !== null && (
          <div className="mas-flow-info-panel-section">
            <div className="mas-flow-info-panel-label">Độ tin cậy</div>
            <div className="mas-flow-info-panel-value">
              <div className="mas-flow-info-panel-confidence">
                <div className="mas-flow-info-panel-confidence-bar">
                  <div
                    className="mas-flow-info-panel-confidence-fill"
                    style={{ width: `${confidence * 100}%` }}
                  />
                </div>
                <span className="mas-flow-info-panel-confidence-text">
                  {(confidence * 100).toFixed(1)}%
                </span>
              </div>
            </div>
          </div>
        )}

        {executionTime && (
          <div className="mas-flow-info-panel-section">
            <div className="mas-flow-info-panel-label">Thời gian ước tính</div>
            <div className="mas-flow-info-panel-value">
              {(executionTime / 1000).toFixed(1)}s
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
