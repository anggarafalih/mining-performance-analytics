-- ==============================================================================
-- P1: Data Validation & Integrity Checks
-- Description: Memvalidasi integritas data: kelengkapan baris, kontinuitas tanggal,
--              integritas referensial (foreign keys), dan batasan operasional jam alat.
-- ==============================================================================

-- 1. Verifikasi Jumlah Baris per Tabel
SELECT 'dim_project' AS table_name, COUNT(*) AS row_count, 4 AS expected_count FROM dim_project
UNION ALL
SELECT 'dim_equipment', COUNT(*), 20 FROM dim_equipment
UNION ALL
SELECT 'fact_production', COUNT(*), 1460 FROM fact_production
UNION ALL
SELECT 'fact_equipment_hours', COUNT(*), 7300 FROM fact_equipment_hours
UNION ALL
SELECT 'fact_fuel', COUNT(*), 7300 FROM fact_fuel
UNION ALL
SELECT 'budget_monthly', COUNT(*), 48 FROM budget_monthly;

-- 2. Verifikasi Kontinuitas Tanggal (Tidak Ada Tanggal yang Hilang di 2025)
WITH calendar_expected AS (
    SELECT generate_series('2025-01-01'::date, '2025-12-31'::date, '1 day'::interval)::date AS expected_date
),
missing_dates_production AS (
    SELECT c.expected_date
    FROM calendar_expected c
    LEFT JOIN fact_production p ON c.expected_date = p.date
    WHERE p.date IS NULL
)
SELECT 'Missing Production Dates' AS check_name, COUNT(*) AS missing_count 
FROM missing_dates_production;

-- 3. Verifikasi Orphan Foreign Keys
SELECT 'Orphan Equipment Project' AS check_name, COUNT(*) AS violation_count
FROM dim_equipment e
LEFT JOIN dim_project p ON e.project_code = p.project_code
WHERE p.project_code IS NULL
UNION ALL
SELECT 'Orphan Production Project', COUNT(*)
FROM fact_production pr
LEFT JOIN dim_project p ON pr.project_code = p.project_code
WHERE p.project_code IS NULL
UNION ALL
SELECT 'Orphan Hours Equipment', COUNT(*)
FROM fact_equipment_hours h
LEFT JOIN dim_equipment e ON h.equipment_code = e.equipment_code
WHERE e.equipment_code IS NULL
UNION ALL
SELECT 'Orphan Fuel Equipment', COUNT(*)
FROM fact_fuel f
LEFT JOIN dim_equipment e ON f.equipment_code = e.equipment_code
WHERE e.equipment_code IS NULL;

-- 4. Verifikasi Batasan Jam Operasional Alat (Sum <= 24.0)
SELECT 
    'Equipment Hours Violations (> 24 hrs)' AS check_name,
    COUNT(*) AS violation_count,
    MAX(ROUND(hours_working + hours_standby + hours_breakdown, 2)) AS max_hours_found
FROM fact_equipment_hours
WHERE ROUND(hours_working + hours_standby + hours_breakdown, 2) > 24.00;
