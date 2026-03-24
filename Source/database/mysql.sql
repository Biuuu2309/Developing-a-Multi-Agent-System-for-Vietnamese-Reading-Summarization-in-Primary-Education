USE mydatabase

CREATE TABLE users (
	user_id VARCHAR(255),
	avatar_url VARCHAR(255),
    email VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    is_active BIT(1) NOT NULL,
    password VARCHAR(255) NOT NULL,
    phone_number VARCHAR(255) NOT NULL,
    role VARCHAR(255) NOT NULL,
    username VARCHAR(255) NOT NULL,
    PRIMARY KEY (user_id)
);

CREATE TABLE summaries (
	summary_id VARCHAR(255),
    approved_at TIMESTAMP NOT NULL,
    content MEDIUMTEXT NOT NULL,summaries
    created_at TIMESTAMP NOT NULL,summaries
    grade VARCHAR(255) NOT NULL,
    image_url TEXT,
    summary_image_url TEXT,
    method VARCHAR(255) NOT NULL,
    read_count INT NOT NULL,
    status VARCHAR(255),
    summary_content MEDIUMTEXT NOT NULL,
    title VARCHAR(255) NOT NULL,
    created_by VARCHAR(255) NOT NULL,
    PRIMARY KEY (summary_id),
    FOREIGN KEY (created_by) REFERENCES users(user_id) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE summary_sessions (
	session_id BIGINT AUTO_INCREMENT,
    content MEDIUMTEXT NOT NULL,
    created_by VARCHAR(255),
    content_hash VARCHAR(255) NOT NULL,
    timestamp VARCHAR(255) NOT NULL,
    PRIMARY KEY (session_id),
    FOREIGN KEY (created_by) REFERENCES users(user_id) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE summary_history (
	history_id BIGINT AUTO_INCREMENT,
    method VARCHAR(255),
    summary_content MEDIUMTEXT NOT NULL,
    session_id BIGINT,
    is_accepted BIT(1),
    image_url VARCHAR(255),
    PRIMARY KEY (history_id),
    FOREIGN KEY (session_id) REFERENCES summary_session(session_id) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE read_history (
	id BIGINT AUTO_INCREMENT,
    summary_id VARCHAR(255),
    user_id VARCHAR(255),
    PRIMARY KEY (id),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (summary_id) REFERENCES summaries(summary_id) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE conversations (
	conversation_id VARCHAR(255),
    user_id VARCHAR(255),
    title VARCHAR(255) NOT NULL,
    status ENUM('ACTIVE', 'ARCHIVED', 'DELETED') DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (conversation_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE agents (
    agent_id VARCHAR(255),
    name VARCHAR(100),
    description TEXT,
    agent_type ENUM('INTENT', 'CLARIFICATION', 'PLANNING', 'IMAGE2TEXT', 'ABSTRACTER', 'EXTRACTOR', 'EVALUATION', 'ORCHESTRATOR', 'OTHER') DEFAULT 'OTHER',
    is_active BOOLEAN DEFAULT TRUE,
    capabilities JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (agent_id)
);

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
    semantic_recall JSON,
    tool_recommendations JSON,
    knowledge_search JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES mas_sessions(session_id) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE messages (
    message_id VARCHAR(255) PRIMARY KEY,
    session_id VARCHAR(255),
    conversation_id VARCHAR(255),
    user_id VARCHAR(255),
    agent_id VARCHAR(255),
    role ENUM('USER', 'ASSISTANT', 'SYSTEM'),
    content TEXT,
    metadata JSON,
    status ENUM('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED') DEFAULT 'PENDING',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (agent_id) REFERENCES agents(agent_id) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (session_id) REFERENCES mas_sessions(session_id) ON UPDATE CASCADE ON DELETE SET NULL
);

ALTER TABLE mas_states 
ADD CONSTRAINT fk_mas_states_message 
FOREIGN KEY (message_id) REFERENCES messages(message_id) ON UPDATE CASCADE ON DELETE SET NULL;

CREATE TABLE agent_logs (
    log_id VARCHAR(255) PRIMARY KEY,
    session_id VARCHAR(255),
    message_id VARCHAR(255),
    state_id VARCHAR(255),
	task_type VARCHAR(100),
	confidence_score DECIMAL(5,4),
    agent_id VARCHAR(255),
    input TEXT,
    output TEXT,
    duration_ms INT,
    status ENUM('SUCCESS', 'ERROR'),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (message_id) REFERENCES messages(message_id) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (agent_id) REFERENCES agents(agent_id) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (session_id) REFERENCES mas_sessions(session_id) ON UPDATE CASCADE ON DELETE SET NULL,
    FOREIGN KEY (state_id) REFERENCES mas_states(state_id) ON UPDATE CASCADE ON DELETE SET NULL
);

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

CREATE TABLE mas_evaluations (
    evaluation_id VARCHAR(255) PRIMARY KEY,
    state_id VARCHAR(255) NOT NULL,
    metrics JSON NOT NULL,
    rouge1_f1 DECIMAL(5,4),
    rougeL_f1 DECIMAL(5,4),
    bertscore_f1 DECIMAL(5,4),
    -- Text difficulty features
    difficulty_level VARCHAR(50),
    total_words INT,
    unique_words INT,
    type_token_ratio DECIMAL(5,4),
    rare_word_ratio DECIMAL(5,4),
    unknown_word_ratio DECIMAL(5,4),
    avg_word_grade DECIMAL(6,3),
    num_sentences INT,
    avg_sentence_length DECIMAL(6,2),
    max_sentence_length INT,
    min_sentence_length INT,
    long_sentence_ratio DECIMAL(5,4),
    avg_word_length DECIMAL(6,3),
    words_per_sentence DECIMAL(6,2),
    lexical_density DECIMAL(5,4),
    matched_rules TEXT,
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (state_id) REFERENCES mas_states(state_id) ON UPDATE CASCADE ON DELETE CASCADE
);

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

ALTER TABLE mas_states 
ADD COLUMN semantic_recall JSON,
ADD COLUMN tool_recommendations JSON,
ADD COLUMN knowledge_search JSON;

-- Migration: Change image_url from VARCHAR(255) to TEXT to support JSON array
ALTER TABLE summaries 
MODIFY COLUMN image_url TEXT;

-- Migration: Add summary_image_url column to store mapping between summary parts and image URLs
ALTER TABLE summaries 
ADD COLUMN summary_image_url TEXT;

ALTER TABLE summary_history ADD COLUMN user_input TEXT;
ALTER TABLE summary_history ADD COLUMN summary_image_url TEXT;
ALTER TABLE summary_history ADD COLUMN evaluation TEXT;
ALTER TABLE summary_history ADD COLUMN mas_session_id VARCHAR(255);
ALTER TABLE summary_history ADD COLUMN conversation_id VARCHAR(255);

DROP TABLE IF EXISTS mas_agent_confidences;
DROP TABLE IF EXISTS mas_agent_memories;
DROP TABLE IF EXISTS mas_negotiations;
DROP TABLE IF EXISTS mas_goals;
DROP TABLE IF EXISTS mas_evaluations;
DROP TABLE IF EXISTS mas_plans;
DROP TABLE IF EXISTS agent_logs;
DROP TABLE IF EXISTS mas_states;
DROP TABLE IF EXISTS messages;
DROP TABLE IF EXISTS mas_sessions;
DROP TABLE IF EXISTS summary_history;
DROP TABLE IF EXISTS summary_sessions;
DROP TABLE IF EXISTS read_history;
DROP TABLE IF EXISTS summaries;
DROP TABLE IF EXISTS conversations;
DROP TABLE IF EXISTS agents;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS message_user_ai;

SELECT * FROM users
SELECT * FROM summary_history
SELECT * FROM summary_session
SELECT * FROM read_history
SELECT * FROM conversations
SELECT * FROM summaries
SELECT * FROM messages
SELECT * FROM agents