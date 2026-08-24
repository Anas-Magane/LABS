-- BlueOffice Breach - Challenge 16: PostgreSQL Weak Credentials (port 5432)
--
-- Second database, seeded after 01-blueoffice.sql. The same postgres/postgres
-- account can reach it. It looks like a routine internal/system-accounts
-- table - the challenge is realizing it's worth enumerating at all, then
-- reading every row's internal_note carefully.

CREATE DATABASE flags;

\c flags

CREATE TABLE users (
    id             SERIAL PRIMARY KEY,
    username       TEXT NOT NULL UNIQUE,
    full_name      TEXT NOT NULL,
    role           TEXT NOT NULL,
    email          TEXT NOT NULL,
    account_status TEXT NOT NULL,
    last_login     TIMESTAMP,
    internal_note  TEXT
);

INSERT INTO users (username, full_name, role, email, account_status, last_login, internal_note) VALUES
    ('backup_service',   'Backup Service Account',      'system', 'backup-service@blueoffice.local',     'active',   '2025-08-21 03:00:00', 'Nightly pg_dump + off-site sync job. Rotates its own credential via Vault every 90 days.'),
    ('audit_reader',     'Audit Log Reader',             'system', 'audit-reader@blueoffice.local',       'active',   '2025-08-21 06:15:00', 'Read-only role used by the compliance team''s log aggregator. No write grants.'),
    ('hr_sync',          'HR Sync Connector',            'system', 'hr-sync@blueoffice.local',            'active',   '2025-08-20 23:45:00', 'Syncs employee records from the HR SaaS nightly at 23:30. Owned by the HR Systems team.'),
    ('reporting_bot',    'Reporting Bot',                'system', 'reporting-bot@blueoffice.local',      'active',   '2025-08-21 05:00:00', 'Generates the weekly executive KPI PDF and emails it to management.'),
    ('svc_monitoring',   'Monitoring Service Account',   'system', 'svc-monitoring@blueoffice.local',     'active',   '2025-08-21 07:00:00', 'Used by the internal Grafana/Prometheus stack for read-only health checks.'),
    ('db_replication',   'DB Replication Agent',         'system', 'db-replication@blueoffice.local',     'active',   '2025-08-21 04:30:00', 'Streaming replication role for the standby replica. Certificate-based auth only.'),
    ('etl_pipeline',     'ETL Pipeline Runner',          'system', 'etl-pipeline@blueoffice.local',       'active',   '2025-08-20 22:10:00', 'Nightly ETL job feeding the analytics warehouse from blueoffice.deals/invoices.'),
    ('vendor_integration','Vendor Integration Account',  'system', 'vendor-integration@blueoffice.local', 'disabled', '2024-11-02 09:00:00', 'Old integration with a third-party invoicing vendor. Disabled after the contract ended.'),
    ('legacy_admin',     'Legacy Admin (migration)',     'admin',  'legacy-admin@blueoffice.local',       'active',   '2021-09-14 17:22:00', 'Left over from the 2021 on-prem-to-cloud migration (ticket IT-4471, still open). Never rotated off its original bootstrap password from the migration runbook - CTF{Alw4y5_cHeK_TH2_D2FaulT_P4ss}. Flagged for removal, keeps getting deprioritized.');
