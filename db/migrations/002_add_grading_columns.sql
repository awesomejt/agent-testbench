-- Add LLM-as-judge grading columns to the runs table
ALTER TABLE runs
    ADD COLUMN IF NOT EXISTS grader_model     TEXT,
    ADD COLUMN IF NOT EXISTS grader_rationale TEXT;
