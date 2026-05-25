-- Suite runs: one row per execution of a named scenario suite
CREATE TABLE IF NOT EXISTS suite_runs (
    id               BIGSERIAL        PRIMARY KEY,
    suite_name       TEXT             NOT NULL,
    run_label        TEXT             NOT NULL,
    model_name       TEXT             NOT NULL,
    provider         TEXT             NOT NULL,
    agent_server     TEXT,
    total_scenarios  INTEGER          NOT NULL DEFAULT 0,
    passed           INTEGER          NOT NULL DEFAULT 0,
    failed           INTEGER          NOT NULL DEFAULT 0,
    partial          INTEGER          NOT NULL DEFAULT 0,
    error_count      INTEGER          NOT NULL DEFAULT 0,
    avg_score        DOUBLE PRECISION,
    total_cost_usd   NUMERIC(12, 8),
    total_time       DOUBLE PRECISION,
    start_datetime   TIMESTAMPTZ      NOT NULL,
    end_datetime     TIMESTAMPTZ,
    created_at       TIMESTAMPTZ      NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS suite_runs_suite_name_idx     ON suite_runs (suite_name);
CREATE INDEX IF NOT EXISTS suite_runs_model_name_idx     ON suite_runs (model_name);
CREATE INDEX IF NOT EXISTS suite_runs_start_datetime_idx ON suite_runs (start_datetime);

-- Link individual runs back to the suite execution that produced them
ALTER TABLE runs
    ADD COLUMN IF NOT EXISTS suite_run_id BIGINT REFERENCES suite_runs(id);

CREATE INDEX IF NOT EXISTS runs_suite_run_id_idx ON runs (suite_run_id);
