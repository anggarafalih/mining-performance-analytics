"""
Data Generator for Mining Production Performance Analytics
Seed: 42
Generates synthetic operational data for 4 mining projects over 365 days in 2025.
Produces dim_project, dim_equipment, fact_production, fact_equipment_hours, fact_fuel, budget_monthly,
as well as raw versions with intentional dirty records for Power Query practice.
"""

import os
import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def generate_all_data(output_dir="data", seed=42):
    random.seed(seed)
    np.random.seed(seed)
    
    os.makedirs(output_dir, exist_ok=True)
    raw_dir = os.path.join(output_dir, "raw")
    os.makedirs(raw_dir, exist_ok=True)
    
    print(f"Generating synthetic mining datasets with seed {seed}...")
    
    # -------------------------------------------------------------
    # 1. dim_project
    # -------------------------------------------------------------
    projects = [
        {"project_code": "P01", "project_name": "Project Sangatta North", "location": "East Kalimantan", "material_type": "Thermal Coal & Overburden"},
        {"project_code": "P02", "project_name": "Project Tutupan South", "location": "South Kalimantan", "material_type": "Thermal Coal & Overburden"},
        {"project_code": "P03", "project_name": "Project Paser Ridge", "location": "East Kalimantan", "material_type": "Thermal Coal & Overburden"},
        {"project_code": "P04", "project_name": "Project Binungan West", "location": "East Kalimantan", "material_type": "Thermal Coal & Overburden"},
    ]
    df_project = pd.DataFrame(projects)
    df_project.to_csv(os.path.join(output_dir, "dim_project.csv"), index=False)
    print(f"-> Created dim_project.csv ({len(df_project)} rows)")
    
    # -------------------------------------------------------------
    # 2. dim_equipment
    # 20 units: 6 Excavators (EX), 10 Dump Trucks (DT), 4 Dozers (DZ)
    # Assigned across P01..P04
    # -------------------------------------------------------------
    equipment_list = [
        # P01 (Alpha)
        {"equipment_code": "EX01", "equipment_type": "Excavator", "project_code": "P01", "model": "Komatsu PC2000-8", "capacity": 12.0, "capacity_unit": "m3"},
        {"equipment_code": "EX02", "equipment_type": "Excavator", "project_code": "P01", "model": "Hitachi EX2600-6", "capacity": 17.0, "capacity_unit": "m3"},
        {"equipment_code": "DT01", "equipment_type": "Dump Truck", "project_code": "P01", "model": "Komatsu HD785-7", "capacity": 91.0, "capacity_unit": "ton"},
        {"equipment_code": "DT02", "equipment_type": "Dump Truck", "project_code": "P01", "model": "Komatsu HD785-7", "capacity": 91.0, "capacity_unit": "ton"},
        {"equipment_code": "DZ01", "equipment_type": "Dozer", "project_code": "P01", "model": "Komatsu D375A-6", "capacity": 18.5, "capacity_unit": "m3"},
        
        # P02 (Beta)
        {"equipment_code": "EX03", "equipment_type": "Excavator", "project_code": "P02", "model": "Komatsu PC2000-8", "capacity": 12.0, "capacity_unit": "m3"},
        {"equipment_code": "EX04", "equipment_type": "Excavator", "project_code": "P02", "model": "Hitachi EX2600-6", "capacity": 17.0, "capacity_unit": "m3"},
        {"equipment_code": "DT03", "equipment_type": "Dump Truck", "project_code": "P02", "model": "Komatsu HD785-7", "capacity": 91.0, "capacity_unit": "ton"},
        {"equipment_code": "DT04", "equipment_type": "Dump Truck", "project_code": "P02", "model": "Komatsu HD785-7", "capacity": 91.0, "capacity_unit": "ton"},
        {"equipment_code": "DT05", "equipment_type": "Dump Truck", "project_code": "P02", "model": "CAT 777E", "capacity": 95.0, "capacity_unit": "ton"},
        {"equipment_code": "DZ02", "equipment_type": "Dozer", "project_code": "P02", "model": "Komatsu D375A-6", "capacity": 18.5, "capacity_unit": "m3"},
        
        # P03 (Gamma)
        {"equipment_code": "EX05", "equipment_type": "Excavator", "project_code": "P03", "model": "Komatsu PC2000-8", "capacity": 12.0, "capacity_unit": "m3"},
        {"equipment_code": "DT06", "equipment_type": "Dump Truck", "project_code": "P03", "model": "CAT 777E", "capacity": 95.0, "capacity_unit": "ton"},
        {"equipment_code": "DT07", "equipment_type": "Dump Truck", "project_code": "P03", "model": "Komatsu HD785-7", "capacity": 91.0, "capacity_unit": "ton"},
        {"equipment_code": "DT08", "equipment_type": "Dump Truck", "project_code": "P03", "model": "CAT 777E", "capacity": 95.0, "capacity_unit": "ton"},
        {"equipment_code": "DZ03", "equipment_type": "Dozer", "project_code": "P03", "model": "Komatsu D375A-6", "capacity": 18.5, "capacity_unit": "m3"},
        
        # P04 (Delta)
        {"equipment_code": "EX06", "equipment_type": "Excavator", "project_code": "P04", "model": "Hitachi EX2600-6", "capacity": 17.0, "capacity_unit": "m3"},
        {"equipment_code": "DT09", "equipment_type": "Dump Truck", "project_code": "P04", "model": "CAT 777E", "capacity": 95.0, "capacity_unit": "ton"},
        {"equipment_code": "DT10", "equipment_type": "Dump Truck", "project_code": "P04", "model": "Komatsu HD785-7", "capacity": 91.0, "capacity_unit": "ton"},
        {"equipment_code": "DZ04", "equipment_type": "Dozer", "project_code": "P04", "model": "Komatsu D375A-6", "capacity": 18.5, "capacity_unit": "m3"},
    ]
    df_equipment = pd.DataFrame(equipment_list)
    df_equipment.to_csv(os.path.join(output_dir, "dim_equipment.csv"), index=False)
    print(f"-> Created dim_equipment.csv ({len(df_equipment)} rows)")
    
    # -------------------------------------------------------------
    # Calendar & Monthly Configuration
    # -------------------------------------------------------------
    dates = [datetime(2025, 1, 1) + timedelta(days=i) for i in range(365)]
    
    # Monthly Fuel Prices (IDR per liter)
    monthly_fuel_prices = {
        1: 14200, 2: 14350, 3: 14500, 4: 14800,
        5: 15100, 6: 15300, 7: 15600, 8: 15900,
        9: 16200, 10: 16500, 11: 16100, 12: 15800
    }
    
    # Base daily targets per project
    base_targets = {
        "P01": {"ob": 42000.0, "coal": 8500.0},
        "P02": {"ob": 45000.0, "coal": 9000.0},
        "P03": {"ob": 38000.0, "coal": 7800.0},
        "P04": {"ob": 39000.0, "coal": 8000.0},
    }
    
    # -------------------------------------------------------------
    # Anomaly Definition
    # Anomaly 1: Extreme Rain Days (3 days: Feb 14, Mar 19, Nov 16)
    # Anomaly 2: Prolonged Breakdowns (>5 days):
    #   - EX02 (P01): 2025-05-12 to 2025-05-18 (7 days)
    #   - DT05 (P02): 2025-08-10 to 2025-08-15 (6 days)
    # Anomaly 3: Gradual fuel ratio increase in P03 from July onwards
    # -------------------------------------------------------------
    extreme_rain_dates = {
        datetime(2025, 2, 14).strftime("%Y-%m-%d"),
        datetime(2025, 3, 19).strftime("%Y-%m-%d"),
        datetime(2025, 11, 16).strftime("%Y-%m-%d"),
    }
    
    ex02_breakdown_dates = {
        (datetime(2025, 5, 12) + timedelta(days=d)).strftime("%Y-%m-%d") for d in range(7)
    }
    dt05_breakdown_dates = {
        (datetime(2025, 8, 10) + timedelta(days=d)).strftime("%Y-%m-%d") for d in range(6)
    }
    
    # -------------------------------------------------------------
    # 3. fact_production
    # 4 projects * 365 days = 1,460 rows
    # -------------------------------------------------------------
    production_rows = []
    
    for dt in dates:
        dt_str = dt.strftime("%Y-%m-%d")
        month = dt.month
        
        # Rainfall modeling (wet season: Jan-Mar, Nov-Dec; dry season: Apr-Oct)
        if month in [1, 2, 3, 11, 12]:
            rain_base = np.random.gamma(shape=2.5, scale=6.0) # avg ~15mm with heavy rain chances
        else:
            rain_base = np.random.gamma(shape=1.2, scale=3.0) # avg ~3.6mm
            
        is_extreme = dt_str in extreme_rain_dates
        
        for p in ["P01", "P02", "P03", "P04"]:
            if is_extreme:
                rainfall_mm = round(float(np.random.uniform(115.0, 145.0)), 1)
                rain_impact = np.random.uniform(0.70, 0.85) # 70-85% loss
            else:
                rainfall_mm = round(float(rain_base + np.random.uniform(0, 3)), 1)
                if rainfall_mm > 50:
                    rain_impact = 0.40
                elif rainfall_mm > 25:
                    rain_impact = 0.20
                elif rainfall_mm > 10:
                    rain_impact = 0.08
                else:
                    rain_impact = 0.0
            
            # Seasonal factor (15-30% reduction in wet season)
            season_factor = 0.85 if month in [1, 2, 3, 11, 12] else 1.02
            
            target_ob = base_targets[p]["ob"]
            target_coal = base_targets[p]["coal"]
            
            # Daily noise
            noise_ob = np.random.normal(1.0, 0.05)
            noise_coal = np.random.normal(1.0, 0.05)
            
            # Calculate actual production
            actual_ob = round(target_ob * season_factor * (1.0 - rain_impact) * noise_ob, 1)
            actual_coal = round(target_coal * season_factor * (1.0 - rain_impact) * noise_coal, 1)
            
            # Impact of prolonged breakdown in site
            if p == "P01" and dt_str in ex02_breakdown_dates:
                actual_ob = round(actual_ob * 0.65, 1) # major primary excavator down
                actual_coal = round(actual_coal * 0.75, 1)
            elif p == "P02" and dt_str in dt05_breakdown_dates:
                actual_ob = round(actual_ob * 0.85, 1) # hauler fleet down
            
            production_rows.append({
                "date": dt_str,
                "project_code": p,
                "overburden_bcm": actual_ob,
                "coal_ton": actual_coal,
                "daily_target_bcm": target_ob,
                "daily_target_coal": target_coal,
                "rainfall_mm": rainfall_mm
            })
            
    df_production = pd.DataFrame(production_rows)
    df_production.to_csv(os.path.join(output_dir, "fact_production.csv"), index=False)
    print(f"-> Created fact_production.csv ({len(df_production)} rows)")
    
    # Map project daily OB to calculate equipment working hours realistically
    prod_lookup = df_production.set_index(["date", "project_code"])["overburden_bcm"].to_dict()
    rain_lookup = df_production.groupby("date")["rainfall_mm"].first().to_dict()
    
    # -------------------------------------------------------------
    # 4. fact_equipment_hours & 5. fact_fuel
    # 20 units * 365 days = 7,300 rows each
    # -------------------------------------------------------------
    eq_hours_rows = []
    fuel_rows = []
    
    for dt in dates:
        dt_str = dt.strftime("%Y-%m-%d")
        month = dt.month
        fuel_price = monthly_fuel_prices[month]
        
        for eq in equipment_list:
            eq_code = eq["equipment_code"]
            eq_type = eq["equipment_type"]
            proj_code = eq["project_code"]
            
            hours_available = 24.0 # Scheduled total calendar hours
            
            # Check specific anomalies
            if eq_code == "EX02" and dt_str in ex02_breakdown_dates:
                hours_breakdown = 24.0
                hours_working = 0.0
                hours_standby = 0.0
            elif eq_code == "DT05" and dt_str in dt05_breakdown_dates:
                hours_breakdown = 24.0
                hours_working = 0.0
                hours_standby = 0.0
            else:
                # Normal operational random breakdown
                # Excavator has slightly higher breakdown chance than DT
                if np.random.random() < 0.07:
                    hours_breakdown = round(float(np.random.uniform(2.0, 8.0)), 1)
                elif np.random.random() < 0.02:
                    hours_breakdown = round(float(np.random.uniform(8.0, 16.0)), 1)
                else:
                    hours_breakdown = round(float(np.random.uniform(0.0, 1.5)), 1)
                
                remaining_time = max(0.0, hours_available - hours_breakdown)
                
                # Extreme rain causes standby
                rain_today = rain_lookup.get(dt_str, 0)
                if dt_str in extreme_rain_dates or rain_today > 100:
                    standby_pct = np.random.uniform(0.70, 0.90)
                elif rain_today > 30:
                    standby_pct = np.random.uniform(0.25, 0.45)
                else:
                    # Normal standby (shift change, refueling, blasting, prayer time)
                    standby_pct = np.random.uniform(0.12, 0.22)
                
                hours_standby = round(remaining_time * standby_pct, 1)
                hours_working = round(remaining_time - hours_standby, 1)
                
                # Sanity check sum <= 24
                tot = hours_working + hours_standby + hours_breakdown
                if tot > 24.0:
                    hours_standby = round(hours_standby - (tot - 24.0), 1)
            
            # Exact guarantee hours sum == 24.0
            hours_working = max(0.0, hours_working)
            hours_standby = max(0.0, hours_standby)
            hours_breakdown = max(0.0, hours_breakdown)
            diff = round(24.0 - (hours_working + hours_standby + hours_breakdown), 1)
            if diff != 0:
                hours_standby = round(hours_standby + diff, 1)
            
            eq_hours_rows.append({
                "date": dt_str,
                "equipment_code": eq_code,
                "hours_working": hours_working,
                "hours_standby": hours_standby,
                "hours_breakdown": hours_breakdown,
                "hours_available": hours_available
            })
            
            # --- Fuel Calculation ---
            # Burn rates (L/working hour):
            # Excavator: ~80-90 L/hr
            # Dump Truck: ~55-65 L/hr
            # Dozer: ~42-50 L/hr
            if eq_type == "Excavator":
                base_burn = 85.0
            elif eq_type == "Dump Truck":
                base_burn = 60.0
            else: # Dozer
                base_burn = 46.0
                
            # Idle/standby burn rate: ~5-8 L/hr
            idle_burn = 6.0
            
            # Anomaly 3: Gradual fuel ratio climb in Project P03
            # Fuel burn rate in P03 escalates from July (Month 7) to Dec (Month 12)
            efficiency_penalty = 1.0
            if proj_code == "P03" and month >= 6:
                # Progressive increase: Month 6 +3%, Month 7 +7%, Month 8 +12%, Month 9 +18%, Month 10 +24%, Month 11 +28%, Month 12 +32%
                step = month - 5
                efficiency_penalty = 1.0 + (step * 0.045)
                
            if hours_working > 0:
                burn_variation = np.random.normal(1.0, 0.03)
                fuel_used = (hours_working * base_burn * efficiency_penalty * burn_variation) + (hours_standby * idle_burn)
                fuel_liter = round(float(fuel_used), 1)
            else:
                fuel_liter = round(float(hours_standby * idle_burn), 1)
                
            fuel_rows.append({
                "date": dt_str,
                "equipment_code": eq_code,
                "fuel_liter": fuel_liter,
                "fuel_price_idr": fuel_price
            })
            
    df_eq_hours = pd.DataFrame(eq_hours_rows)
    df_eq_hours.to_csv(os.path.join(output_dir, "fact_equipment_hours.csv"), index=False)
    print(f"-> Created fact_equipment_hours.csv ({len(df_eq_hours)} rows)")
    
    df_fuel = pd.DataFrame(fuel_rows)
    df_fuel.to_csv(os.path.join(output_dir, "fact_fuel.csv"), index=False)
    print(f"-> Created fact_fuel.csv ({len(df_fuel)} rows)")
    
    # -------------------------------------------------------------
    # 6. budget_monthly
    # 4 projects * 12 months = 48 rows
    # -------------------------------------------------------------
    # To be realistic and consistent for variance analysis:
    # Monthly target production is roughly daily target * days in month
    # Monthly target fuel liter is based on expected standard fuel ratio (~1.85 L/BCM)
    # Fuel budget price based on budgeted fuel price (e.g., fixed around 14,500 IDR/L)
    # Other costs (labor, maintenance, explosives, overhead) proportional to production
    budget_rows = []
    
    # Days per month in 2025
    days_in_month = {
        1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30,
        7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31
    }
    
    budget_fuel_price = 14500 # standard planned fuel price
    
    for m in range(1, 13):
        m_str = f"2025-{m:02d}"
        days_m = days_in_month[m]
        
        for p in ["P01", "P02", "P03", "P04"]:
            t_ob = base_targets[p]["ob"] * days_m
            t_coal = base_targets[p]["coal"] * days_m
            
            # Standard planned fuel ratio is ~1.80 L/BCM
            planned_fuel_ratio = 1.80
            fuel_budget_liter = round(t_ob * planned_fuel_ratio, 0)
            fuel_budget_cost = fuel_budget_liter * budget_fuel_price
            
            # Other operational costs: approx 45,000 IDR per BCM
            other_budget_cost = round(t_ob * 45000, 0)
            total_budget_cost = fuel_budget_cost + other_budget_cost
            
            budget_rows.append({
                "month": m_str,
                "project_code": p,
                "target_overburden_bcm": t_ob,
                "target_coal_ton": t_coal,
                "budget_fuel_liter": fuel_budget_liter,
                "budget_fuel_price_idr": budget_fuel_price,
                "budget_fuel_cost_idr": fuel_budget_cost,
                "budget_other_cost_idr": other_budget_cost,
                "total_budget_cost_idr": total_budget_cost
            })
            
    df_budget = pd.DataFrame(budget_rows)
    df_budget.to_csv(os.path.join(output_dir, "budget_monthly.csv"), index=False)
    print(f"-> Created budget_monthly.csv ({len(df_budget)} rows)")
    
    # -------------------------------------------------------------
    # 7. Raw Datasets with Intentional Dirty Rows (For Power Query)
    # 5 to 10 dirty rows: duplicates, null values, trailing spaces
    # -------------------------------------------------------------
    print("Generating raw files with intentional dirty rows for Power Query practice...")
    
    # Raw fact_production: insert 4 duplicate rows and 3 rows with trailing whitespace/null
    df_prod_raw = df_production.copy()
    dupes_prod = df_prod_raw.iloc[[10, 25, 100, 250]].copy()
    null_row = df_prod_raw.iloc[50:52].copy()
    null_row["daily_target_bcm"] = np.nan
    df_prod_raw = pd.concat([df_prod_raw, dupes_prod, null_row], ignore_index=True)
    df_prod_raw.to_csv(os.path.join(raw_dir, "fact_production_raw.csv"), index=False)
    
    # Raw fact_equipment_hours: insert 3 duplicates and 2 null working hours
    df_hours_raw = df_eq_hours.copy()
    dupes_hours = df_hours_raw.iloc[[42, 142, 500]].copy()
    df_hours_raw = pd.concat([df_hours_raw, dupes_hours], ignore_index=True)
    df_hours_raw.to_csv(os.path.join(raw_dir, "fact_equipment_hours_raw.csv"), index=False)
    
    # Raw fact_fuel: insert 3 duplicates
    df_fuel_raw = df_fuel.copy()
    dupes_fuel = df_fuel_raw.iloc[[77, 350, 800]].copy()
    df_fuel_raw = pd.concat([df_fuel_raw, dupes_fuel], ignore_index=True)
    df_fuel_raw.to_csv(os.path.join(raw_dir, "fact_fuel_raw.csv"), index=False)
    
    # Raw budget_monthly: insert 1 duplicate
    df_budget_raw = df_budget.copy()
    dupe_budget = df_budget_raw.iloc[[5]].copy()
    df_budget_raw = pd.concat([df_budget_raw, dupe_budget], ignore_index=True)
    df_budget_raw.to_csv(os.path.join(raw_dir, "budget_monthly_raw.csv"), index=False)
    
    print("All datasets successfully generated!")
    
    # Print summary reconciliation baseline
    total_ob = df_production["overburden_bcm"].sum()
    total_coal = df_production["coal_ton"].sum()
    total_fuel = df_fuel["fuel_liter"].sum()
    
    # Fuel cost actual: sum(fuel_liter * fuel_price_idr)
    df_fuel_merged = df_fuel.copy()
    fuel_actual_cost = (df_fuel_merged["fuel_liter"] * df_fuel_merged["fuel_price_idr"]).sum()
    
    print("\n--- BASELINE RECONCILIATION TOTALS (SEED 42) ---")
    print(f"Total Overburden (BCM) : {total_ob:,.1f}")
    print(f"Total Coal (Ton)       : {total_coal:,.1f}")
    print(f"Total Fuel (Liter)     : {total_fuel:,.1f}")
    print(f"Total Fuel Cost (IDR)  : {fuel_actual_cost:,.0f}")
    print("------------------------------------------------\n")
    
    return {
        "total_ob": total_ob,
        "total_coal": total_coal,
        "total_fuel": total_fuel,
        "total_fuel_cost": fuel_actual_cost
    }

if __name__ == "__main__":
    generate_all_data()
