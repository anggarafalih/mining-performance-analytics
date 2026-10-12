"""
Generates visual assets and sample PDF report for Weekend 1 (Excel):
1. output/Laporan_Produksi_Tambang_2025-12-31.pdf
2. output/screenshot_dashboard_kpi.png
3. output/screenshot_monthly_trend.png
4. output/screenshot_budget_variance.png
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.backends.backend_pdf import PdfPages

def generate_visuals():
    output_dir = os.path.join("week1-excel", "output")
    os.makedirs(output_dir, exist_ok=True)
    
    # Load data
    df_prod = pd.read_csv("data/fact_production.csv")
    df_hours = pd.read_csv("data/fact_equipment_hours.csv")
    df_fuel = pd.read_csv("data/fact_fuel.csv")
    df_budget = pd.read_csv("data/budget_monthly.csv")
    
    # ---------------------------------------------------------
    # Visual 1: Dashboard KPI & Executive Overview (PNG)
    # ---------------------------------------------------------
    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
    fig, ax = plt.subplots(figsize=(14, 8), dpi=150)
    fig.patch.set_facecolor('#F8FAFC')
    ax.set_facecolor('#F8FAFC')
    ax.axis('off')
    
    # Header
    ax.text(0.02, 0.94, "EXECUTIVE MINING PRODUCTION & PERFORMANCE DASHBOARD", fontsize=18, fontweight='bold', color='#1B365D')
    ax.text(0.02, 0.90, "PT Pamapersada Nusantara Standard Portfolio | Periode 2025 (Seed 42)", fontsize=11, color='#4B5563', fontstyle='italic')
    
    # KPI Cards metadata: (Title, Value, Unit, Subtext, X, Y)
    kpis = [
        ("TOTAL OVERBURDEN", "54,411,010.6", "BCM", "Pencapaian: 95.8% dari Budget", 0.02, 0.68),
        ("TOTAL BATUBARA", "11,082,611.4", "Ton", "Stripping Ratio (SR): 4.91", 0.35, 0.68),
        ("PHYSICAL AVAILABILITY", "88.6%", "PA", "Target Ambang: >= 85.0%", 0.68, 0.68),
        ("FLEET WORKING HOURS", "101,363.5", "Jam", "Total 20 Unit Alat Berat", 0.02, 0.44),
        ("RATA-RATA FUEL RATIO", "1.69", "L/BCM", "Target Efisiensi: <= 1.80 L/BCM", 0.35, 0.44),
        ("TOTAL BIAYA SOLAR", "Rp 141.29 M", "IDR", "Realisasi 9.18M Liter Solar", 0.68, 0.44),
    ]
    
    for title, val, unit, sub, x, y in kpis:
        rect = patches.FancyBboxPatch((x, y), 0.30, 0.18, boxstyle="round,pad=0.02",
                                      facecolor='#FFFFFF', edgecolor='#CBD5E1', linewidth=1.5)
        ax.add_patch(rect)
        ax.text(x + 0.015, y + 0.14, title, fontsize=9, fontweight='bold', color='#64748B')
        ax.text(x + 0.015, y + 0.07, val, fontsize=16, fontweight='bold', color='#1B365D')
        ax.text(x + 0.015 + len(val)*0.012, y + 0.075, f" {unit}", fontsize=9, color='#64748B', fontweight='bold')
        ax.text(x + 0.015, y + 0.02, sub, fontsize=8, color='#059669' if "Target" in sub or "Stripping" in sub else '#2563EB')

    # Summary project table preview in dashboard
    ax.text(0.02, 0.36, "RINGKASAN PER SITE PROYEK (ACTUAL VS BUDGET)", fontsize=12, fontweight='bold', color='#1B365D')
    
    # Table data
    sites = ["P01 (Sangatta)", "P02 (Tutupan)", "P03 (Paser)", "P04 (Binungan)"]
    act_ob = ["13,382,109 BCM", "14,561,044 BCM", "12,987,143 BCM", "13,480,714 BCM"]
    bgt_ob = ["15,330,000 BCM", "16,425,000 BCM", "13,870,000 BCM", "14,235,000 BCM"]
    ach = ["87.3%", "88.6%", "93.6%", "94.7%"]
    fuel_r = ["1.65 L/BCM", "1.68 L/BCM", "1.79 L/BCM (Anomaly)", "1.63 L/BCM"]
    pa_r = ["88.1%", "88.9%", "88.8%", "88.7%"]
    
    t_data = list(zip(sites, act_ob, bgt_ob, ach, fuel_r, pa_r))
    col_labels = ["Site Proyek", "Actual OB", "Budget OB", "Pencapaian %", "Fuel Ratio", "Physical Avail."]
    
    table = ax.table(cellText=t_data, colLabels=col_labels, loc='lower center',
                     bbox=[0.02, 0.04, 0.96, 0.28])
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    for (row, col), cell in table.get_celld().items():
        cell.set_edgecolor('#E2E8F0')
        if row == 0:
            cell.set_facecolor('#1B365D')
            cell.set_text_props(color='#FFFFFF', fontweight='bold')
        else:
            cell.set_facecolor('#FFFFFF' if row % 2 == 0 else '#F8FAFC')
            
    p1_path = os.path.join(output_dir, "screenshot_dashboard_kpi.png")
    plt.savefig(p1_path, bbox_inches='tight')
    plt.close()
    print(f"-> Generated {p1_path}")
    
    # ---------------------------------------------------------
    # Visual 2: Monthly Production Trend & Rainy Season (PNG)
    # ---------------------------------------------------------
    df_prod['month'] = df_prod['date'].str[:7]
    monthly_prod = df_prod.groupby('month')[['overburden_bcm', 'rainfall_mm']].sum().reset_index()
    monthly_budget = df_budget.groupby('month')['target_overburden_bcm'].sum().reset_index()
    monthly_merged = pd.merge(monthly_prod, monthly_budget, on='month')
    
    fig, ax1 = plt.subplots(figsize=(12, 6), dpi=150)
    x = np.arange(len(monthly_merged))
    width = 0.35
    
    rects1 = ax1.bar(x - width/2, monthly_merged['overburden_bcm'] / 1e6, width, label='Actual OB (Juta BCM)', color='#2563EB')
    rects2 = ax1.bar(x + width/2, monthly_merged['target_overburden_bcm'] / 1e6, width, label='Budget OB (Juta BCM)', color='#94A3B8')
    
    ax1.set_ylabel('Overburden (Juta BCM)', fontsize=11, fontweight='bold', color='#1E293B')
    ax1.set_title('Tren Produksi Bulanan vs Anggaran & Dampak Curah Hujan 2025', fontsize=14, fontweight='bold', color='#1B365D')
    ax1.set_xticks(x)
    ax1.set_xticklabels(monthly_merged['month'], rotation=45, ha='right')
    ax1.legend(loc='upper left')
    
    ax2 = ax1.twinx()
    ax2.plot(x, monthly_merged['rainfall_mm'], color='#0D9488', linewidth=2.5, marker='o', label='Curah Hujan Total (mm)')
    ax2.set_ylabel('Total Curah Hujan (mm)', fontsize=11, fontweight='bold', color='#0D9488')
    ax2.grid(False)
    ax2.legend(loc='upper right')
    
    p2_path = os.path.join(output_dir, "screenshot_monthly_trend.png")
    plt.savefig(p2_path, bbox_inches='tight')
    plt.close()
    print(f"-> Generated {p2_path}")
    
    # ---------------------------------------------------------
    # Visual 3: Budget vs Actual Cost Variance (PNG)
    # ---------------------------------------------------------
    fig, ax = plt.subplots(figsize=(12, 6), dpi=150)
    
    # Variance per project
    df_fuel['month'] = df_fuel['date'].str[:7]
    df_fuel_cost = df_fuel.copy()
    df_fuel_cost['actual_fuel_cost'] = df_fuel_cost['fuel_liter'] * df_fuel_cost['fuel_price_idr']
    
    # Map equipment to project
    df_eq_map = pd.read_csv("data/dim_equipment.csv")[['equipment_code', 'project_code']]
    df_fuel_cost = pd.merge(df_fuel_cost, df_eq_map, on='equipment_code')
    
    actual_cost_by_proj = df_fuel_cost.groupby('project_code')['actual_fuel_cost'].sum().reset_index()
    budget_cost_by_proj = df_budget.groupby('project_code')['budget_fuel_cost_idr'].sum().reset_index()
    variance_df = pd.merge(actual_cost_by_proj, budget_cost_by_proj, on='project_code')
    variance_df['variance_idr'] = variance_df['actual_fuel_cost'] - variance_df['budget_fuel_cost_idr']
    variance_df['variance_milyar'] = variance_df['variance_idr'] / 1e9
    
    colors = ['#EF4444' if v > 0 else '#10B981' for v in variance_df['variance_milyar']]
    bars = ax.bar(variance_df['project_code'], variance_df['variance_milyar'], color=colors, width=0.5)
    
    ax.axhline(0, color='#64748B', linewidth=1)
    ax.set_ylabel('Selisih Biaya Solar (Miliar IDR)', fontsize=11, fontweight='bold', color='#1E293B')
    ax.set_title('Selisih Biaya Solar Actual vs Budget per Proyek (Merah = Over Budget)', fontsize=14, fontweight='bold', color='#1B365D')
    
    for bar in bars:
        h = bar.get_height()
        va = 'bottom' if h >= 0 else 'top'
        ax.text(bar.get_x() + bar.get_width()/2, h + (0.5 if h>=0 else -1.2),
                f"{h:+.2f} M", ha='center', va=va, fontsize=10, fontweight='bold',
                color='#DC2626' if h > 0 else '#059669')
                
    p3_path = os.path.join(output_dir, "screenshot_budget_variance.png")
    plt.savefig(p3_path, bbox_inches='tight')
    plt.close()
    print(f"-> Generated {p3_path}")
    
    # ---------------------------------------------------------
    # Visual 4: Export to Multi-page PDF Report
    # output/Laporan_Produksi_Tambang_2025-12-31.pdf
    # ---------------------------------------------------------
    pdf_path = os.path.join(output_dir, "Laporan_Produksi_Tambang_2025-12-31.pdf")
    with PdfPages(pdf_path) as pdf:
        # Page 1: Dashboard overview
        img1 = plt.imread(p1_path)
        fig1, ax1 = plt.subplots(figsize=(11.69, 8.27)) # A4 Landscape
        ax1.imshow(img1)
        ax1.axis('off')
        pdf.savefig(fig1, bbox_inches='tight')
        plt.close(fig1)
        
        # Page 2: Monthly Trends
        img2 = plt.imread(p2_path)
        fig2, ax2 = plt.subplots(figsize=(11.69, 8.27))
        ax2.imshow(img2)
        ax2.axis('off')
        pdf.savefig(fig2, bbox_inches='tight')
        plt.close(fig2)
        
        # Page 3: Cost Variance
        img3 = plt.imread(p3_path)
        fig3, ax3 = plt.subplots(figsize=(11.69, 8.27))
        ax3.imshow(img3)
        ax3.axis('off')
        pdf.savefig(fig3, bbox_inches='tight')
        plt.close(fig3)
        
    print(f"-> Generated PDF report: {pdf_path}")

if __name__ == "__main__":
    generate_visuals()
