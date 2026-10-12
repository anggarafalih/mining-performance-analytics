-- ==============================================================================
-- Schema: Mining Production Performance Analytics (PostgreSQL 16)
-- Author: @faleh
-- Description: DDL skema database, constraint integritas, dan views analitik
-- ==============================================================================

-- Drop existing views and tables if rebuilding
DROP VIEW IF EXISTS v_monthly_variance CASCADE;
DROP VIEW IF EXISTS v_daily_performance CASCADE;

DROP TABLE IF EXISTS fact_fuel CASCADE;
DROP TABLE IF EXISTS fact_equipment_hours CASCADE;
DROP TABLE IF EXISTS fact_production CASCADE;
DROP TABLE IF EXISTS budget_monthly CASCADE;
DROP TABLE IF EXISTS dim_equipment CASCADE;
DROP TABLE IF EXISTS dim_project CASCADE;

-- -------------------------------------------------------------
-- 1. Dimensi Proyek (Site Tambang)
-- -------------------------------------------------------------
CREATE TABLE dim_project (
    project_code VARCHAR(10) PRIMARY KEY,
    project_name VARCHAR(100) NOT NULL,
    location VARCHAR(100) NOT NULL,
    material_type VARCHAR(100) NOT NULL
);

-- -------------------------------------------------------------
-- 2. Dimensi Alat Berat (Fleet)
-- -------------------------------------------------------------
CREATE TABLE dim_equipment (
    equipment_code VARCHAR(20) PRIMARY KEY,
    equipment_type VARCHAR(50) NOT NULL,
    project_code VARCHAR(10) NOT NULL REFERENCES dim_project(project_code),
    model VARCHAR(100) NOT NULL,
    capacity NUMERIC(10, 2) NOT NULL,
    capacity_unit VARCHAR(20) NOT NULL
);

-- -------------------------------------------------------------
-- 3. Fakta Produksi Harian
-- -------------------------------------------------------------
CREATE TABLE fact_production (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    project_code VARCHAR(10) NOT NULL REFERENCES dim_project(project_code),
    overburden_bcm NUMERIC(12, 2) NOT NULL CHECK (overburden_bcm >= 0),
    coal_ton NUMERIC(12, 2) NOT NULL CHECK (coal_ton >= 0),
    daily_target_bcm NUMERIC(12, 2) NOT NULL CHECK (daily_target_bcm >= 0),
    daily_target_coal NUMERIC(12, 2) NOT NULL CHECK (daily_target_coal >= 0),
    rainfall_mm NUMERIC(8, 2) NOT NULL CHECK (rainfall_mm >= 0),
    CONSTRAINT uq_production_date_project UNIQUE (date, project_code)
);

-- -------------------------------------------------------------
-- 4. Fakta Jam Kerja Operasional Alat
-- -------------------------------------------------------------
CREATE TABLE fact_equipment_hours (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    equipment_code VARCHAR(20) NOT NULL REFERENCES dim_equipment(equipment_code),
    hours_working NUMERIC(6, 2) NOT NULL CHECK (hours_working >= 0),
    hours_standby NUMERIC(6, 2) NOT NULL CHECK (hours_standby >= 0),
    hours_breakdown NUMERIC(6, 2) NOT NULL CHECK (hours_breakdown >= 0),
    hours_available NUMERIC(6, 2) NOT NULL CHECK (hours_available >= 0),
    CONSTRAINT chk_hours_sum CHECK (ROUND(hours_working + hours_standby + hours_breakdown, 2) <= 24.00),
    CONSTRAINT uq_hours_date_equipment UNIQUE (date, equipment_code)
);

-- -------------------------------------------------------------
-- 5. Fakta Konsumsi Bahan Bakar (Solar)
-- -------------------------------------------------------------
CREATE TABLE fact_fuel (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    equipment_code VARCHAR(20) NOT NULL REFERENCES dim_equipment(equipment_code),
    fuel_liter NUMERIC(10, 2) NOT NULL CHECK (fuel_liter >= 0),
    fuel_price_idr NUMERIC(12, 2) NOT NULL CHECK (fuel_price_idr >= 0),
    CONSTRAINT uq_fuel_date_equipment UNIQUE (date, equipment_code)
);

