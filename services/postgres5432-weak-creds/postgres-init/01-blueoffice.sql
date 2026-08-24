-- BlueOffice Breach - Challenge 16: PostgreSQL Weak Credentials (port 5432)
--
-- Seed data for the "blueoffice" database (the default database created by
-- POSTGRES_DB). Runs first (01-) against the connection already opened by
-- the official postgres image's entrypoint. Purely fake/fictional data -
-- no real secrets, no real people.

-- ---------------------------------------------------------------------------
-- departments
-- ---------------------------------------------------------------------------
CREATE TABLE departments (
    id            SERIAL PRIMARY KEY,
    name          TEXT NOT NULL,
    manager_name  TEXT NOT NULL,
    office_floor  INTEGER NOT NULL,
    budget_mad    NUMERIC(12, 2) NOT NULL
);

INSERT INTO departments (name, manager_name, office_floor, budget_mad) VALUES
    ('Executive',         'Nabil El Amrani',   5, 1200000.00),
    ('Human Resources',   'Sana Amrani',       3,  450000.00),
    ('Finance',           'Rachid Belhaj',     3,  900000.00),
    ('Sales',             'Youssef Bennani',   2, 1500000.00),
    ('IT',                'Imane Ziani',       4, 2100000.00),
    ('Security',          'Hamza Tazi',        4,  600000.00),
    ('Operations',        'Khadija Aitali',    1,  800000.00),
    ('Customer Success',  'Omar Fassi',        2,  500000.00);

-- ---------------------------------------------------------------------------
-- employees
-- ---------------------------------------------------------------------------
CREATE TABLE employees (
    id                 SERIAL PRIMARY KEY,
    employee_code      TEXT NOT NULL UNIQUE,
    full_name          TEXT NOT NULL,
    email              TEXT NOT NULL,
    phone              TEXT NOT NULL,
    department         TEXT NOT NULL,
    job_title          TEXT NOT NULL,
    salary_mad         NUMERIC(10, 2) NOT NULL,
    hire_date          DATE NOT NULL,
    manager_id         INTEGER REFERENCES employees(id),
    employment_status  TEXT NOT NULL DEFAULT 'active'
);

