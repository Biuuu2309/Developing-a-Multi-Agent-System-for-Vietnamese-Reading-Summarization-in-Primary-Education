import { useEffect, useCallback, useRef } from 'react';
import { NODE_STATES, EDGE_STATES, AGENT_TYPE_MAP } from '../utils/masFlowConfig';
import {
  parseAgentConfidences,
  getExecutedNodes,
  getExecutionOrder,
  wasOCRExecuted,
  wasClarificationExecuted,
} from '../utils/masFlowParser';

/**
 * Hook for real-time MAS updates from API response
 */
export function useMASRealTime(masState, masResponse) {
  /**
   * Determine which summarization agent was used
   */
  const getSummarizationAgent = useCallback((masResponse) => {
    if (!masResponse) return null;

    try {
      const intentStr = masResponse.intent;
      if (typeof intentStr === 'string') {
        const intent = JSON.parse(intentStr);
        return intent.summarization_type; // 'abstractive' or 'extractive'
      } else if (intentStr && typeof intentStr === 'object') {
        return intentStr.summarization_type;
      }
    } catch (e) {
      console.warn('Failed to parse intent:', e);
    }

    // Fallback: check agent_confidences
    const confidences = parseAgentConfidences(masResponse);
    if ('abstractive_agent' in confidences) {
      return 'abstractive';
    }
    if ('extractive_agent' in confidences) {
      return 'extractive';
    }

    return null;
  }, []);

  /**
   * Update nodes based on MAS response
   */
  const updateNodesFromResponse = useCallback(
    (masResponse, masStateRef) => {
      const currentMasState = masStateRef.current || masState;
      if (!masResponse) return;

      const confidences = parseAgentConfidences(masResponse);
      const executedNodes = getExecutedNodes(masResponse);
      const summarizationType = getSummarizationAgent(masResponse);
      const hasOCR = wasOCRExecuted(masResponse);
      const hasClarification = wasClarificationExecuted(masResponse);

      // Update all nodes based on execution
      const nodeUpdates = [];

      // Intent node - always executed if we have a response
      if (executedNodes.includes('intent') || 'intent_agent' in confidences) {
        nodeUpdates.push({ id: 'intent', state: NODE_STATES.COMPLETED });
      }

      // Clarification node
      if (masResponse.clarification_needed === undefined) {
        // No clarification info - assume it was skipped or not needed
        nodeUpdates.push({ id: 'clarification', state: NODE_STATES.SKIPPED });
      } else if (hasClarification) {
        nodeUpdates.push({ id: 'clarification', state: NODE_STATES.COMPLETED });
      } else if (masResponse.clarification_needed === true) {
        // Clarification was needed but not answered yet
        nodeUpdates.push({ id: 'clarification', state: NODE_STATES.ACTIVE });
      } else {
        // Clarification was skipped (clarification_needed === false but not executed)
        nodeUpdates.push({ id: 'clarification', state: NODE_STATES.SKIPPED });
      }

      // Planning node
      if (executedNodes.includes('planning') || 'planning_agent' in confidences) {
        nodeUpdates.push({ id: 'planning', state: NODE_STATES.COMPLETED });
      }

      // Agent Memory node
      // Check if agent_memories exists in response
      if (masResponse.agent_memories) {
        try {
          const agentMemories =
            typeof masResponse.agent_memories === 'string'
              ? JSON.parse(masResponse.agent_memories)
              : masResponse.agent_memories;
          if (agentMemories && Object.keys(agentMemories).length > 0) {
            nodeUpdates.push({ id: 'agent_memory', state: NODE_STATES.COMPLETED });
          } else {
            nodeUpdates.push({ id: 'agent_memory', state: NODE_STATES.SKIPPED });
          }
        } catch (e) {
          console.warn('Failed to parse agent_memories:', e);
          nodeUpdates.push({ id: 'agent_memory', state: NODE_STATES.SKIPPED });
        }
      } else {
        // No agent_memories in response - assume it was used but not explicitly returned
        // Or mark as skipped if we want to be strict
        nodeUpdates.push({ id: 'agent_memory', state: NODE_STATES.IDLE });
      }

      // OCR node
      if (hasOCR) {
        nodeUpdates.push({ id: 'ocr', state: NODE_STATES.COMPLETED });
      } else {
        nodeUpdates.push({ id: 'ocr', state: NODE_STATES.SKIPPED });
      }

      // Summarization nodes - only one should be completed
      if (summarizationType === 'abstractive') {
        nodeUpdates.push({ id: 'abstractive', state: NODE_STATES.COMPLETED });
        nodeUpdates.push({ id: 'extractive', state: NODE_STATES.SKIPPED });
      } else if (summarizationType === 'extractive') {
        nodeUpdates.push({ id: 'extractive', state: NODE_STATES.COMPLETED });
        nodeUpdates.push({ id: 'abstractive', state: NODE_STATES.SKIPPED });
      } else {
        // If we can't determine, check confidences
        if ('abstractive_agent' in confidences) {
          nodeUpdates.push({ id: 'abstractive', state: NODE_STATES.COMPLETED });
          nodeUpdates.push({ id: 'extractive', state: NODE_STATES.SKIPPED });
        } else if ('extractive_agent' in confidences) {
          nodeUpdates.push({ id: 'extractive', state: NODE_STATES.COMPLETED });
          nodeUpdates.push({ id: 'abstractive', state: NODE_STATES.SKIPPED });
        } else {
          // Both skipped if no summarization happened
          nodeUpdates.push({ id: 'abstractive', state: NODE_STATES.SKIPPED });
          nodeUpdates.push({ id: 'extractive', state: NODE_STATES.SKIPPED });
        }
      }

      // Evaluation node
      if (executedNodes.includes('evaluate') || 'evaluation_agent' in confidences) {
        nodeUpdates.push({ id: 'evaluate', state: NODE_STATES.COMPLETED });
      }

      // Apply updates and add confidence scores
      if (nodeUpdates.length > 0) {
        // Add confidence scores to node updates
        const nodeUpdatesWithConfidence = nodeUpdates.map((update) => {
          const nodeId = update.id;
          const nodeToAgentMap = {
            intent: 'intent_agent',
            planning: 'planning_agent',
            abstractive: 'abstractive_agent',
            extractive: 'extractive_agent',
            evaluate: 'evaluation_agent',
            ocr: 'image2text_agent',
          };
          const agentName = nodeToAgentMap[nodeId];
          const confidence = agentName && confidences[agentName];
          
          return {
            ...update,
            confidence,
          };
        });
        
        currentMasState.updateNodesState(nodeUpdatesWithConfidence);
      }
    },
    [masState, getSummarizationAgent]
  );

  /**
   * Update edges based on execution path
   */
  const updateEdgesFromResponse = useCallback(
    (masResponse, masStateRef) => {
      const currentMasState = masStateRef.current || masState;
      if (!masResponse) return;

      const executionOrder = getExecutionOrder(masResponse);
      const summarizationType = getSummarizationAgent(masResponse);
      const hasOCR = wasOCRExecuted(masResponse);
      const hasClarification = wasClarificationExecuted(masResponse);

      const edgeUpdates = [];

      // Intent -> Clarification
      // Always show this edge as completed if we have any response
      if (masResponse) {
        edgeUpdates.push({
          id: 'e-intent-clarification',
          state: EDGE_STATES.COMPLETED,
        });
      }

      // Clarification -> Planning
      if (hasClarification === false || masResponse.clarification_needed === false) {
        edgeUpdates.push({
          id: 'e-clarification-planning',
          state: EDGE_STATES.COMPLETED,
        });
      }

      // Planning -> Agent Memory
      if (masResponse.agent_memories) {
        edgeUpdates.push({
          id: 'e-planning-memory',
          state: EDGE_STATES.COMPLETED,
        });
        edgeUpdates.push({
          id: 'e-memory-planning',
          state: EDGE_STATES.COMPLETED,
        });
      }

      // Planning -> OCR (if OCR was executed)
      if (hasOCR) {
        edgeUpdates.push({
          id: 'e-planning-ocr',
          state: EDGE_STATES.COMPLETED,
        });
      }

      // Planning -> Summarize (if no OCR)
      if (!hasOCR) {
        if (summarizationType === 'abstractive') {
          edgeUpdates.push({
            id: 'e-planning-abstractive',
            state: EDGE_STATES.COMPLETED,
          });
        } else if (summarizationType === 'extractive') {
          edgeUpdates.push({
            id: 'e-planning-extractive',
            state: EDGE_STATES.COMPLETED,
          });
        }
      }

      // OCR -> Summarize
      if (hasOCR) {
        if (summarizationType === 'abstractive') {
          edgeUpdates.push({
            id: 'e-ocr-abstractive',
            state: EDGE_STATES.COMPLETED,
          });
        } else if (summarizationType === 'extractive') {
          edgeUpdates.push({
            id: 'e-ocr-extractive',
            state: EDGE_STATES.COMPLETED,
          });
        }
      }

      // Summarize -> Evaluate
      if (summarizationType === 'abstractive') {
        edgeUpdates.push({
          id: 'e-abstractive-evaluate',
          state: EDGE_STATES.COMPLETED,
        });
      } else if (summarizationType === 'extractive') {
        edgeUpdates.push({
          id: 'e-extractive-evaluate',
          state: EDGE_STATES.COMPLETED,
        });
      }

      // Evaluate -> Planning (self-improvement loop - check if needs_improvement)
      if (masResponse.needs_improvement === true) {
        edgeUpdates.push({
          id: 'e-evaluate-planning',
          state: EDGE_STATES.COMPLETED,
        });
      }

      // Apply updates
      if (edgeUpdates.length > 0) {
        currentMasState.updateEdgesState(edgeUpdates);
      }
    },
    [masState, getSummarizationAgent]
  );

  // Track processed response to avoid re-applying
  const processedResponseRef = useRef(null);
  const masStateRef = useRef(masState);

  // Keep masStateRef updated
  useEffect(() => {
    masStateRef.current = masState;
  }, [masState]);

  // Auto-apply updates when masResponse changes
  useEffect(() => {
    if (!masResponse) {
      processedResponseRef.current = null;
      return;
    }

    // Create a stable key from masResponse to check if it's already processed
    const responseKey = JSON.stringify({
      agent_confidences: masResponse.agent_confidences,
      clarification_needed: masResponse.clarification_needed,
      intent: masResponse.intent,
      agent_memories: masResponse.agent_memories,
      image_path: masResponse.image_path,
      needs_improvement: masResponse.needs_improvement,
    });

    // Only apply if this is a new response
    if (processedResponseRef.current !== responseKey) {
      processedResponseRef.current = responseKey;
      
      // Apply updates using ref to avoid dependency issues
      updateNodesFromResponse(masResponse, masStateRef);
      updateEdgesFromResponse(masResponse, masStateRef);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [masResponse]); // Only depend on masResponse

  return {
    updateNodesFromResponse,
    updateEdgesFromResponse,
  };
}
