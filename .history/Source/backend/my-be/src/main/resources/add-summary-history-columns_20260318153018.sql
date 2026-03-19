-- Run this once on your database to add missing columns to summary_history
-- (e.g. mysql -u user -p your_db < add-summary-history-columns.sql)

ALTER TABLE summary_history ADD COLUMN user_input TEXT;
ALTER TABLE summary_history ADD COLUMN summary_image_url TEXT;
ALTER TABLE summary_history ADD COLUMN evaluation TEXT;
ALTER TABLE summary_history ADD COLUMN mas_session_id VARCHAR(255);
ALTER TABLE summary_history ADD COLUMN conversation_id VARCHAR(255);
