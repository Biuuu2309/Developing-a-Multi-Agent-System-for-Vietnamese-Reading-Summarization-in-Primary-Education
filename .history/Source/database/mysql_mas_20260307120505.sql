USE mydatabase;

-- ============================================
-- MAS SYSTEM DATABASE SCHEMA
-- ============================================

-- MAS Sessions: Quản lý các session conversation với MAS
CREATE TABLE mas_sessions (
    session_id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    conversation_id VARCHAR(255),
    status ENUM('ACTIVE', 'COMPLETED', 'ARCHIVED') DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id) ON UPDATE CASCADE ON DELETE SET NULL
);

-- MAS States: Lưu trữ state của MAS workflow cho mỗi request
CREATE TABLE mas_states (
    state_id VARCHAR(255) PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    message_id VARCHAR(255),
    user_input TEXT,
    history JSON,
    intent JSON,
    clarification_needed BOOLEAN DEFAULT FALSE,
    clarification_question TEXT,
    plan JSON,
    original_text TEXT,
    summary TEXT,
    evaluation JSON,
    final_output TEXT,
    plan_revision_count INT DEFAULT 0,
    strategy_changed BOOLEAN DEFAULT FALSE,
    improvement_count INT DEFAULT 0,
    needs_improvement BOOLEAN DEFAULT FALSE,
    image_path VARCHAR(500),
    extracted_text TEXT,
    goal_state JSON,
    agent_confidences JSON,
    negotiation_result JSON,
    agent_memories JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES mas_sessions(session_id) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (message_id) REFERENCES messages(message_id) ON UPDATE CASCADE ON DELETE SET NULL
);

-- MAS Plans: Lưu trữ execution plans
CREATE TABLE mas_plans (
    plan_id VARCHAR(255) PRIMARY KEY,
    state_id VARCHAR(255) NOT NULL,
    intent JSON,
    pipeline JSON NOT NULL,
    context JSON,
    revision_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (state_id) REFERENCES mas_states(state_id) ON UPDATE CASCADE ON DELETE CASCADE
);

-- MAS Evaluations: Lưu trữ kết quả đánh giá
CREATE TABLE mas_evaluations (
    evaluation_id VARCHAR(255) PRIMARY KEY,
    state_id VARCHAR(255) NOT NULL,
    metrics JSON NOT NULL,
    rouge1_f1 DECIMAL(5,4),
    rougeL_f1 DECIMAL(5,4),
    bertscore_f1 DECIMAL(5,4),
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (state_id) REFERENCES mas_states(state_id) ON UPDATE CASCADE ON DELETE CASCADE
);

-- MAS Goals: Advanced MAS - Goal State Management
CREATE TABLE mas_goals (
    goal_id VARCHAR(255) PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    goal_type VARCHAR(100) NOT NULL,
    description TEXT,
    requirements JSON,
    priority INT DEFAULT 5,
    status ENUM('PENDING', 'IN_PROGRESS', 'ACHIEVED', 'FAILED', 'CANCELLED') DEFAULT 'PENDING',
    progress JSON,
    final_metrics JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES mas_sessions(session_id) ON UPDATE CASCADE ON DELETE CASCADE
);

-- MAS Agent Memories: Lưu trữ memory của từng agent
CREATE TABLE mas_agent_memories (
    memory_id VARCHAR(255) PRIMARY KEY,
    agent_id VARCHAR(255) NOT NULL,
    task_type VARCHAR(100),
    input_data JSON,
    output_data TEXT,
    success BOOLEAN DEFAULT TRUE,
    context JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (agent_id) REFERENCES agents(agent_id) ON UPDATE CASCADE ON DELETE CASCADE,
    INDEX idx_agent_task (agent_id, task_type)
);

-- MAS Negotiations: Lưu trữ negotiation history
CREATE TABLE mas_negotiations (
    negotiation_id VARCHAR(255) PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    initiator VARCHAR(100) NOT NULL,
    participants JSON NOT NULL,
    topic VARCHAR(255),
    status ENUM('INITIATED', 'IN_PROGRESS', 'ACCEPTED', 'REJECTED', 'TIMEOUT') DEFAULT 'INITIATED',
    proposals JSON,
    responses JSON,
    constraints JSON,
    max_rounds INT DEFAULT 5,
    current_round INT DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES mas_sessions(session_id) ON UPDATE CASCADE ON DELETE CASCADE
);

-- MAS Agent Confidences: Lưu trữ confidence scores của agents
CREATE TABLE mas_agent_confidences (
    confidence_id VARCHAR(255) PRIMARY KEY,
    agent_id VARCHAR(255) NOT NULL,
    session_id VARCHAR(255),
    task_type VARCHAR(100),
    confidence_score DECIMAL(5,4) NOT NULL,
    context JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (agent_id) REFERENCES agents(agent_id) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (session_id) REFERENCES mas_sessions(session_id) ON UPDATE CASCADE ON DELETE SET NULL,
    INDEX idx_agent_confidence (agent_id, task_type)
);

-- Cập nhật bảng agents để hỗ trợ MAS agents
ALTER TABLE agents ADD COLUMN IF NOT EXISTS agent_type ENUM('INTENT', 'CLARIFICATION', 'PLANNING', 'IMAGE2TEXT', 'ABSTRACTER', 'EXTRACTOR', 'EVALUATION', 'ORCHESTRATOR', 'OTHER') DEFAULT 'OTHER';
ALTER TABLE agents ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;

-- Cập nhật bảng messages để hỗ trợ MAS workflow
ALTER TABLE messages ADD COLUMN IF NOT EXISTS session_id VARCHAR(255);
ALTER TABLE messages ADD COLUMN IF NOT EXISTS state_id VARCHAR(255);
ALTER TABLE messages ADD FOREIGN KEY (session_id) REFERENCES mas_sessions(session_id) ON UPDATE CASCADE ON DELETE SET NULL;
ALTER TABLE messages ADD FOREIGN KEY (state_id) REFERENCES mas_states(state_id) ON UPDATE CASCADE ON DELETE SET NULL;

-- Cập nhật bảng agent_logs để hỗ trợ MAS
ALTER TABLE agent_logs ADD COLUMN IF NOT EXISTS session_id VARCHAR(255);
ALTER TABLE agent_logs ADD COLUMN IF NOT EXISTS state_id VARCHAR(255);
ALTER TABLE agent_logs ADD COLUMN IF NOT EXISTS task_type VARCHAR(100);
ALTER TABLE agent_logs ADD COLUMN IF NOT EXISTS confidence_score DECIMAL(5,4);
ALTER TABLE agent_logs ADD FOREIGN KEY (session_id) REFERENCES mas_sessions(session_id) ON UPDATE CASCADE ON DELETE SET NULL;
ALTER TABLE agent_logs ADD FOREIGN KEY (state_id) REFERENCES mas_states(state_id) ON UPDATE CASCADE ON DELETE SET NULL;
