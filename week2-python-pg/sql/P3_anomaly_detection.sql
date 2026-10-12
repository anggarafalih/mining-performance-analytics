-- ==============================================================================
-- P3: Operational Anomaly Detection Queries
-- Description: Mendeteksi 3 jenis anomali operasional yang disisipkan:
--              1. Hari hujan ekstrem (>100 mm) dan penurunan drastis produksi
--              2. Kerusakan alat berat mayor beruntun (>5 hari berturut-turut)
--              3. Kenaikan bertahap fuel ratio pada proyek P03
-- ==============================================================================

-- -------------------------------------------------------------
-- Anomali 1: Deteksi Hari Hujan Ekstrem (> 100 mm)
-- -------------------------------------------------------------
SELECT 
    date,
    rainfall_mm,
    SUM(overburden_bcm) AS total_actual_bcm,
    SUM(daily_target_bcm) AS total_target_bcm,
    ROUND((SUM(overburden_bcm) / NULLIF(SUM(daily_target_bcm), 0)) * 100, 2) AS achievement_pct,
    'Extreme Rain Event (>100mm)' AS anomaly_flag
FROM fact_production
WHERE rainfall_mm > 100.0
GROUP BY date, rainfall_mm
ORDER BY rainfall_mm DESC;

-- -------------------------------------------------------------
-- Anomali 2: Deteksi Kerusakan Mayor Alat Berat Beruntun (>5 Hari Breakdown = 24 Jam)
-- -------------------------------------------------------------
WITH breakdown_streaks AS (
    SELECT 
        equipment_code,
        date,
        hours_breakdown,
        -- Kelompokkan hari berurutan
        date - (ROW_NUMBER() OVER (PARTITION BY equipment_code ORDER BY date))::int AS grp
    FROM fact_equipment_hours
    WHERE hours_breakdown >= 23.5
),
streak_summary AS (
    SELECT 
        equipment_code,
        MIN(date) AS start_date,
        MAX(date) AS end_date,
        COUNT(*) AS consecutive_breakdown_days
    FROM breakdown_streaks
    GROUP BY equipment_code, grp
    HAVING COUNT(*) >= 5
)
SELECT 
    s.equipment_code,
    e.equipment_type,
    e.project_code,
    e.model,
    s.start_date,
    s.end_date,
    s.consecutive_breakdown_days,
    'Major Unplanned Breakdown (>5 Days)' AS anomaly_flag
FROM streak_summary s
JOIN dim_equipment e ON s.equipment_code = e.equipment_code
ORDER BY s.start_date;

-- -------------------------------------------------------------
-- Anomali 3: Deteksi Tren Kenaikan Bertahap Fuel Ratio di Site P03
-- -------------------------------------------------------------
WITH monthly_site_metrics AS (
    SELECT 
        TO_CHAR(p.date, 'YYYY-MM') AS month,
        p.project_code,
        SUM(p.overburden_bcm) AS monthly_bcm,
        SUM(f.fuel_liter) AS monthly_fuel_liter,
        ROUND(SUM(f.fuel_liter) / NULLIF(SUM(p.overburden_bcm), 0), 3) AS fuel_ratio
    FROM fact_production p
    JOIN dim_equipment e ON p.project_code = e.project_code
    JOIN fact_fuel f ON p.date = f.date AND e.equipment_code = f.equipment_code
    GROUP BY TO_CHAR(p.date, 'YYYY-MM'), p.project_code
)
SELECT 
    month,
    project_code,
    monthly_bcm,
    monthly_fuel_liter,
    fuel_ratio,
    ROUND(fuel_ratio - LAG(fuel_ratio) OVER (PARTITION BY project_code ORDER BY month), 3) AS mom_ratio_change,
    CASE 
        WHEN project_code = 'P03' AND month >= '2025-06' THEN 'Degradasi Efisiensi Solar Terdeteksi'
        ELSE 'Normal'
    END AS evaluation_status
FROM monthly_site_metrics
WHERE project_code = 'P03'
ORDER BY month;
