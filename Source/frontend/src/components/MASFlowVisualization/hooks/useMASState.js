import { useState, useCallback } from 'react';
import { NODE_STATES, EDGE_STATES } from '../utils/masFlowConfig';

/**
 * Hook for managing MAS Flow state
 */
export function useMASState(initialNodes, initialEdges) {
  const [nodes, setNodes] = useState(initialNodes);
  const [edges, setEdges] = useState(initialEdges);

  /**
   * Update node state
   */
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
  }, []);

  /**
   * Update multiple nodes state
   */
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
            },
          };
        }
        return node;
      })
    );
  }, []);

  /**
   * Update edge state
   */
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
  }, []);

  /**
   * Update multiple edges state
   */
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
  }, []);

  /**
   * Reset all nodes and edges to initial state
   */
  const resetState = useCallback(() => {
    setNodes((prevNodes) =>
      prevNodes.map((node) => ({
        ...node,
        data: {
          ...node.data,
          state: NODE_STATES.IDLE,
        },
      }))
    );
    setEdges((prevEdges) =>
      prevEdges.map((edge) => ({
        ...edge,
        data: {
          ...edge.data,
          state: EDGE_STATES.PENDING,
        },
      }))
    );
  }, []);

  /**
   * Get node by ID
   */
  const getNode = useCallback(
    (nodeId) => {
      return nodes.find((node) => node.id === nodeId);
    },
    [nodes]
  );

  /**
   * Get edge by ID
   */
  const getEdge = useCallback(
    (edgeId) => {
      return edges.find((edge) => edge.id === edgeId);
    },
    [edges]
  );

  /**
   * Get edges connected to a node
   */
  const getConnectedEdges = useCallback(
    (nodeId, direction = 'both') => {
      // direction: 'incoming', 'outgoing', 'both'
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
    [edges]
  );

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
    getNode,
    getEdge,
    getConnectedEdges,
  };
}
