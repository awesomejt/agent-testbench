-- Run records table — one row per scenario execution
CREATE TABLE IF NOT EXISTS runs (
    id               BIGSERIAL PRIMARY KEY,
    run_name         TEXT        NOT NULL,
    scenario_name    TEXT        NOT NULL,
    model_name       TEXT        NOT NULL,
    provider         TEXT        NOT NULL,
    agent_server     TEXT,                          -- null for cloud models
    start_datetime   TIMESTAMPTZ NOT NULL,
    end_datetime     TIMESTAMPTZ NOT NULL,
    total_time       DOUBLE PRECISION NOT NULL,     -- seconds
    tokens_per_second DOUBLE PRECISION,
    follow_up_prompts INTEGER     NOT NULL DEFAULT 0,
    input_tokens     INTEGER     NOT NULL DEFAULT 0,
    output_tokens    INTEGER     NOT NULL DEFAULT 0,
    total_tokens     INTEGER     NOT NULL DEFAULT 0,
    cost_usd         NUMERIC(12, 8),                -- API billing or estimated local cost
    pass_fail        TEXT CHECK (pass_fail IN ('pass', 'fail', 'partial', 'error')),
    score            DOUBLE PRECISION,
    error            BOOLEAN     NOT NULL DEFAULT FALSE,
    error_message    TEXT,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS runs_scenario_name_idx ON runs (scenario_name);
CREATE INDEX IF NOT EXISTS runs_model_name_idx    ON runs (model_name);
CREATE INDEX IF NOT EXISTS runs_provider_idx      ON runs (provider);
CREATE INDEX IF NOT EXISTS runs_start_datetime_idx ON runs (start_datetime);
