import { useMemo, useState, useCallback } from 'react';
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  ReactFlowProvider,
} from 'reactflow';
import 'reactflow/dist/style.css';
import MASNode from './MASNode';
import MASEdge from './MASEdge';
import ControlPanel from './ControlPanel';
import Legend from './Legend';
import InfoPanel from './InfoPanel';
import { MAS_NODES, MAS_EDGES } from './utils/masFlowConfig';
import { calculateHierarchicalLayout, getDefaultLayoutOptions } from './utils/masFlowLayout';
import { useMASState } from './hooks/useMASState';
import { useMASSimulation } from './hooks/useMASSimulation';
import { useMASRealTime } from './hooks/useMASRealTime';
import { validateMASResponse } from './utils/errorHandler';

// Register custom node and edge types
const nodeTypes = {
  masNode: MASNode,
};

const edgeTypes = {
  masEdge: MASEdge,
};

function MASFlowInner({ masResponse = null }) {
  // Calculate layout
  const layoutOptions = getDefaultLayoutOptions();
  const initialNodes = useMemo(() => {
    const nodesWithPositions = calculateHierarchicalLayout(MAS_NODES, layoutOptions);
    return nodesWithPositions.map((node) => ({
      ...node,
      type: 'masNode',
      data: {
        ...node,
        state: 'idle', // Will be updated by simulation/real-time
      },
    }));
  }, []);

  const initialEdges = useMemo(() => {
    return MAS_EDGES.map((edge) => ({
      ...edge,
      type: 'masEdge',
      data: {
        ...edge,
        state: 'pending',
      },
      style: {
        strokeWidth: 2,
      },
      markerEnd: {
        type: 'arrowclosed',
        color: '#9CA3AF',
      },
    }));
  }, []);

  // Use ReactFlow's built-in state management
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  // Create masState wrapper that syncs with ReactFlow state
  // Use useCallback to create stable function references
  const updateNodeState = useCallback((nodeId, newState) => {
    setNodes((prevNodes) =>
      prevNodes.map((node) =>
        node.id === nodeId
          ? {
              ...node,
              data: {
                ...node.data,
                state: newState,
              },
            }
          : node
      )
    );
  }, [setNodes]);

  const updateNodesState = useCallback((nodeUpdates) => {
    setNodes((prevNodes) =>
      prevNodes.map((node) => {
        const update = nodeUpdates.find((u) => u.id === node.id);
        if (update) {
          return {
            ...node,
            data: {
              ...node.data,
              state: update.state,
              ...(update.confidence !== undefined && { confidence: update.confidence }),
            },
          };
        }
        return node;
      })
    );
  }, [setNodes]);

  const updateEdgeState = useCallback((edgeId, newState) => {
    setEdges((prevEdges) =>
      prevEdges.map((edge) =>
        edge.id === edgeId
          ? {
              ...edge,
              data: {
                ...edge.data,
                state: newState,
              },
            }
          : edge
      )
    );
  }, [setEdges]);

  const updateEdgesState = useCallback((edgeUpdates) => {
    setEdges((prevEdges) =>
      prevEdges.map((edge) => {
        const update = edgeUpdates.find((u) => u.id === edge.id);
        if (update) {
          return {
            ...edge,
            data: {
              ...edge.data,
              state: update.state,
            },
          };
        }
        return edge;
      })
    );
  }, [setEdges]);

  const resetState = useCallback(() => {
    setNodes(initialNodes);
    setEdges(initialEdges);
  }, [setNodes, setEdges, initialNodes, initialEdges]);

  const masState = useMemo(() => {
    return {
      nodes,
      edges,
      setNodes,
      setEdges,
      updateNodeState,
      updateNodesState,
      updateEdgeState,
      updateEdgesState,
      resetState,
      getNode: (nodeId) => nodes.find((node) => node.id === nodeId),
      getEdge: (edgeId) => edges.find((edge) => edge.id === edgeId),
      getConnectedEdges: (nodeId, direction = 'both') => {
        return edges.filter((edge) => {
          if (direction === 'incoming') {
            return edge.target === nodeId;
          }
          if (direction === 'outgoing') {
            return edge.source === nodeId;
          }
          return edge.source === nodeId || edge.target === nodeId;
        });
      },
    };
  }, [nodes, edges, setNodes, setEdges, updateNodeState, updateNodesState, updateEdgeState, updateEdgesState, resetState]);

  // Use simulation hook
  const simulation = useMASSimulation(masState, masResponse);

  // Validate MAS response
  const validationResult = useMemo(() => {
    if (masResponse) {
      return validateMASResponse(masResponse);
    }
    return { valid: true };
  }, [masResponse]);

  // Use real-time updates hook (auto-applies when masResponse changes)
  // Only apply if response is valid
  useMASRealTime(masState, validationResult.valid ? masResponse : null);

  // Info panel state
  const [selectedNode, setSelectedNode] = useState(null);

  // Handle node click
  const onNodeClick = useCallback((event, node) => {
    setSelectedNode(node);
  }, []);

  // Handle pane click to deselect
  const onPaneClick = useCallback(() => {
    setSelectedNode(null);
  }, []);

  return (
    <div style={{ width: '100%', height: '100%', backgroundColor: '#F9FAFB', position: 'relative' }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onNodeClick={onNodeClick}
        onPaneClick={onPaneClick}
        nodeTypes={nodeTypes}
        edgeTypes={edgeTypes}
        fitView
        fitViewOptions={{ padding: 0.2 }}
        minZoom={0.2}
        maxZoom={1.5}
        proOptions={{ hideAttribution: true }}
      >
        <Background color="#E5E7EB" gap={16} />
        <Controls />
        <MiniMap
          nodeColor={(node) => {
            const state = node.data?.state || 'idle';
            const colors = {
              idle: '#9CA3AF',
              active: '#F59E0B',
              completed: '#10B981',
              error: '#EF4444',
              skipped: '#D1D5DB',
            };
            return colors[state] || '#9CA3AF';
          }}
          maskColor="rgba(0, 0, 0, 0.1)"
        />
      </ReactFlow>
      
      {/* Control Panel */}
      <ControlPanel
        isPlaying={simulation.isPlaying}
        isPaused={simulation.isPaused}
        speed={simulation.speed}
        onPlay={simulation.startSimulation}
        onPause={simulation.pauseSimulation}
        onResume={simulation.resumeSimulation}
        onStop={simulation.stopSimulation}
        onReset={simulation.resetSimulation}
        onSpeedChange={simulation.changeSpeed}
      />

      {/* Legend */}
      <Legend />

      {/* Info Panel */}
      {selectedNode && (
        <InfoPanel
          activeNode={selectedNode}
          masResponse={masResponse}
          onClose={() => setSelectedNode(null)}
        />
      )}
      
      <style>
        {`
          .react-flow__attribution {
            display: none !important;
          }
        `}
      </style>
    </div>
  );
}

export default function MASFlow({ masResponse = null }) {
  return (
    <ReactFlowProvider>
      <MASFlowInner masResponse={masResponse} />
    </ReactFlowProvider>
  );
}