INSERT INTO employees (employee_code, full_name, email, phone, department, job_title, salary_mad, hire_date, manager_id, employment_status) VALUES
    ('EMP-0001', 'Nabil El Amrani',       'nabil.elamrani@blueoffice.local',   '+212600100001', 'Executive',        'Chief Executive Officer',   45000.00, '2016-01-10', NULL, 'active'),
    ('EMP-0002', 'Sana Amrani',           'sana.amrani@blueoffice.local',      '+212600100002', 'Human Resources',  'HR Manager',                 28000.00, '2017-03-01', 1,    'active'),
    ('EMP-0003', 'Rachid Belhaj',         'rachid.belhaj@blueoffice.local',    '+212600100003', 'Finance',          'Finance Director',           32000.00, '2016-06-15', 1,    'active'),
    ('EMP-0004', 'Youssef Bennani',       'youssef.bennani@blueoffice.local',  '+212600100004', 'Sales',            'Sales Director',             33000.00, '2017-01-20', 1,    'active'),
    ('EMP-0005', 'Imane Ziani',           'imane.ziani@blueoffice.local',      '+212600100005', 'IT',               'IT Director',                34000.00, '2016-09-05', 1,    'active'),
    ('EMP-0006', 'Hamza Tazi',            'hamza.tazi@blueoffice.local',       '+212600100006', 'Security',         'Security Manager',           30000.00, '2018-02-11', 1,    'active'),
    ('EMP-0007', 'Khadija Aitali',        'khadija.aitali@blueoffice.local',   '+212600100007', 'Operations',       'Operations Manager',         27000.00, '2017-11-01', 1,    'active'),
    ('EMP-0008', 'Omar Fassi',            'omar.fassi@blueoffice.local',       '+212600100008', 'Customer Success', 'Customer Success Manager',   26000.00, '2018-05-22', 1,    'active'),
    ('EMP-0009', 'Nadia Chraibi',         'nadia.chraibi@blueoffice.local',    '+212600100009', 'Security',         'Network Security Analyst',   18000.00, '2019-04-01', 6,    'active'),
    ('EMP-0010', 'Karim El Idrissi',      'karim.elidrissi@blueoffice.local',  '+212600100010', 'IT',               'Java Backend Engineer',      19000.00, '2019-07-14', 5,    'active'),
    ('EMP-0011', 'Salma Idrissi',         'salma.idrissi@blueoffice.local',    '+212600100011', 'Human Resources',  'HR Business Partner',        15000.00, '2020-01-09', 2,    'active'),
    ('EMP-0012', 'Youssef Alaoui',        'youssef.alaoui@blueoffice.local',   '+212600100012', 'IT',               'Systems Administrator',      17000.00, '2018-08-19', 5,    'active'),
    ('EMP-0013', 'Amina Bouzidi',         'amina.bouzidi@blueoffice.local',    '+212600100013', 'Finance',          'Accountant',                 13000.00, '2019-03-03', 3,    'active'),
    ('EMP-0014', 'Othmane Sabri',         'othmane.sabri@blueoffice.local',    '+212600100014', 'Finance',          'Financial Analyst',          14500.00, '2020-06-12', 3,    'active'),
    ('EMP-0015', 'Yassine Bouzid',        'yassine.bouzid@blueoffice.local',   '+212600100015', 'Sales',            'Account Executive',          16000.00, '2019-09-01', 4,    'active'),
    ('EMP-0016', 'Ikram Zerouali',        'ikram.zerouali@blueoffice.local',   '+212600100016', 'Sales',            'Account Executive',          15500.00, '2020-02-17', 4,    'active'),
    ('EMP-0017', 'Mehdi Saadi',           'mehdi.saadi@blueoffice.local',      '+212600100017', 'Sales',            'Sales Development Rep',      11000.00, '2021-01-05', 4,    'active'),
    ('EMP-0018', 'Rania Alaoui',          'rania.alaoui@blueoffice.local',     '+212600100018', 'Customer Success', 'Customer Success Specialist',12500.00, '2020-10-10', 8,    'active'),
    ('EMP-0019', 'Bilal Ouahbi',          'bilal.ouahbi@blueoffice.local',     '+212600100019', 'Customer Success', 'Support Engineer',           12000.00, '2021-03-22', 8,    'active'),
    ('EMP-0020', 'Zineb Amine',           'zineb.amine@blueoffice.local',      '+212600100020', 'Operations',       'Operations Coordinator',     11500.00, '2020-11-15', 7,    'active'),
    ('EMP-0021', 'Adil Kabbaj',           'adil.kabbaj@blueoffice.local',      '+212600100021', 'IT',               'Linux Systems Engineer',     18500.00, '2019-05-30', 5,    'active'),
    ('EMP-0022', 'Fatima Zahra Idrissi',  'fatimazahra.idrissi@blueoffice.local','+212600100022','Human Resources', 'Recruiter',                  13500.00, '2021-06-01', 2,    'on_leave'),
    ('EMP-0023', 'Houda Cherkaoui',       'houda.cherkaoui@blueoffice.local',  '+212600100023', 'Finance',          'Data Analyst',               16500.00, '2021-08-10', 3,    'active'),
    ('EMP-0024', 'Yasmine Toumi',         'yasmine.toumi@blueoffice.local',    '+212600100024', 'IT',               'IT Support Technician',      10500.00, '2022-01-15', 5,    'active'),
    ('EMP-0025', 'Anas Mrabet',           'anas.mrabet@blueoffice.local',      '+212600100025', 'IT',               'Junior Developer',            9500.00, '2022-09-01', 5,    'terminated');

-- ---------------------------------------------------------------------------
-- clients
-- ---------------------------------------------------------------------------
CREATE TABLE clients (
    id            SERIAL PRIMARY KEY,
    client_code   TEXT NOT NULL UNIQUE,
    company_name  TEXT NOT NULL,
    contact_name  TEXT NOT NULL,
    email         TEXT NOT NULL,
    phone         TEXT NOT NULL,
    city          TEXT NOT NULL,
    industry      TEXT NOT NULL,
    status        TEXT NOT NULL DEFAULT 'active',
    created_at    DATE NOT NULL
);

