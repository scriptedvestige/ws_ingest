CREATE TABLE lightning_events (
    time TIMESTAMPTZ NOT NULL,
    lightning_num INTEGER,
    lightning_time TIMESTAMPTZ,
    lightning NUMERIC(6,2)
);

SELECT create_hypertable('lightning_events', 'time');