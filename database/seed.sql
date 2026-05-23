-- Optional seed data for local development.
INSERT INTO users (id, email, display_name, plan)
VALUES ('00000000-0000-0000-0000-000000000001', 'demo@local', 'Demo User', 'studio')
ON CONFLICT (id) DO NOTHING;

INSERT INTO channels (user_id, name, niche, language)
VALUES ('00000000-0000-0000-0000-000000000001', 'Deep Facts', 'science/curiosity', 'en')
ON CONFLICT DO NOTHING;
