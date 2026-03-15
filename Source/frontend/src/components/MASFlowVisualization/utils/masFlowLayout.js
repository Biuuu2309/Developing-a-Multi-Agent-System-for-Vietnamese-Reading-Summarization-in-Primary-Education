// MAS Flow Layout - Hierarchical layout calculation

/**
 * Calculate hierarchical layout positions for nodes
 * @param {Array} nodes - Array of node definitions
 * @param {Object} options - Layout options
 * @returns {Array} Nodes with calculated positions
 */
export function calculateHierarchicalLayout(nodes, options = {}) {
  const {
    nodeWidth = 200,
    nodeHeight = 100,
    horizontalSpacing = 300,
    verticalSpacing = 200,
    startX = 100,
    startY = 100,
  } = options;

  // Define layers based on MAS flow
  const layers = [
    ['intent'], // Layer 0
    ['clarification'], // Layer 1
    ['planning', 'agent_memory'], // Layer 2 (parallel)
    ['ocr'], // Layer 3
    ['abstractive', 'extractive'], // Layer 4 (parallel - chỉ 1 trong 2 chạy)
    ['evaluate'], // Layer 5
  ];

  const positionedNodes = [];
  let currentY = startY;

  layers.forEach((layer, layerIndex) => {
    const nodesInLayer = layer.length;
    const totalWidth = (nodesInLayer - 1) * horizontalSpacing;
    const startXLayer = startX - totalWidth / 2;

    layer.forEach((nodeId, indexInLayer) => {
      const node = nodes.find((n) => n.id === nodeId);
      if (node) {
        const x = startXLayer + indexInLayer * horizontalSpacing;
        positionedNodes.push({
          ...node,
          position: { x, y: currentY },
          data: {
            ...node.data,
            layer: layerIndex,
          },
        });
      }
    });

    currentY += verticalSpacing;
  });

  return positionedNodes;
}

/**
 * Get default layout options
 */
export function getDefaultLayoutOptions() {
  return {
    nodeWidth: 200,
    nodeHeight: 100,
    horizontalSpacing: 300,
    verticalSpacing: 200,
    startX: 400,
    startY: 100,
  };
}

/**
 * Calculate layout for a specific viewport size
 */
export function calculateResponsiveLayout(viewportWidth, viewportHeight) {
  const baseOptions = getDefaultLayoutOptions();

  // Adjust spacing based on viewport
  if (viewportWidth < 768) {
    // Mobile
    return {
      ...baseOptions,
      horizontalSpacing: 200,
      verticalSpacing: 150,
      startX: viewportWidth / 2,
    };
  } else if (viewportWidth < 1024) {
    // Tablet
    return {
      ...baseOptions,
      horizontalSpacing: 250,
      verticalSpacing: 180,
      startX: viewportWidth / 2,
    };
  }

  // Desktop
  return baseOptions;
}
