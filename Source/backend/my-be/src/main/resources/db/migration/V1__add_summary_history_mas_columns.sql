-- Add columns for MAS chat flow to summary_history (run once)
ALTER TABLE summary_history ADD COLUMN user_input TEXT;
ALTER TABLE summary_history ADD COLUMN summary_image_url TEXT;
ALTER TABLE summary_history ADD COLUMN evaluation TEXT;
ALTER TABLE summary_history ADD COLUMN mas_session_id VARCHAR(255);
ALTER TABLE summary_history ADD COLUMN conversation_id VARCHAR(255);