INSERT INTO clients (client_code, company_name, contact_name, email, phone, city, industry, status, created_at) VALUES
    ('CLI-0001', 'Atlas Textiles SARL',           'Hicham Radi',       'hicham.radi@atlastextiles.ma',      '+212661000001', 'Rabat',        'Textiles',     'active',    '2018-04-12'),
    ('CLI-0002', 'Marrakech Digital Solutions',   'Laila Benjelloun',  'laila.benjelloun@mdsolutions.ma',   '+212661000002', 'Marrakech',    'Technology',   'active',    '2019-02-20'),
    ('CLI-0003', 'Casablanca Freight & Logistics','Driss Kettani',     'driss.kettani@cfl.ma',              '+212661000003', 'Casablanca',   'Logistics',    'active',    '2017-11-05'),
    ('CLI-0004', 'Rif Agro Export',               'Samira Ouazzani',   'samira.ouazzani@rifagro.ma',        '+212661000004', 'Tetouan',      'Agriculture',  'active',    '2020-06-18'),
    ('CLI-0005', 'Fes Ceramics Co.',               'Abdelali Naciri',   'abdelali.naciri@fesceramics.ma',    '+212661000005', 'Fes',          'Manufacturing','active',    '2016-09-30'),
    ('CLI-0006', 'Tanger Med Shipping',            'Nawal Berrada',     'nawal.berrada@tangermedship.ma',    '+212661000006', 'Tangier',      'Logistics',    'active',    '2018-01-22'),
    ('CLI-0007', 'Souss Massa Renewables',         'Kamal Idrissi',     'kamal.idrissi@soussmassa.ma',       '+212661000007', 'Agadir',       'Energy',       'prospect',  '2023-03-14'),
    ('CLI-0008', 'Oujda Steel Works',              'Fatiha Lahlou',     'fatiha.lahlou@oujdasteel.ma',       '+212661000008', 'Oujda',        'Manufacturing','active',    '2017-05-09'),
    ('CLI-0009', 'Sahara Solar Ventures',          'Yassir Bouazza',    'yassir.bouazza@saharasolar.ma',     '+212661000009', 'Laayoune',     'Energy',       'prospect',  '2024-01-08'),
    ('CLI-0010', 'Atlantic Seafood Group',         'Meryem Skalli',     'meryem.skalli@atlanticseafood.ma',  '+212661000010', 'El Jadida',    'Agriculture',  'active',    '2019-08-27'),
    ('CLI-0011', 'Meknes Leather Goods',           'Aziz Chafik',       'aziz.chafik@mekncsleather.ma',      '+212661000011', 'Meknes',       'Manufacturing','inactive',  '2015-12-01'),
    ('CLI-0012', 'Rabat FinTech Partners',         'Sofia Berrahou',    'sofia.berrahou@rabatfintech.ma',    '+212661000012', 'Rabat',        'Finance',      'active',    '2021-04-19'),
    ('CLI-0013', 'Casablanca Retail Holding',      'Tarik Amrani',      'tarik.amrani@crholding.ma',         '+212661000013', 'Casablanca',   'Retail',       'active',    '2016-02-14'),
    ('CLI-0014', 'Chefchaouen Tourism Co.',        'Widad Fassi',       'widad.fassi@chefchaouentour.ma',    '+212661000014', 'Chefchaouen',  'Hospitality',  'active',    '2020-10-02'),
    ('CLI-0015', 'Kenitra Auto Components',        'Reda Slaoui',       'reda.slaoui@kenitraauto.ma',        '+212661000015', 'Kenitra',      'Manufacturing','active',    '2018-07-11'),
    ('CLI-0016', 'Beni Mellal AgriTech',           'Hind Ezzahra',      'hind.ezzahra@bmagritech.ma',        '+212661000016', 'Beni Mellal',  'Agriculture',  'prospect',  '2023-09-25'),
    ('CLI-0017', 'Nador Construction Group',       'Younes Barhoun',    'younes.barhoun@nadorconstruction.ma','+212661000017','Nador',        'Construction', 'active',    '2017-03-08'),
    ('CLI-0018', 'Settat Pharma Distribution',     'Ghita Moukrim',     'ghita.moukrim@settatpharma.ma',     '+212661000018', 'Settat',       'Healthcare',   'active',    '2019-11-30'),
    ('CLI-0019', 'Errachidia Mining Corp',         'Anouar Zerhouni',   'anouar.zerhouni@errachidiamining.ma','+212661000019','Errachidia',   'Mining',       'inactive',  '2014-06-21'),
    ('CLI-0020', 'Essaouira Craft Exports',        'Loubna Karimi',     'loubna.karimi@essaouiracrafts.ma',  '+212661000020', 'Essaouira',    'Retail',       'active',    '2021-12-05');

