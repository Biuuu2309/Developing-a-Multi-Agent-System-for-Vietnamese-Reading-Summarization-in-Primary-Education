// MAS Flow Configuration - Node and Edge definitions

export const MAS_NODES = [
  {
    id: 'intent',
    label: 'Intent Agent',
    type: 'intent',
    description: 'Phân tích ý định người dùng',
    icon: '🎯',
    estimatedTime: 1000, // ms
  },
  {
    id: 'clarification',
    label: 'Clarification Agent',
    type: 'clarification',
    description: 'Làm rõ thông tin cần thiết',
    icon: '❓',
    estimatedTime: 800,
    conditional: true, // Có thể bị skip
  },
  {
    id: 'planning',
    label: 'Planning Agent',
    type: 'planning',
    description: 'Tạo kế hoạch thực thi',
    icon: '📋',
    estimatedTime: 2000,
  },
  {
    id: 'ocr',
    label: 'OCR Agent',
    type: 'ocr',
    description: 'Trích xuất text từ ảnh',
    icon: '🖼️',
    estimatedTime: 5000,
    conditional: true, // Chỉ chạy khi có image
  },
  {
    id: 'abstractive',
    label: 'Abstractive Agent',
    type: 'abstractive',
    description: 'Tóm tắt diễn giải',
    icon: '✨',
    estimatedTime: 4000,
    conditional: true, // Chỉ chạy khi strategy = abstractive
  },
  {
    id: 'extractive',
    label: 'Extractive Agent',
    type: 'extractive',
    description: 'Tóm tắt trích xuất',
    icon: '📄',
    estimatedTime: 3000,
    conditional: true, // Chỉ chạy khi strategy = extractive
  },
  {
    id: 'agent_memory',
    label: 'Agent Memory',
    type: 'memory',
    description: 'Lưu trữ và truy xuất kinh nghiệm',
    icon: '🧠',
    estimatedTime: 500,
  },
  {
    id: 'evaluate',
    label: 'Evaluation Agent',
    type: 'evaluation',
    description: 'Đánh giá chất lượng tóm tắt',
    icon: '⭐',
    estimatedTime: 2000,
  },
];

export const MAS_EDGES = [
  {
    id: 'e-intent-clarification',
    source: 'intent',
    target: 'clarification',
    type: 'default',
    animated: false,
  },
  {
    id: 'e-clarification-planning',
    source: 'clarification',
    target: 'planning',
    type: 'default',
    animated: false,
    conditional: true, // Có thể đi thẳng đến END
  },
  {
    id: 'e-planning-ocr',
    source: 'planning',
    target: 'ocr',
    type: 'default',
    animated: false,
    conditional: true, // Chỉ khi có image
  },
  {
    id: 'e-planning-abstractive',
    source: 'planning',
    target: 'abstractive',
    type: 'default',
    animated: false,
    conditional: true, // Khi strategy = abstractive và không có image
  },
  {
    id: 'e-planning-extractive',
    source: 'planning',
    target: 'extractive',
    type: 'default',
    animated: false,
    conditional: true, // Khi strategy = extractive và không có image
  },
  {
    id: 'e-ocr-abstractive',
    source: 'ocr',
    target: 'abstractive',
    type: 'default',
    animated: false,
    conditional: true, // Chỉ khi intent = summarize và strategy = abstractive
  },
  {
    id: 'e-ocr-extractive',
    source: 'ocr',
    target: 'extractive',
    type: 'default',
    animated: false,
    conditional: true, // Chỉ khi intent = summarize và strategy = extractive
  },
  {
    id: 'e-abstractive-evaluate',
    source: 'abstractive',
    target: 'evaluate',
    type: 'default',
    animated: false,
    conditional: true,
  },
  {
    id: 'e-extractive-evaluate',
    source: 'extractive',
    target: 'evaluate',
    type: 'default',
    animated: false,
    conditional: true,
  },
  {
    id: 'e-planning-memory',
    source: 'planning',
    target: 'agent_memory',
    type: 'default',
    animated: false,
  },
  {
    id: 'e-memory-planning',
    source: 'agent_memory',
    target: 'planning',
    type: 'default',
    animated: false,
  },
  {
    id: 'e-evaluate-planning',
    source: 'evaluate',
    target: 'planning',
    type: 'default',
    animated: false,
    conditional: true, // Self-improvement loop
  },
];

// Node states
export const NODE_STATES = {
  IDLE: 'idle',
  ACTIVE: 'active',
  COMPLETED: 'completed',
  ERROR: 'error',
  SKIPPED: 'skipped',
};

// Edge states
export const EDGE_STATES = {
  PENDING: 'pending',
  ACTIVE: 'active',
  COMPLETED: 'completed',
};

// Color scheme
export const COLORS = {
  idle: '#9CA3AF', // gray-400
  active: '#F59E0B', // amber-500
  completed: '#10B981', // emerald-500
  error: '#EF4444', // red-500
  skipped: '#D1D5DB', // gray-300
  background: '#1F2937', // gray-800 (dark theme)
  backgroundLight: '#F9FAFB', // gray-50 (light theme)
};

// Agent type mapping from MAS response
export const AGENT_TYPE_MAP = {
  intent_agent: 'intent',
  planning_agent: 'planning',
  abstractive_agent: 'abstractive',
  extractive_agent: 'extractive',
  evaluation_agent: 'evaluate',
  image2text_agent: 'ocr',
};
