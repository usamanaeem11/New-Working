-- Sample seed data for development
-- Organization
INSERT INTO organizations (id, name, slug, description) VALUES
('11111111-1111-1111-1111-111111111111', 'Demo Corporation', 'demo-corp', 'Demo organization for testing');

-- Users
INSERT INTO users (id, email, username, password_hash, first_name, last_name, is_superuser) VALUES
('22222222-2222-2222-2222-222222222222', 'admin@demo.com', 'admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5lW3Z8pMQY9EK', 'Admin', 'User', true);

-- More seed data...
