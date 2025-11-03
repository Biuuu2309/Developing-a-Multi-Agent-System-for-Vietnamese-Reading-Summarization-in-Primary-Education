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
)

CREATE TABLE tags (
	tag_id VARCHAR(255),
    name VARCHAR(255) NOT NULL,
    PRIMARY KEY (tag_id)
)

CREATE TABLE summaries (
	summary_id VARCHAR(255),
    approved_at TIMESTAMP NOT NULL,
    content MEDIUMTEXT NOT NULL,
    created_at TIMESTAMP NOT NULL,
    grade VARCHAR(255) NOT NULL,
    image_url VARCHAR(255),
    method VARCHAR(255) NOT NULL,
    read_count INT NOT NULL,
    status VARCHAR(255),
    summary_content MEDIUMTEXT NOT NULL,
    title VARCHAR(255) NOT NULL,
    created_by VARCHAR(255) NOT NULL,
    PRIMARY KEY (summary_id),
    FOREIGN KEY (created_by) REFERENCES users(user_id) ON UPDATE CASCADE ON DELETE CASCADE
)

CREATE TABLE summary_session (
	session_id BIGINT AUTO_INCREMENT,
    content MEDIUMTEXT NOT NULL,
    created_by VARCHAR(255),
    content_hash VARCHAR(255) NOT NULL,
    timestamp VARCHAR(255) NOT NULL,
    PRIMARY KEY (session_id),
    FOREIGN KEY (created_by) REFERENCES users(user_id) ON UPDATE CASCADE ON DELETE CASCADE
)

CREATE TABLE summary_history (
	history_id BIGINT AUTO_INCREMENT,
    method VARCHAR(255),
    summary_content MEDIUMTEXT NOT NULL,
    session_id BIGINT,
    is_accepted BIT(1),
    image_url VARCHAR(255),
    PRIMARY KEY (history_id),
    FOREIGN KEY (session_id) REFERENCES summary_session(session_id) ON UPDATE CASCADE ON DELETE CASCADE
)

CREATE TABLE read_history (
	id BIGINT AUTO_INCREMENT,
    summary_id VARCHAR(255),
    user_id VARCHAR(255),
    PRIMARY KEY (id),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (summary_id) REFERENCES summaries(summary_id) ON UPDATE CASCADE ON DELETE CASCADE
)

CREATE TABLE summary_tags (
	summary_tag_id NVARCHAR(255),
    summary_id NVARCHAR(255),
    tag_id NVARCHAR(255),
    PRIMARY KEY (summary_tag_id),
    FOREIGN KEY (summary_id) REFERENCES summaries(summary_id) ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(tag_id) ON UPDATE CASCADE ON DELETE CASCADE
)

CREATE TABLE conversations (
	message_id NVARCHAR(255),
    user_id NVARCHAR(255),
    role NVARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (message_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON UPDATE CASCADE ON DELETE CASCADE
)

DROP TABLE IF EXISTS summary_history;
DROP TABLE IF EXISTS summary_session;
DROP TABLE IF EXISTS read_history;
DROP TABLE IF EXISTS conversations;
DROP TABLE IF EXISTS summary_tags;
DROP TABLE IF EXISTS summaries;
DROP TABLE IF EXISTS tags;
DROP TABLE IF EXISTS users;

SELECT * FROM users
SELECT * FROM summary_history
SELECT * FROM summary_session
SELECT * FROM read_history
SELECT * FROM conversations
SELECT * FROM summary_tags
SELECT * FROM summaries
SELECT * FROM tags