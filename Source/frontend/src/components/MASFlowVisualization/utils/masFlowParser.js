// MAS Flow Parser - Parse MAS response to extract agent execution info

/**
 * Parse agent_confidences from MAS response
 * @param {Object} masResponse - Response from MAS API
 * @returns {Object} Map of agent types to confidence scores
 */
export function parseAgentConfidences(masResponse) {
  const confidences = {};
  
  try {
    const agentConfs = masResponse.agent_confidences;
    if (typeof agentConfs === 'string') {
      const parsed = JSON.parse(agentConfs);
      Object.assign(confidences, parsed);
    } else if (typeof agentConfs === 'object' && agentConfs !== null) {
      Object.assign(confidences, agentConfs);
    }
  } catch (e) {
    console.warn('Failed to parse agent_confidences:', e);
  }

  return confidences;
}

/**
 * Determine which nodes were executed based on MAS response
 * @param {Object} masResponse - Response from MAS API
 * @returns {Array} Array of node IDs that were executed
 */
export function getExecutedNodes(masResponse) {
  const executedNodes = [];
  const confidences = parseAgentConfidences(masResponse);

  // Map agent names to node IDs
  const agentToNodeMap = {
    intent_agent: 'intent',
    planning_agent: 'planning',
    abstractive_agent: 'abstractive',
    extractive_agent: 'extractive',
    evaluation_agent: 'evaluate',
    image2text_agent: 'ocr',
  };

  // Check which agents have confidence scores (meaning they executed)
  Object.keys(confidences).forEach((agentName) => {
    const nodeId = agentToNodeMap[agentName];
    if (nodeId && !executedNodes.includes(nodeId)) {
      executedNodes.push(nodeId);
    }
  });

  // Check for clarification (if clarification_needed is false, it ran)
  if (masResponse.clarification_needed === false) {
    executedNodes.push('clarification');
  }

  return executedNodes;
}

/**
 * Determine execution order from MAS response
 * @param {Object} masResponse - Response from MAS API
 * @returns {Array} Array of node IDs in execution order
 */
export function getExecutionOrder(masResponse) {
  // Default order based on MAS flow
  const defaultOrder = ['intent', 'clarification', 'planning', 'agent_memory', 'ocr', 'abstractive', 'extractive', 'evaluate'];
  
  const executedNodes = getExecutedNodes(masResponse);
  
  // Filter to only include executed nodes and maintain order
  return defaultOrder.filter((nodeId) => executedNodes.includes(nodeId));
}

/**
 * Check if OCR was executed (has image_path or image2text_agent confidence)
 */
export function wasOCRExecuted(masResponse) {
  const confidences = parseAgentConfidences(masResponse);
  return 'image2text_agent' in confidences || !!masResponse.image_path;
}

/**
 * Check if clarification was needed (and thus executed)
 */
export function wasClarificationExecuted(masResponse) {
  return masResponse.clarification_needed === false;
}