-- ---------------------------------------------------------------------------
-- deals
-- ---------------------------------------------------------------------------
CREATE TABLE deals (
    id                    SERIAL PRIMARY KEY,
    deal_ref              TEXT NOT NULL UNIQUE,
    client_id             INTEGER NOT NULL REFERENCES clients(id),
    account_manager_id    INTEGER NOT NULL REFERENCES employees(id),
    title                 TEXT NOT NULL,
    amount_mad            NUMERIC(12, 2) NOT NULL,
    stage                 TEXT NOT NULL,
    probability           INTEGER NOT NULL,
    created_at            DATE NOT NULL,
    expected_close_date   DATE NOT NULL
);

INSERT INTO deals (deal_ref, client_id, account_manager_id, title, amount_mad, stage, probability, created_at, expected_close_date) VALUES
    ('DEAL-0001', 1,  15, 'Annual textile ERP licensing renewal',      320000.00, 'closed_won',   100, '2024-01-05', '2024-02-15'),
    ('DEAL-0002', 2,  16, 'Cloud migration retainer',                   540000.00, 'negotiation',   70, '2024-11-10', '2025-01-20'),
    ('DEAL-0003', 3,  4,  'Fleet tracking platform rollout',            875000.00, 'closed_won',   100, '2023-08-01', '2023-10-30'),
    ('DEAL-0004', 4,  17, 'Export compliance consulting',               210000.00, 'proposal',      50, '2025-02-14', '2025-05-01'),
    ('DEAL-0005', 5,  15, 'Point-of-sale hardware upgrade',             150000.00, 'closed_won',   100, '2023-03-22', '2023-05-10'),
    ('DEAL-0006', 6,  16, 'Port logistics analytics dashboard',        1200000.00, 'negotiation',   65, '2025-01-15', '2025-04-30'),
    ('DEAL-0007', 7,  17, 'Solar plant monitoring pilot',               380000.00, 'prospecting',   20, '2025-03-01', '2025-08-15'),
    ('DEAL-0008', 8,  4,  'Steel plant safety system integration',      690000.00, 'closed_won',   100, '2022-09-14', '2022-12-01'),
    ('DEAL-0009', 9,  17, 'Renewable energy CRM onboarding',            275000.00, 'prospecting',   15, '2025-04-10', '2025-09-01'),
    ('DEAL-0010', 10, 15, 'Cold chain tracking devices',                430000.00, 'closed_won',   100, '2023-06-06', '2023-08-20'),
    ('DEAL-0011', 12, 16, 'FinTech API integration package',            610000.00, 'closed_won',   100, '2024-05-02', '2024-07-18'),
    ('DEAL-0012', 13, 4,  'Retail chain inventory system',              950000.00, 'negotiation',   60, '2024-12-01', '2025-03-15'),
    ('DEAL-0013', 14, 17, 'Tourism booking platform',                   180000.00, 'closed_lost',    0, '2023-11-20', '2024-01-10'),
    ('DEAL-0014', 15, 15, 'Auto parts supply chain optimization',       720000.00, 'closed_won',   100, '2022-04-11', '2022-07-01'),
    ('DEAL-0015', 16, 16, 'AgriTech IoT sensor rollout',                340000.00, 'proposal',      45, '2025-02-28', '2025-06-30'),
    ('DEAL-0016', 17, 17, 'Construction project management suite',      520000.00, 'closed_won',   100, '2023-02-15', '2023-05-01'),
    ('DEAL-0017', 18, 4,  'Pharma distribution compliance audit',       260000.00, 'closed_won',   100, '2024-03-19', '2024-06-05'),
    ('DEAL-0018', 19, 15, 'Mining fleet telematics',                    890000.00, 'closed_lost',    0, '2023-07-08', '2023-10-01'),
    ('DEAL-0019', 20, 16, 'Artisan export e-commerce platform',         195000.00, 'closed_won',   100, '2024-08-22', '2024-10-30'),
    ('DEAL-0020', 11, 17, 'Legacy leather goods POS revamp',            140000.00, 'closed_lost',    0, '2022-01-10', '2022-04-01');

-- ---------------------------------------------------------------------------
-- invoices
-- ---------------------------------------------------------------------------
CREATE TABLE invoices (
    id               SERIAL PRIMARY KEY,
    invoice_number   TEXT NOT NULL UNIQUE,
    client_id        INTEGER NOT NULL REFERENCES clients(id),
    amount_mad       NUMERIC(12, 2) NOT NULL,
    payment_status   TEXT NOT NULL,
    issued_at        DATE NOT NULL,
    due_at           DATE NOT NULL
);

