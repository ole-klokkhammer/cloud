-- surveillance bootstrap + schema (events + embeddings)


-- stage 0: the database itself (idempotent; must be run from outside it)
CREATE DATABASE surveillance;
CREATE USER surveillance WITH PASSWORD 'IGZ1VnQyWbGdcnE7GlsKTE0y';
GRANT ALL ON DATABASE surveillance TO surveillance;
GRANT ALL PRIVILEGES  ON SCHEMA public TO surveillance;


-- stage 1: extensions + objects (in `public`; db is dedicated, so no custom schema)
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS timescaledb;

CREATE TABLE IF NOT EXISTS events (
    id          bigserial,
    ts          timestamptz NOT NULL,
    camera      text NOT NULL,
    class       text NOT NULL,
    conf        real,                 -- detector confidence (NULL when written by the embedder from a still)
    still_path  text,                 -- container-visible path (/detector/events/...; same PVE disk the detector writes)
    embedding   vector(512),         -- CLIP ViT-B/32 image+text space
    created_at  timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (id, ts)
);

-- one chunk per day; tune with retention/volume
SELECT create_hypertable('events', 'ts',
    chunk_time_interval => INTERVAL '1 day',
    if_not_exists => TRUE);

-- query hot paths
CREATE INDEX IF NOT EXISTS events_camera_ts_idx ON events (camera, ts DESC);
CREATE INDEX IF NOT EXISTS events_class_ts_idx  ON events (class, ts DESC); 