-- Migration 001: Add hostname tracking columns
-- Run this script to upgrade existing database to support hostname tracking

USE telegram_utilities;

-- Add hostname columns to messages table
ALTER TABLE messages
ADD COLUMN IF NOT EXISTS retrieved_hostname VARCHAR(255) AFTER retrieved_datetime,
ADD COLUMN IF NOT EXISTS download_hostname VARCHAR(255) AFTER local_file_path;

-- Add indexes for hostname columns in messages table
CREATE INDEX IF NOT EXISTS idx_retrieved_hostname ON messages(retrieved_hostname);
CREATE INDEX IF NOT EXISTS idx_download_hostname ON messages(download_hostname);

-- Add hostname column to download_log table
ALTER TABLE download_log
ADD COLUMN IF NOT EXISTS hostname VARCHAR(255) AFTER retry_count;

-- Add index for hostname column in download_log table
CREATE INDEX IF NOT EXISTS idx_hostname ON download_log(hostname);

-- Add hostname column to action_log table
ALTER TABLE action_log
ADD COLUMN IF NOT EXISTS hostname VARCHAR(255) AFTER error_message;

-- Add index for hostname column in action_log table
CREATE INDEX IF NOT EXISTS idx_hostname ON action_log(hostname);

-- Migration complete
SELECT 'Migration 001 completed: Hostname tracking columns added' AS status;