-- -------------------------------------------------------------
-- 6. Anggaran Biaya Bulanan (Budget)
-- -------------------------------------------------------------
CREATE TABLE budget_monthly (
    id SERIAL PRIMARY KEY,
    month VARCHAR(7) NOT NULL, -- Format YYYY-MM
    project_code VARCHAR(10) NOT NULL REFERENCES dim_project(project_code),
    target_overburden_bcm NUMERIC(14, 2) NOT NULL,
    target_coal_ton NUMERIC(14, 2) NOT NULL,
    budget_fuel_liter NUMERIC(14, 2) NOT NULL,
    budget_fuel_price_idr NUMERIC(12, 2) NOT NULL,
    budget_fuel_cost_idr NUMERIC(16, 2) NOT NULL,
    budget_other_cost_idr NUMERIC(16, 2) NOT NULL,
    total_budget_cost_idr NUMERIC(16, 2) NOT NULL,
    CONSTRAINT uq_budget_month_project UNIQUE (month, project_code)
);

-- -------------------------------------------------------------
-- Indices for Performance Optimization
-- -------------------------------------------------------------
CREATE INDEX idx_prod_date_proj ON fact_production(date, project_code);
CREATE INDEX idx_hours_date_eq ON fact_equipment_hours(date, equipment_code);
CREATE INDEX idx_fuel_date_eq ON fact_fuel(date, equipment_code);

-- -------------------------------------------------------------
-- 7. View: v_daily_performance
-- Agregasi performa operasional harian per proyek
-- -------------------------------------------------------------
CREATE OR REPLACE VIEW v_daily_performance AS
WITH eq_daily AS (
    SELECT 
        h.date,
        e.project_code,
        SUM(h.hours_working) AS total_hours_working,
        SUM(h.hours_standby) AS total_hours_standby,
        SUM(h.hours_breakdown) AS total_hours_breakdown,
        SUM(h.hours_available) AS total_hours_available,
        SUM(f.fuel_liter) AS total_fuel_liter,
        SUM(f.fuel_liter * f.fuel_price_idr) AS total_fuel_cost_idr
    FROM fact_equipment_hours h
    JOIN dim_equipment e ON h.equipment_code = e.equipment_code
    JOIN fact_fuel f ON h.date = f.date AND h.equipment_code = f.equipment_code
    GROUP BY h.date, e.project_code
)
SELECT 
    p.date,
    p.project_code,
    pr.project_name,
    p.overburden_bcm,
    p.coal_ton,
    p.daily_target_bcm,
    p.daily_target_coal,
    p.rainfall_mm,
    COALESCE(ed.total_hours_working, 0) AS hours_working,
    COALESCE(ed.total_hours_standby, 0) AS hours_standby,
    COALESCE(ed.total_hours_breakdown, 0) AS hours_breakdown,
    COALESCE(ed.total_hours_available, 0) AS hours_available,
    COALESCE(ed.total_fuel_liter, 0) AS fuel_liter,
    COALESCE(ed.total_fuel_cost_idr, 0) AS fuel_cost_idr,
    -- KPI Tambang Baku
    CASE 
        WHEN COALESCE(ed.total_hours_available, 0) > 0 
        THEN ROUND(((ed.total_hours_available - ed.total_hours_breakdown) / ed.total_hours_available) * 100, 2)
        ELSE 0.00 
    END AS physical_availability_pct,
    CASE 
        WHEN COALESCE(ed.total_hours_available, 0) > 0 
        THEN ROUND((ed.total_hours_working / ed.total_hours_available) * 100, 2)
        ELSE 0.00 
    END AS utilization_pct,
    CASE 
        WHEN COALESCE(ed.total_hours_working, 0) > 0 
        THEN ROUND(p.overburden_bcm / ed.total_hours_working, 2)
        ELSE 0.00 
    END AS productivity_bcm_per_hour,
    CASE 
        WHEN p.overburden_bcm > 0 
        THEN ROUND(COALESCE(ed.total_fuel_liter, 0) / p.overburden_bcm, 3)
        ELSE 0.000 
    END AS fuel_ratio_l_per_bcm
