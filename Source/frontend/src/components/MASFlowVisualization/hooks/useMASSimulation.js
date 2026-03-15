import { useState, useCallback, useRef, useEffect } from 'react';
import { NODE_STATES, EDGE_STATES, MAS_NODES } from '../utils/masFlowConfig';
import { getExecutionOrder, getExecutedNodes } from '../utils/masFlowParser';

/**
 * Hook for MAS Flow simulation
 */
export function useMASSimulation(masState, masResponse = null) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [speed, setSpeed] = useState(1); // 0.5x, 1x, 2x
  const [currentStep, setCurrentStep] = useState(0);
  const [executionOrder, setExecutionOrder] = useState([]);
  const timeoutRefs = useRef([]);

  /**
   * Get execution order from MAS response or use default
   */
  useEffect(() => {
    if (masResponse) {
      const order = getExecutionOrder(masResponse);
      setExecutionOrder(order);
    } else {
      // Default execution order (simulation without real response)
      setExecutionOrder(['intent', 'clarification', 'planning', 'agent_memory', 'abstractive', 'evaluate']);
    }
  }, [masResponse]);

  /**
   * Clear all timeouts
   */
  const clearAllTimeouts = useCallback(() => {
    timeoutRefs.current.forEach((timeout) => clearTimeout(timeout));
    timeoutRefs.current = [];
  }, []);

  /**
   * Get estimated time for a node
   */
  const getNodeEstimatedTime = useCallback((nodeId) => {
    const node = MAS_NODES.find((n) => n.id === nodeId);
    return node?.estimatedTime || 1000;
  }, []);

  /**
   * Activate a node and its incoming edge
   */
  const activateNode = useCallback(
    (nodeId, stepIndex) => {
      // Find incoming edge using getConnectedEdges
      const connectedEdges = masState.getConnectedEdges(nodeId, 'incoming');
      const incomingEdge = connectedEdges[0]; // Take first incoming edge

      // Activate incoming edge
      if (incomingEdge) {
        masState.updateEdgeState(incomingEdge.id, EDGE_STATES.ACTIVE);
        
        // Complete edge after a short delay
        const edgeTimeout = setTimeout(() => {
          masState.updateEdgeState(incomingEdge.id, EDGE_STATES.COMPLETED);
        }, 300 / speed);
        timeoutRefs.current.push(edgeTimeout);
      }

      // Activate node
      masState.updateNodeState(nodeId, NODE_STATES.ACTIVE);

      // Get estimated execution time
      const estimatedTime = getNodeEstimatedTime(nodeId);

      // Complete node after estimated time
      const nodeTimeout = setTimeout(() => {
        masState.updateNodeState(nodeId, NODE_STATES.COMPLETED);

        // Activate outgoing edges
        const outgoingEdges = masState.getConnectedEdges(nodeId, 'outgoing');
        outgoingEdges.forEach((edge) => {
          masState.updateEdgeState(edge.id, EDGE_STATES.ACTIVE);
          
          // Complete edge after a short delay
          const edgeCompleteTimeout = setTimeout(() => {
            masState.updateEdgeState(edge.id, EDGE_STATES.COMPLETED);
          }, 300 / speed);
          timeoutRefs.current.push(edgeCompleteTimeout);
        });

        // Move to next step
        if (stepIndex < executionOrder.length - 1) {
          const nextNodeId = executionOrder[stepIndex + 1];
          const nextStepDelay = 200 / speed; // Small delay between nodes
          const nextStepTimeout = setTimeout(() => {
            activateNode(nextNodeId, stepIndex + 1);
          }, nextStepDelay);
          timeoutRefs.current.push(nextStepTimeout);
        } else {
          // Simulation complete
          setIsPlaying(false);
          setCurrentStep(0);
        }
      }, estimatedTime / speed);

      timeoutRefs.current.push(nodeTimeout);
      setCurrentStep(stepIndex);
    },
    [masState, executionOrder, speed, getNodeEstimatedTime]
  );

  /**
   * Start simulation
   */
  const startSimulation = useCallback(() => {
    if (isPlaying) return;

    // Reset state first
    masState.resetState();
    setCurrentStep(0);
    clearAllTimeouts();

    setIsPlaying(true);
    setIsPaused(false);

    // Start with first node
    if (executionOrder.length > 0) {
      const firstNodeId = executionOrder[0];
      activateNode(firstNodeId, 0);
    }
  }, [isPlaying, executionOrder, masState, activateNode, clearAllTimeouts]);

  /**
   * Pause simulation
   */
  const pauseSimulation = useCallback(() => {
    setIsPaused(true);
    clearAllTimeouts();
  }, [clearAllTimeouts]);

  /**
   * Resume simulation
   */
  const resumeSimulation = useCallback(() => {
    if (!isPaused || !isPlaying) return;

    setIsPaused(false);

    // Continue from current step
    if (currentStep < executionOrder.length) {
      const currentNodeId = executionOrder[currentStep];
      activateNode(currentNodeId, currentStep);
    }
  }, [isPaused, isPlaying, currentStep, executionOrder, activateNode]);

  /**
   * Stop simulation
   */
  const stopSimulation = useCallback(() => {
    setIsPlaying(false);
    setIsPaused(false);
    setCurrentStep(0);
    clearAllTimeouts();
    masState.resetState();
  }, [masState, clearAllTimeouts]);

  /**
   * Reset simulation
   */
  const resetSimulation = useCallback(() => {
    stopSimulation();
  }, [stopSimulation]);

  /**
   * Change simulation speed
   */
  const changeSpeed = useCallback((newSpeed) => {
    setSpeed(newSpeed);
    // If currently playing, restart with new speed
    if (isPlaying && !isPaused) {
      const currentStepIndex = currentStep;
      stopSimulation();
      setTimeout(() => {
        // Restart from beginning with new speed
        startSimulation();
      }, 100);
    }
  }, [isPlaying, isPaused, currentStep, stopSimulation, startSimulation]);

  /**
   * Cleanup on unmount
   */
  useEffect(() => {
    return () => {
      clearAllTimeouts();
    };
  }, [clearAllTimeouts]);

  return {
    isPlaying,
    isPaused,
    speed,
    currentStep,
    executionOrder,
    startSimulation,
    pauseSimulation,
    resumeSimulation,
    stopSimulation,
    resetSimulation,
    changeSpeed,
  };
}