INSERT INTO invoices (invoice_number, client_id, amount_mad, payment_status, issued_at, due_at) VALUES
    ('INV-2024-0001', 1,  32000.00,  'paid',    '2024-02-15', '2024-03-15'),
    ('INV-2024-0002', 3,  87500.00,  'paid',    '2023-10-30', '2023-11-30'),
    ('INV-2024-0003', 5,  15000.00,  'paid',    '2023-05-10', '2023-06-10'),
    ('INV-2024-0004', 8,  69000.00,  'paid',    '2022-12-01', '2022-12-31'),
    ('INV-2024-0005', 10, 43000.00,  'overdue', '2023-08-20', '2023-09-20'),
    ('INV-2024-0006', 12, 61000.00,  'paid',    '2024-07-18', '2024-08-18'),
    ('INV-2024-0007', 15, 72000.00,  'paid',    '2022-07-01', '2022-07-31'),
    ('INV-2024-0008', 17, 52000.00,  'paid',    '2023-05-01', '2023-05-31'),
    ('INV-2024-0009', 18, 26000.00,  'pending', '2024-06-05', '2024-07-05'),
    ('INV-2024-0010', 20, 19500.00,  'paid',    '2024-10-30', '2024-11-30'),
    ('INV-2024-0011', 2,  54000.00,  'pending', '2025-01-05', '2025-02-05'),
    ('INV-2024-0012', 6,  120000.00, 'pending', '2025-02-01', '2025-03-01'),
    ('INV-2024-0013', 13, 95000.00,  'overdue', '2025-01-01', '2025-01-31'),
    ('INV-2024-0014', 4,  21000.00,  'pending', '2025-03-01', '2025-04-01'),
    ('INV-2024-0015', 9,  27500.00,  'pending', '2025-04-15', '2025-05-15'),
    ('INV-2024-0016', 1,  32000.00,  'paid',    '2023-02-15', '2023-03-15'),
    ('INV-2024-0017', 11, 14000.00,  'overdue', '2022-04-01', '2022-05-01'),
    ('INV-2024-0018', 16, 34000.00,  'pending', '2025-03-01', '2025-04-01'),
    ('INV-2024-0019', 19, 89000.00,  'overdue', '2023-10-01', '2023-11-01'),
    ('INV-2024-0020', 7,  38000.00,  'pending', '2025-03-15', '2025-04-15');

-- ---------------------------------------------------------------------------
-- projects
-- ---------------------------------------------------------------------------
CREATE TABLE projects (
    id                     SERIAL PRIMARY KEY,
    project_code           TEXT NOT NULL UNIQUE,
    client_id              INTEGER NOT NULL REFERENCES clients(id),
    project_name           TEXT NOT NULL,
    project_manager        TEXT NOT NULL,
    budget_mad             NUMERIC(12, 2) NOT NULL,
    status                 TEXT NOT NULL,
    start_date             DATE NOT NULL,
    expected_end_date      DATE NOT NULL
);

INSERT INTO projects (project_code, client_id, project_name, project_manager, budget_mad, status, start_date, expected_end_date) VALUES
    ('PRJ-0001', 1,  'Textile ERP Rollout',                'Imane Ziani',    280000.00, 'completed',   '2024-02-20', '2024-06-30'),
    ('PRJ-0002', 2,  'Cloud Migration Phase 1',             'Adil Kabbaj',    460000.00, 'in_progress', '2025-01-25', '2025-06-15'),
    ('PRJ-0003', 3,  'Fleet Tracking Platform',             'Karim El Idrissi',780000.00,'completed',   '2023-11-01', '2024-03-01'),
    ('PRJ-0004', 6,  'Port Analytics Dashboard',            'Youssef Alaoui', 950000.00, 'in_progress', '2025-02-01', '2025-08-01'),
    ('PRJ-0005', 8,  'Steel Plant Safety Integration',      'Nadia Chraibi',  610000.00, 'completed',   '2022-12-05', '2023-04-01'),
    ('PRJ-0006', 10, 'Cold Chain Tracking Deployment',      'Karim El Idrissi',390000.00,'completed',   '2023-08-25', '2023-12-01'),
    ('PRJ-0007', 12, 'FinTech API Integration',             'Adil Kabbaj',    540000.00, 'completed',   '2024-07-20', '2024-11-01'),
    ('PRJ-0008', 13, 'Retail Inventory System',             'Imane Ziani',    820000.00, 'in_progress', '2025-01-10', '2025-07-01'),
    ('PRJ-0009', 15, 'Auto Parts Supply Chain Optimization','Youssef Alaoui', 650000.00, 'completed',   '2022-07-05', '2022-12-15'),
    ('PRJ-0010', 17, 'Construction PM Suite Deployment',    'Karim El Idrissi',470000.00,'completed',   '2023-05-05', '2023-09-01'),
    ('PRJ-0011', 18, 'Pharma Compliance Audit Platform',    'Nadia Chraibi',  230000.00, 'completed',   '2024-06-10', '2024-09-01'),
    ('PRJ-0012', 20, 'Artisan Export E-commerce Build',     'Adil Kabbaj',    175000.00, 'on_hold',     '2024-11-01', '2025-03-01');

