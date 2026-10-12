-- ==============================================================================
-- Schema: Mining Production Performance Analytics (SQL Server 2022 / T-SQL)
-- Author: @faleh
-- Description: Konversi skema PostgreSQL ke T-SQL dengan IDENTITY, NVARCHAR,
--              DECIMAL, dan CREATE OR ALTER VIEW.
-- ==============================================================================

USE master;
GO

IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = N'mining_analytics')
BEGIN
    CREATE DATABASE mining_analytics;
END
GO

USE mining_analytics;
GO

-- -------------------------------------------------------------
-- 1. Dimensi Proyek (Site Tambang)
-- -------------------------------------------------------------
IF OBJECT_ID(N'dbo.dim_project', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.dim_project (
        project_code NVARCHAR(10) NOT NULL PRIMARY KEY,
        project_name NVARCHAR(100) NOT NULL,
        location NVARCHAR(100) NOT NULL,
        material_type NVARCHAR(100) NOT NULL
    );
END
GO

-- -------------------------------------------------------------
-- 2. Dimensi Alat Berat (Fleet)
-- -------------------------------------------------------------
IF OBJECT_ID(N'dbo.dim_equipment', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.dim_equipment (
        equipment_code NVARCHAR(20) NOT NULL PRIMARY KEY,
        equipment_type NVARCHAR(50) NOT NULL,
        project_code NVARCHAR(10) NOT NULL FOREIGN KEY REFERENCES dbo.dim_project(project_code),
        model NVARCHAR(100) NOT NULL,
        capacity DECIMAL(10, 2) NOT NULL,
        capacity_unit NVARCHAR(20) NOT NULL
    );
END
GO

-- -------------------------------------------------------------
-- 3. Fakta Produksi Harian
-- -------------------------------------------------------------
IF OBJECT_ID(N'dbo.fact_production', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.fact_production (
        id INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
        date DATE NOT NULL,
        project_code NVARCHAR(10) NOT NULL FOREIGN KEY REFERENCES dbo.dim_project(project_code),
        overburden_bcm DECIMAL(12, 2) NOT NULL CHECK (overburden_bcm >= 0),
        coal_ton DECIMAL(12, 2) NOT NULL CHECK (coal_ton >= 0),
        daily_target_bcm DECIMAL(12, 2) NOT NULL CHECK (daily_target_bcm >= 0),
        daily_target_coal DECIMAL(12, 2) NOT NULL CHECK (daily_target_coal >= 0),
        rainfall_mm DECIMAL(8, 2) NOT NULL CHECK (rainfall_mm >= 0),
        CONSTRAINT UQ_production_date_project UNIQUE (date, project_code)
    );
END
GO

-- -------------------------------------------------------------
-- 4. Fakta Jam Kerja Operasional Alat
-- -------------------------------------------------------------
IF OBJECT_ID(N'dbo.fact_equipment_hours', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.fact_equipment_hours (
        id INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
        date DATE NOT NULL,
        equipment_code NVARCHAR(20) NOT NULL FOREIGN KEY REFERENCES dbo.dim_equipment(equipment_code),
        hours_working DECIMAL(6, 2) NOT NULL CHECK (hours_working >= 0),
        hours_standby DECIMAL(6, 2) NOT NULL CHECK (hours_standby >= 0),
        hours_breakdown DECIMAL(6, 2) NOT NULL CHECK (hours_breakdown >= 0),
        hours_available DECIMAL(6, 2) NOT NULL CHECK (hours_available >= 0),
        CONSTRAINT CHK_hours_sum CHECK (ROUND(hours_working + hours_standby + hours_breakdown, 2) <= 24.00),
        CONSTRAINT UQ_hours_date_equipment UNIQUE (date, equipment_code)
    );
END
GO

-- -------------------------------------------------------------
-- 5. Fakta Konsumsi Bahan Bakar (Solar)
-- -------------------------------------------------------------
IF OBJECT_ID(N'dbo.fact_fuel', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.fact_fuel (
        id INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
        date DATE NOT NULL,
        equipment_code NVARCHAR(20) NOT NULL FOREIGN KEY REFERENCES dbo.dim_equipment(equipment_code),
        fuel_liter DECIMAL(10, 2) NOT NULL CHECK (fuel_liter >= 0),
        fuel_price_idr DECIMAL(12, 2) NOT NULL CHECK (fuel_price_idr >= 0),
        CONSTRAINT UQ_fuel_date_equipment UNIQUE (date, equipment_code)
    );
END
GO

-- -------------------------------------------------------------
-- 6. Anggaran Biaya Bulanan (Budget)
-- -------------------------------------------------------------
IF OBJECT_ID(N'dbo.budget_monthly', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.budget_monthly (
        id INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
        month NVARCHAR(7) NOT NULL, -- Format YYYY-MM
        project_code NVARCHAR(10) NOT NULL FOREIGN KEY REFERENCES dbo.dim_project(project_code),
        target_overburden_bcm DECIMAL(14, 2) NOT NULL,
        target_coal_ton DECIMAL(14, 2) NOT NULL,
        budget_fuel_liter DECIMAL(14, 2) NOT NULL,
        budget_fuel_price_idr DECIMAL(12, 2) NOT NULL,
        budget_fuel_cost_idr DECIMAL(16, 2) NOT NULL,
        budget_other_cost_idr DECIMAL(16, 2) NOT NULL,
        total_budget_cost_idr DECIMAL(16, 2) NOT NULL,
        CONSTRAINT UQ_budget_month_project UNIQUE (month, project_code)
    );
END
GO

-- -------------------------------------------------------------
-- 7. View: v_daily_performance
-- -------------------------------------------------------------
CREATE OR ALTER VIEW dbo.v_daily_performance AS
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
    FROM dbo.fact_equipment_hours h
    JOIN dbo.dim_equipment e ON h.equipment_code = e.equipment_code
    JOIN dbo.fact_fuel f ON h.date = f.date AND h.equipment_code = f.equipment_code
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
    -- KPI Tambang
    CASE 
        WHEN COALESCE(ed.total_hours_available, 0) > 0 
        THEN ROUND(((ed.total_hours_available - ed.total_hours_breakdown) / ed.total_hours_available) * 100.0, 2)
        ELSE 0.00 
    END AS physical_availability_pct,
    CASE 
        WHEN COALESCE(ed.total_hours_available, 0) > 0 
        THEN ROUND((ed.total_hours_working / ed.total_hours_available) * 100.0, 2)
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
FROM dbo.fact_production p
JOIN dbo.dim_project pr ON p.project_code = pr.project_code
LEFT JOIN eq_daily ed ON p.date = ed.date AND p.project_code = ed.project_code;
GO

-- -------------------------------------------------------------
-- 8. View: v_monthly_variance
-- -------------------------------------------------------------
CREATE OR ALTER VIEW dbo.v_monthly_variance AS
WITH monthly_actual AS (
    SELECT 
        FORMAT(date, 'yyyy-MM') AS month,
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
    FROM dbo.v_daily_performance
    GROUP BY FORMAT(date, 'yyyy-MM'), project_code
)
SELECT 
    b.month,
    b.project_code,
    pr.project_name,
    a.actual_overburden_bcm,
    a.actual_coal_ton,
    a.actual_fuel_liter,
    a.actual_fuel_cost_idr,
    ROUND(a.actual_fuel_ratio, 3) AS actual_fuel_ratio,
    ROUND(a.actual_fuel_price_avg, 2) AS actual_fuel_price_avg,
    b.target_overburden_bcm AS budget_overburden_bcm,
    b.target_coal_ton AS budget_coal_ton,
    b.budget_fuel_liter,
    b.budget_fuel_cost_idr,
    ROUND(b.budget_fuel_liter / b.target_overburden_bcm, 3) AS budget_fuel_ratio,
    b.budget_fuel_price_idr,
    -- Varians
    ROUND(a.actual_fuel_cost_idr - b.budget_fuel_cost_idr, 2) AS total_fuel_cost_variance_idr,
    ROUND((a.actual_overburden_bcm - b.target_overburden_bcm) * (b.budget_fuel_liter / b.target_overburden_bcm) * b.budget_fuel_price_idr, 2) AS volume_effect_idr,
    ROUND(a.actual_overburden_bcm * (a.actual_fuel_ratio - (b.budget_fuel_liter / b.target_overburden_bcm)) * b.budget_fuel_price_idr, 2) AS efficiency_effect_idr,
    ROUND(a.actual_overburden_bcm * a.actual_fuel_ratio * (a.actual_fuel_price_avg - b.budget_fuel_price_idr), 2) AS price_effect_idr
FROM dbo.budget_monthly b
JOIN dbo.dim_project pr ON b.project_code = pr.project_code
JOIN monthly_actual a ON b.month = a.month AND b.project_code = a.project_code;
GO
