import { memo } from 'react';
import { getBezierPath } from 'reactflow';
import { EDGE_STATES, COLORS } from './utils/masFlowConfig';

const MASEdge = ({
  id,
  sourceX,
  sourceY,
  targetX,
  targetY,
  sourcePosition,
  targetPosition,
  style = {},
  data,
  markerEnd,
}) => {
  const [edgePath] = getBezierPath({
    sourceX,
    sourceY,
    sourcePosition,
    targetX,
    targetY,
    targetPosition,
  });

  const state = data?.state || EDGE_STATES.PENDING;
  const isConditional = data?.conditional || false;

  // Get edge styles based on state
  const getEdgeStyles = () => {
    const baseStyles = {
      strokeWidth: 2,
      fill: 'none',
      ...style,
    };

    switch (state) {
      case EDGE_STATES.PENDING:
        return {
          ...baseStyles,
          stroke: COLORS.idle,
          strokeDasharray: isConditional ? '5,5' : 'none',
          opacity: 0.3,
        };
      case EDGE_STATES.ACTIVE:
        return {
          ...baseStyles,
          stroke: COLORS.active,
          strokeWidth: 3,
          strokeDasharray: isConditional ? '10,5' : '10,5',
          opacity: 1,
          filter: `drop-shadow(0 0 4px ${COLORS.active})`,
          animation: 'flow 1s linear infinite',
        };
      case EDGE_STATES.COMPLETED:
        return {
          ...baseStyles,
          stroke: COLORS.completed,
          strokeDasharray: isConditional ? '5,5' : 'none',
          opacity: 0.8,
        };
      default:
        return baseStyles;
    }
  };

  return (
    <>
      <defs>
        <style>
          {`
            @keyframes flow {
              from {
                stroke-dashoffset: 0;
              }
              to {
                stroke-dashoffset: 20;
              }
            }
          `}
        </style>
      </defs>
      <path
        id={id}
        className="react-flow__edge-path"
        d={edgePath}
        markerEnd={markerEnd}
        style={getEdgeStyles()}
      />
    </>
  );
};

export default memo(MASEdge);