FROM fact_production p
JOIN dim_project pr ON p.project_code = pr.project_code
LEFT JOIN eq_daily ed ON p.date = ed.date AND p.project_code = ed.project_code;

-- -------------------------------------------------------------
-- 8. View: v_monthly_variance
-- Pemecahan varians anggaran bulanan (Volume, Harga, Efisiensi)
-- -------------------------------------------------------------
CREATE OR REPLACE VIEW v_monthly_variance AS
WITH monthly_actual AS (
    SELECT 
        TO_CHAR(date, 'YYYY-MM') AS month,
        project_code,
        SUM(overburden_bcm) AS actual_overburden_bcm,
        SUM(coal_ton) AS actual_coal_ton,
        SUM(fuel_liter) AS actual_fuel_liter,
        SUM(fuel_cost_idr) AS actual_fuel_cost_idr,
        CASE 
            WHEN SUM(overburden_bcm) > 0 THEN SUM(fuel_liter) / SUM(overburden_bcm)
            ELSE 0 
        END AS actual_fuel_ratio,
        CASE 
            WHEN SUM(fuel_liter) > 0 THEN SUM(fuel_cost_idr) / SUM(fuel_liter)
            ELSE 0 
        END AS actual_fuel_price_avg
    FROM v_daily_performance
    GROUP BY TO_CHAR(date, 'YYYY-MM'), project_code
)
SELECT 
    b.month,
    b.project_code,
    pr.project_name,
    -- Actuals
    a.actual_overburden_bcm,
    a.actual_coal_ton,
    a.actual_fuel_liter,
    a.actual_fuel_cost_idr,
    ROUND(a.actual_fuel_ratio, 3) AS actual_fuel_ratio,
    ROUND(a.actual_fuel_price_avg, 2) AS actual_fuel_price_avg,
    -- Budgets
    b.target_overburden_bcm AS budget_overburden_bcm,
    b.target_coal_ton AS budget_coal_ton,
    b.budget_fuel_liter,
    b.budget_fuel_cost_idr,
    ROUND(b.budget_fuel_liter / b.target_overburden_bcm, 3) AS budget_fuel_ratio,
    b.budget_fuel_price_idr,
    -- Total Variance
    ROUND(a.actual_fuel_cost_idr - b.budget_fuel_cost_idr, 2) AS total_fuel_cost_variance_idr,
    -- 3-Way Variance Decomposition
    -- 1. Volume Effect: (Actual_BCM - Budget_BCM) * Budget_Ratio * Budget_Price
    ROUND((a.actual_overburden_bcm - b.target_overburden_bcm) * (b.budget_fuel_liter / b.target_overburden_bcm) * b.budget_fuel_price_idr, 2) AS volume_effect_idr,
    -- 2. Efficiency Effect: Actual_BCM * (Actual_Ratio - Budget_Ratio) * Budget_Price
    ROUND(a.actual_overburden_bcm * (a.actual_fuel_ratio - (b.budget_fuel_liter / b.target_overburden_bcm)) * b.budget_fuel_price_idr, 2) AS efficiency_effect_idr,
    -- 3. Price Effect: Actual_BCM * Actual_Ratio * (Actual_Price - Budget_Price)
    ROUND(a.actual_overburden_bcm * a.actual_fuel_ratio * (a.actual_fuel_price_avg - b.budget_fuel_price_idr), 2) AS price_effect_idr
FROM budget_monthly b
JOIN dim_project pr ON b.project_code = pr.project_code
JOIN monthly_actual a ON b.month = a.month AND b.project_code = a.project_code;
