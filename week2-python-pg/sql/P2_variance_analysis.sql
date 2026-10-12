-- ==============================================================================
-- P2: Diagnostic Variance Analysis (3-Way Decomposition)
-- Description: Menganalisis selisih biaya solar aktual vs anggaran per proyek per bulan.
--              Memecah varians menjadi Efek Volume, Efek Efisiensi, dan Efek Harga.
--              Membuktikan secara matematis bahwa jumlah ketiga efek = total selisih.
-- ==============================================================================

WITH monthly_actuals AS (
    SELECT 
        TO_CHAR(p.date, 'YYYY-MM') AS month,
        p.project_code,
        SUM(p.overburden_bcm) AS actual_bcm,
        SUM(f.fuel_liter) AS actual_fuel_liter,
        SUM(f.fuel_liter * f.fuel_price_idr) AS actual_fuel_cost,
        SUM(f.fuel_liter) / NULLIF(SUM(p.overburden_bcm), 0) AS actual_fuel_ratio,
        SUM(f.fuel_liter * f.fuel_price_idr) / NULLIF(SUM(f.fuel_liter), 0) AS actual_fuel_price
    FROM fact_production p
    JOIN dim_equipment e ON p.project_code = e.project_code
    JOIN fact_fuel f ON p.date = f.date AND e.equipment_code = f.equipment_code
    GROUP BY TO_CHAR(p.date, 'YYYY-MM'), p.project_code
),
variance_calc AS (
    SELECT 
        b.month,
        b.project_code,
        pr.project_name,
        -- Volume
        a.actual_bcm,
        b.target_overburden_bcm AS budget_bcm,
        (a.actual_bcm - b.target_overburden_bcm) AS volume_diff_bcm,
        
        -- Fuel Ratio & Price
        a.actual_fuel_ratio,
        (b.budget_fuel_liter / b.target_overburden_bcm) AS budget_fuel_ratio,
        a.actual_fuel_price,
        b.budget_fuel_price_idr AS budget_fuel_price,
        
        -- Costs
        a.actual_fuel_cost,
        b.budget_fuel_cost_idr AS budget_fuel_cost,
        (a.actual_fuel_cost - b.budget_fuel_cost_idr) AS total_variance_cost,
        
        -- 1. Efek Volume = (Actual_BCM - Budget_BCM) * Budget_Ratio * Budget_Price
        ((a.actual_bcm - b.target_overburden_bcm) * 
         (b.budget_fuel_liter / b.target_overburden_bcm) * 
         b.budget_fuel_price_idr) AS volume_effect,
         
        -- 2. Efek Efisiensi = Actual_BCM * (Actual_Ratio - Budget_Ratio) * Budget_Price
        (a.actual_bcm * 
         (a.actual_fuel_ratio - (b.budget_fuel_liter / b.target_overburden_bcm)) * 
         b.budget_fuel_price_idr) AS efficiency_effect,
         
        -- 3. Efek Harga = Actual_BCM * Actual_Ratio * (Actual_Price - Budget_Price)
        (a.actual_bcm * 
         a.actual_fuel_ratio * 
         (a.actual_fuel_price - b.budget_fuel_price_idr)) AS price_effect
         
    FROM budget_monthly b
    JOIN dim_project pr ON b.project_code = pr.project_code
    JOIN monthly_actuals a ON b.month = a.month AND b.project_code = a.project_code
)
SELECT 
    month,
    project_code,
    project_name,
    ROUND(total_variance_cost, 0) AS total_variance_idr,
    ROUND(volume_effect, 0) AS volume_effect_idr,
    ROUND(efficiency_effect, 0) AS efficiency_effect_idr,
    ROUND(price_effect, 0) AS price_effect_idr,
    -- Verifikasi rekonsiliasi penjumlahan 3 efek = total varians
    ROUND((volume_effect + efficiency_effect + price_effect) - total_variance_cost, 4) AS decomposition_residual_diff,
    -- MoM Trend Varians menggunakan Window Function
    ROUND(total_variance_cost - LAG(total_variance_cost) OVER (PARTITION BY project_code ORDER BY month), 0) AS variance_mom_change_idr
FROM variance_calc
ORDER BY project_code, month;