-- ---------------------------------------------------------------------------
-- users (BlueOffice internal portal / application accounts - separate from
-- the "flags" database seeded in 02-flags.sql)
-- ---------------------------------------------------------------------------
CREATE TABLE users (
    id           SERIAL PRIMARY KEY,
    username     TEXT NOT NULL UNIQUE,
    full_name    TEXT NOT NULL,
    email        TEXT NOT NULL,
    role         TEXT NOT NULL,
    department   TEXT NOT NULL,
    last_login   TIMESTAMP,
    internal_note TEXT
);

INSERT INTO users (username, full_name, email, role, department, last_login, internal_note) VALUES
    ('nabil.elamrani',  'Nabil El Amrani',   'nabil.elamrani@blueoffice.local',   'admin',   'Executive',        '2025-08-20 09:12:00', 'Primary platform owner.'),
    ('sana.amrani',     'Sana Amrani',       'sana.amrani@blueoffice.local',      'manager', 'Human Resources',  '2025-08-19 14:05:00', 'Manages onboarding workflows.'),
    ('rachid.belhaj',   'Rachid Belhaj',     'rachid.belhaj@blueoffice.local',    'manager', 'Finance',          '2025-08-18 08:44:00', 'Reviews monthly invoice exports.'),
    ('youssef.bennani', 'Youssef Bennani',   'youssef.bennani@blueoffice.local',  'manager', 'Sales',            '2025-08-20 11:30:00', 'Owns the deals pipeline dashboard.'),
    ('imane.ziani',     'Imane Ziani',       'imane.ziani@blueoffice.local',      'admin',   'IT',               '2025-08-21 07:58:00', 'IT platform administrator.'),
    ('hamza.tazi',      'Hamza Tazi',        'hamza.tazi@blueoffice.local',       'manager', 'Security',         '2025-08-17 16:20:00', 'Requested quarterly access review.'),
    ('karim.elidrissi', 'Karim El Idrissi',  'karim.elidrissi@blueoffice.local',  'staff',   'IT',               '2025-08-20 10:02:00', 'Backend engineer, deploys via CI.'),
    ('nadia.chraibi',   'Nadia Chraibi',     'nadia.chraibi@blueoffice.local',    'staff',   'Security',         '2025-08-19 09:47:00', 'Runs monthly vulnerability scans.'),
    ('adil.kabbaj',     'Adil Kabbaj',       'adil.kabbaj@blueoffice.local',      'staff',   'IT',               '2025-08-21 08:15:00', 'Manages the Linux server fleet.'),
    ('yassine.bouzid',  'Yassine Bouzid',    'yassine.bouzid@blueoffice.local',   'staff',   'Sales',            '2025-08-16 13:40:00', 'Top account executive Q2 2025.'),
    ('rania.alaoui',    'Rania Alaoui',      'rania.alaoui@blueoffice.local',     'staff',   'Customer Success', '2025-08-15 09:00:00', 'Handles enterprise support tickets.'),
    ('zineb.amine',     'Zineb Amine',       'zineb.amine@blueoffice.local',      'staff',   'Operations',       '2025-08-14 12:25:00', 'Coordinates vendor logistics.'),
    ('houda.cherkaoui', 'Houda Cherkaoui',   'houda.cherkaoui@blueoffice.local',  'viewer',  'Finance',          '2025-08-12 15:10:00', 'Read-only reporting access.'),
    ('yasmine.toumi',   'Yasmine Toumi',     'yasmine.toumi@blueoffice.local',    'staff',   'IT',               '2025-08-20 09:33:00', 'Handles internal helpdesk tickets.'),
    ('auditor.readonly','External Auditor',  'auditor@blueoffice.local',          'viewer',  'Finance',          '2025-07-30 10:00:00', 'Temporary account for the annual audit.');
