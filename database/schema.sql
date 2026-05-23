-- =============================================================================
-- AI YouTube Factory — Postgres / Supabase schema (standalone DDL).
--
-- Alembic is authoritative for the app (see database/alembic). This file is for
-- provisioning the schema directly in the Supabase SQL editor or a fresh DB.
-- =============================================================================

CREATE EXTENSION IF NOT EXISTS pgcrypto;  -- gen_random_uuid()

-- ---- enums ----
DO $$ BEGIN
  CREATE TYPE jobstatus AS ENUM
    ('queued','scripting','voicing','rendering','assembling','uploading','completed','failed','canceled');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TYPE jobsource AS ENUM ('api','telegram','scheduler','dashboard');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TYPE assetkind AS ENUM ('image','audio','video_clip','final_video','thumbnail','subtitle','log');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TYPE plantier AS ENUM ('free','creator','studio');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- ---- users ----
CREATE TABLE IF NOT EXISTS users (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  email         varchar(320) UNIQUE,
  telegram_id   integer UNIQUE,
  display_name  varchar(120),
  plan          plantier NOT NULL DEFAULT 'free',
  is_active     boolean NOT NULL DEFAULT true,
  created_at    timestamptz NOT NULL DEFAULT now(),
  updated_at    timestamptz NOT NULL DEFAULT now()
);

-- ---- channels ----
CREATE TABLE IF NOT EXISTS channels (
  id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id     uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  name        varchar(120) NOT NULL,
  niche       varchar(120),
  language    varchar(12) NOT NULL DEFAULT 'en',
  voice       varchar(80),
  branding    jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at  timestamptz NOT NULL DEFAULT now(),
  updated_at  timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_channels_user_id ON channels(user_id);

-- ---- jobs ----
CREATE TABLE IF NOT EXISTS jobs (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id         uuid REFERENCES users(id),
  channel_id      uuid REFERENCES channels(id),
  topic           text NOT NULL,
  style           varchar(60) NOT NULL DEFAULT 'documentary',
  source          jobsource NOT NULL DEFAULT 'api',
  status          jobstatus NOT NULL DEFAULT 'queued',
  stage           varchar(60),
  progress        integer NOT NULL DEFAULT 0,
  params          jsonb NOT NULL DEFAULT '{}'::jsonb,
  script          jsonb,
  error           text,
  celery_task_id  varchar(80),
  started_at      timestamptz,
  finished_at     timestamptz,
  created_at      timestamptz NOT NULL DEFAULT now(),
  updated_at      timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_jobs_user_id ON jobs(user_id);
CREATE INDEX IF NOT EXISTS ix_jobs_status  ON jobs(status);
CREATE INDEX IF NOT EXISTS ix_jobs_created ON jobs(created_at DESC);
CREATE INDEX IF NOT EXISTS ix_jobs_task    ON jobs(celery_task_id);

-- ---- videos ----
CREATE TABLE IF NOT EXISTS videos (
  id             uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  job_id         uuid NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
  title          varchar(200) NOT NULL,
  description    text,
  tags           jsonb NOT NULL DEFAULT '[]'::jsonb,
  duration_sec   double precision,
  width          integer,
  height         integer,
  storage_key    varchar(512),
  url            varchar(1024),
  thumbnail_url  varchar(1024),
  captions_url   varchar(1024),
  created_at     timestamptz NOT NULL DEFAULT now(),
  updated_at     timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_videos_job_id ON videos(job_id);

-- ---- assets ----
CREATE TABLE IF NOT EXISTS assets (
  id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  job_id       uuid NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
  kind         assetkind NOT NULL,
  storage_key  varchar(512) NOT NULL,
  url          varchar(1024),
  meta         jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at   timestamptz NOT NULL DEFAULT now(),
  updated_at   timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_assets_job_id ON assets(job_id);

-- ---- events (audit / analytics) ----
CREATE TABLE IF NOT EXISTS events (
  id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  job_id      uuid REFERENCES jobs(id) ON DELETE CASCADE,
  type        varchar(60) NOT NULL,
  data        jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at  timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_events_job_id ON events(job_id);

-- ---- subscriptions ----
CREATE TABLE IF NOT EXISTS subscriptions (
  id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id      uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  plan         plantier NOT NULL DEFAULT 'free',
  status       varchar(40) NOT NULL DEFAULT 'active',
  provider     varchar(40),
  external_id  varchar(120),
  period_end   timestamptz,
  created_at   timestamptz NOT NULL DEFAULT now(),
  updated_at   timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_subscriptions_user_id ON subscriptions(user_id);

-- ---- Supabase RLS note ----
-- The backend connects with the service role (bypasses RLS). If you expose any
-- table to anon/auth roles directly, enable RLS and add policies, e.g.:
--   ALTER TABLE videos ENABLE ROW LEVEL SECURITY;
--   CREATE POLICY "public read completed videos" ON videos FOR SELECT USING (true);
