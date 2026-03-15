import { memo } from 'react';
import { Handle, Position } from 'reactflow';
import { NODE_STATES, COLORS } from './utils/masFlowConfig';

const MASNode = ({ data, selected }) => {
  const { label, icon, state = NODE_STATES.IDLE, description, confidence } = data;
  
  // Build tooltip content
  const tooltipContent = confidence !== undefined 
    ? `${label}\nĐộ tin cậy: ${(confidence * 100).toFixed(1)}%`
    : label;

  // Get colors based on state
  const getNodeStyles = () => {
    const baseStyles = {
      padding: '12px 16px',
      borderRadius: '12px',
      minWidth: '180px',
      textAlign: 'center',
      border: '2px solid',
      transition: 'all 0.3s ease',
      position: 'relative',
      backgroundColor: '#FFFFFF',
      boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)',
    };

    switch (state) {
      case NODE_STATES.IDLE:
        return {
          ...baseStyles,
          borderColor: COLORS.idle,
          opacity: 0.5,
          backgroundColor: '#F9FAFB',
        };
      case NODE_STATES.ACTIVE:
        return {
          ...baseStyles,
          borderColor: COLORS.active,
          backgroundColor: '#FFFBEB',
          boxShadow: `0 0 20px ${COLORS.active}40`,
          animation: 'pulse 2s ease-in-out infinite',
        };
      case NODE_STATES.COMPLETED:
        return {
          ...baseStyles,
          borderColor: COLORS.completed,
          backgroundColor: '#ECFDF5',
          boxShadow: `0 0 15px ${COLORS.completed}30`,
        };
      case NODE_STATES.ERROR:
        return {
          ...baseStyles,
          borderColor: COLORS.error,
          backgroundColor: '#FEF2F2',
        };
      case NODE_STATES.SKIPPED:
        return {
          ...baseStyles,
          borderColor: COLORS.skipped,
          opacity: 0.3,
          backgroundColor: '#F9FAFB',
        };
      default:
        return baseStyles;
    }
  };

  const getIcon = () => {
    if (state === NODE_STATES.ACTIVE) {
      return '⏳'; // Spinner/loading icon
    }
    if (state === NODE_STATES.COMPLETED) {
      return '✓'; // Checkmark
    }
    if (state === NODE_STATES.ERROR) {
      return '✗'; // Error icon
    }
    return icon || '○';
  };

  return (
    <div 
      style={getNodeStyles()}
      title={tooltipContent}
    >
      <Handle type="target" position={Position.Top} style={{ background: '#555' }} />
      
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '8px' }}>
        <div style={{ fontSize: '24px' }}>{getIcon()}</div>
        <div style={{ fontWeight: 600, fontSize: '14px', color: '#1F2937' }}>
          {label}
        </div>
        {description && (
          <div style={{ fontSize: '11px', color: '#6B7280', marginTop: '-4px' }}>
            {description}
          </div>
        )}
        {confidence !== undefined && (
          <div style={{ fontSize: '10px', color: '#6B7280', marginTop: '-4px' }}>
            {(confidence * 100).toFixed(0)}%
          </div>
        )}
      </div>

      <Handle type="source" position={Position.Bottom} style={{ background: '#555' }} />
      
      <style>
        {`
          @keyframes pulse {
            0%, 100% {
              transform: scale(1);
              opacity: 1;
            }
            50% {
              transform: scale(1.05);
              opacity: 0.9;
            }
          }
        `}
      </style>
    </div>
  );
};

export default memo(MASNode);
