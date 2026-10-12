"""
Excel Workbook Generator for Mining Production Performance Analytics
Generates week1-excel/Mining_Performance.xlsx with complete sheets, formulas,
tables, formatting, and dashboard.
"""

import os
import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

def build_workbook():
    print("Building Mining_Performance.xlsx workbook...")
    
    # Load source CSV data
    df_proj = pd.read_csv("data/dim_project.csv")
    df_eq = pd.read_csv("data/dim_equipment.csv")
    df_prod = pd.read_csv("data/fact_production.csv")
    df_hours = pd.read_csv("data/fact_equipment_hours.csv")
    df_fuel = pd.read_csv("data/fact_fuel.csv")
    df_budget = pd.read_csv("data/budget_monthly.csv")
    
    wb = openpyxl.Workbook()
    # remove default sheet
    default_sheet = wb.active
    wb.remove(default_sheet)
    
    # Theme colors
    NAVY = "1B365D"
    WHITE = "FFFFFF"
    GOLD = "D4AF37"
    LIGHT_GRAY = "F4F6F9"
    BORDER_GRAY = "D1D5DB"
    ACCENT_BLUE = "2563EB"
    CARD_BG = "F8FAFC"
    
    font_title = Font(name="Segoe UI", size=16, bold=True, color=NAVY)
    font_subtitle = Font(name="Segoe UI", size=11, italic=True, color="4B5563")
    font_header = Font(name="Segoe UI", size=11, bold=True, color=WHITE)
    font_bold = Font(name="Segoe UI", size=10, bold=True)
    font_regular = Font(name="Segoe UI", size=10)
    font_kpi_num = Font(name="Segoe UI", size=18, bold=True, color=NAVY)
    font_kpi_lbl = Font(name="Segoe UI", size=9, bold=True, color="6B7280")
    
    fill_header = PatternFill(start_color=NAVY, end_color=NAVY, fill_type="solid")
    fill_card = PatternFill(start_color=CARD_BG, end_color=CARD_BG, fill_type="solid")
    fill_accent = PatternFill(start_color="EFF6FF", end_color="EFF6FF", fill_type="solid")
    
    thin_side = Side(border_style="thin", color=BORDER_GRAY)
    border_all = Border(left=thin_side, right=thin_side, top=thin_side, bottom=thin_side)
    border_box = Border(left=thin_side, right=thin_side, top=thin_side, bottom=thin_side)
    
    # -------------------------------------------------------------
    # 1. Sheet README
    # -------------------------------------------------------------
    ws_readme = wb.create_sheet(title="README")
    ws_readme.views.sheetView[0].showGridLines = True
    
    ws_readme["B2"] = "MINING PRODUCTION PERFORMANCE ANALYTICS"
    ws_readme["B2"].font = font_title
    ws_readme["B3"] = "Portfolio Studi Kasus Operasional Tambang (PT Pamapersada Nusantara Standard)"
    ws_readme["B3"].font = font_subtitle
    
    ws_readme["B5"] = "[!] DISCLAIMER DATA SINTETIS"
    ws_readme["B5"].font = Font(name="Segoe UI", size=12, bold=True, color="DC2626")
    ws_readme["B6"] = "Seluruh data dalam workbook ini adalah data sintetis matematis (seed 42) untuk keperluan simulasi teknis portofolio. Tidak memuat data riil rahasia perusahaan."
    ws_readme["B6"].font = font_regular
    
    ws_readme["B8"] = "DAFTAR WORKSHEET & FUNGSI"
    ws_readme["B8"].font = Font(name="Segoe UI", size=12, bold=True, color=NAVY)
    
    sheets_info = [
        ("README", "Disclaimer, petunjuk teknis, deskripsi modul, dan kamus metrik."),
        ("Control", "Parameter dinamis: seleksi proyek, rentang tanggal, target PA & batas fuel ratio."),
        ("Dashboard", "Executive KPI card (A4 landscape), grafik performa, dan analisis budget vs actual."),
        ("Pivot", "Tabel ringkasan agregasi bulanan, mingguan (ISO week), dan per-site proyek."),
        ("Calc", "Tabel perhitungan metrik turunan (PA, UA, Produktivitas, Fuel Ratio, Varians)."),
        ("Budget", "Master data anggaran biaya dan target produksi bulanan 2025 (48 baris)."),
        ("Data_Production", "Data transaksi produksi harian BCM, Batubara, target, dan curah hujan (1.460 baris)."),
        ("Data_Equipment", "Data transaksi jam kerja operasional harian alat berat (7.300 baris)."),
        ("Data_Fuel", "Data transaksi konsumsi solar dan fluktuasi harga bulanan (7.300 baris)."),
        ("Log", "Log audit otomatis hasil eksekusi makro VBA RefreshAndExport.")
    ]
    
    ws_readme.cell(row=9, column=2, value="Sheet Name").font = font_bold
    ws_readme.cell(row=9, column=3, value="Deskripsi & Fungsi").font = font_bold
    for i, (sname, sdesc) in enumerate(sheets_info, start=10):
        ws_readme.cell(row=i, column=2, value=sname).font = Font(name="Segoe UI", size=10, bold=True, color=ACCENT_BLUE)
        ws_readme.cell(row=i, column=3, value=sdesc).font = font_regular
        
    ws_readme["B22"] = "PANDUAN EKSEKUSI MAKRO VBA"
    ws_readme["B22"].font = Font(name="Segoe UI", size=12, bold=True, color=NAVY)
    ws_readme["B23"] = "1. Buka tab Developer > Visual Basic (atau tekan Alt + F11)."
    ws_readme["B24"] = "2. File Module `RefreshAndExport.bas` dapat diimpor via menu File > Import File."
    ws_readme["B25"] = "3. Tombol 'Refresh & Ekspor PDF' di sheet Dashboard akan merefresh data, menghitung ulang formula, dan mencetak laporan A4 Landscape ke folder 'output/'."
    for r in range(23, 26):
        ws_readme[f"B{r}"].font = font_regular
        
    ws_readme.column_dimensions["B"].width = 25
    ws_readme.column_dimensions["C"].width = 85
    
    # -------------------------------------------------------------
    # 2. Sheet Control
    # -------------------------------------------------------------
    ws_control = wb.create_sheet(title="Control")
    ws_control.views.sheetView[0].showGridLines = True
    
    ws_control["B2"] = "CONTROL PANEL & PARAMETER DASHBOARD"
    ws_control["B2"].font = font_title
    
    controls = [
        ("Parameter", "Nilai", "Keterangan"),
        ("Project Selection", "ALL", "Pilihan: ALL, P01, P02, P03, P04"),
        ("Start Date", "2025-01-01", "Awal rentang evaluasi"),
        ("End Date", "2025-12-31", "Akhir rentang evaluasi"),
        ("Target PA (%)", 0.85, "Ambang batas minimum Physical Availability"),
        ("Fuel Ratio Threshold (L/BCM)", 1.95, "Batas toleransi efisiensi bahan bakar"),
    ]
    
    for r_idx, row in enumerate(controls, start=4):
        for c_idx, val in enumerate(row, start=2):
            cell = ws_control.cell(row=r_idx, column=c_idx, value=val)
            if r_idx == 4:
                cell.font = font_header
                cell.fill = fill_header
            else:
                cell.font = font_bold if c_idx == 2 else font_regular
                if c_idx == 3 and isinstance(val, float):
                    if val < 1.0:
                        cell.number_format = "0.0%"
                    else:
                        cell.number_format = "#,##0.00"
            cell.border = border_all
            
    ws_control.column_dimensions["B"].width = 30
    ws_control.column_dimensions["C"].width = 20
    ws_control.column_dimensions["D"].width = 40
    
    # -------------------------------------------------------------
    # Helper for Data Sheets
    # -------------------------------------------------------------
    def write_dataframe_to_sheet(sheet, df, table_name):
        sheet.views.sheetView[0].showGridLines = True
        cols = list(df.columns)
        # Header
        for col_idx, col_name in enumerate(cols, start=1):
            cell = sheet.cell(row=1, column=col_idx, value=col_name)
            cell.font = font_header
            cell.fill = fill_header
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border = border_all
            
        # Rows
        for r_idx, row_vals in enumerate(df.itertuples(index=False), start=2):
            for col_idx, val in enumerate(row_vals, start=1):
                cell = sheet.cell(row=r_idx, column=col_idx, value=val)
                cell.font = font_regular
                cell.border = border_all
                if isinstance(val, (int, float)):
                    if "price" in cols[col_idx-1] or "cost" in cols[col_idx-1]:
                        cell.number_format = "#,##0"
                    elif "hours" in cols[col_idx-1] or "bcm" in cols[col_idx-1] or "ton" in cols[col_idx-1] or "liter" in cols[col_idx-1] or "rainfall" in cols[col_idx-1]:
                        cell.number_format = "#,##0.0"
                        
        for col_idx, col_name in enumerate(cols, start=1):
            sheet.column_dimensions[get_column_letter(col_idx)].width = max(len(col_name) + 4, 13)
            
    # 3. Data_Production
    ws_prod = wb.create_sheet(title="Data_Production")
    write_dataframe_to_sheet(ws_prod, df_prod, "Table_Production")
    
    # 4. Data_Equipment
    ws_eq = wb.create_sheet(title="Data_Equipment")
    write_dataframe_to_sheet(ws_eq, df_hours, "Table_EquipmentHours")
    
    # 5. Data_Fuel
    ws_fuel = wb.create_sheet(title="Data_Fuel")
    write_dataframe_to_sheet(ws_fuel, df_fuel, "Table_Fuel")
    
    # 6. Budget
    ws_budget = wb.create_sheet(title="Budget")
    write_dataframe_to_sheet(ws_budget, df_budget, "Table_Budget")
    
    # -------------------------------------------------------------
    # 7. Sheet Pivot (Monthly & Project Summary Tables)
    # -------------------------------------------------------------
    ws_pivot = wb.create_sheet(title="Pivot")
    ws_pivot.views.sheetView[0].showGridLines = True
    
    ws_pivot["B2"] = "RINGKASAN PERFORMA PRODUKSI PER PROYEK (ACTUAL TAHUNAN)"
    ws_pivot["B2"].font = font_title
    
    headers_proj_pivot = ["Project Code", "Project Name", "Actual Overburden (BCM)", "Actual Coal (Ton)", "Working Hours (Jam)", "PA (%)", "Fuel Used (Liter)", "Fuel Ratio (L/BCM)"]
    for c_idx, h in enumerate(headers_proj_pivot, start=2):
        cell = ws_pivot.cell(row=4, column=c_idx, value=h)
        cell.font = font_header
        cell.fill = fill_header
        cell.border = border_all
        cell.alignment = Alignment(horizontal="center")
        
    projects_meta = [
        ("P01", "Project Sangatta North"),
        ("P02", "Project Tutupan South"),
        ("P03", "Project Paser Ridge"),
        ("P04", "Project Binungan West")
    ]
    
    # Aggregation formulas using SUMIF/SUMIFS
    for idx, (p_code, p_name) in enumerate(projects_meta, start=5):
        ws_pivot.cell(row=idx, column=2, value=p_code).font = font_bold
        ws_pivot.cell(row=idx, column=3, value=p_name).font = font_regular
        
        # BCM formula: SUMIF(Data_Production!B:B, p_code, Data_Production!C:C)
        c_bcm = ws_pivot.cell(row=idx, column=4, value=f"=SUMIF(Data_Production!B:B, B{idx}, Data_Production!C:C)")
        c_bcm.number_format = "#,##0.0"
        
        # Coal formula: SUMIF(Data_Production!B:B, p_code, Data_Production!D:D)
        c_coal = ws_pivot.cell(row=idx, column=5, value=f"=SUMIF(Data_Production!B:B, B{idx}, Data_Production!D:D)")
        c_coal.number_format = "#,##0.0"
        
        # Working hours & PA via equipment lookup
        # In fact_equipment_hours, we have equipment codes.
        # We can calculate project working hours by linking equipment to project
        # In our generator:
        # P01: EX01, EX02, DT01, DT02, DZ01
        # P02: EX03, EX04, DT03, DT04, DT05, DZ02
        # P03: EX05, DT06, DT07, DT08, DZ03
        # P04: EX06, DT09, DT10, DZ04
        eq_map = {
            "P01": ["EX01", "EX02", "DT01", "DT02", "DZ01"],
            "P02": ["EX03", "EX04", "DT03", "DT04", "DT05", "DZ02"],
            "P03": ["EX05", "DT06", "DT07", "DT08", "DZ03"],
            "P04": ["EX06", "DT09", "DT10", "DZ04"],
        }
        eq_list = eq_map[p_code]
        wh_formula = "+".join([f"SUMIF(Data_Equipment!B:B, \"{eq}\", Data_Equipment!C:C)" for eq in eq_list])
        br_formula = "+".join([f"SUMIF(Data_Equipment!B:B, \"{eq}\", Data_Equipment!E:E)" for eq in eq_list])
        av_formula = "+".join([f"SUMIF(Data_Equipment!B:B, \"{eq}\", Data_Equipment!F:F)" for eq in eq_list])
        fuel_formula = "+".join([f"SUMIF(Data_Fuel!B:B, \"{eq}\", Data_Fuel!C:C)" for eq in eq_list])
        
        c_wh = ws_pivot.cell(row=idx, column=6, value=f"={wh_formula}")
        c_wh.number_format = "#,##0.0"
        
        # PA % = (Available - Breakdown) / Available
        c_pa = ws_pivot.cell(row=idx, column=7, value=f"=({av_formula}-({br_formula}))/({av_formula})")
        c_pa.number_format = "0.0%"
        
        # Fuel
        c_fl = ws_pivot.cell(row=idx, column=8, value=f"={fuel_formula}")
        c_fl.number_format = "#,##0.0"
        
        # Fuel Ratio = Fuel / BCM
        c_fr = ws_pivot.cell(row=idx, column=9, value=f"=H{idx}/D{idx}")
        c_fr.number_format = "#,##0.00"
        
        for c in range(2, 10):
            ws_pivot.cell(row=idx, column=c).border = border_all
            ws_pivot.cell(row=idx, column=c).font = font_regular
            
    # Total row
    r_tot = 9
    ws_pivot.cell(row=r_tot, column=2, value="TOTAL / AVERAGE").font = font_bold
    ws_pivot.cell(row=r_tot, column=3, value="-").font = font_bold
    ws_pivot.cell(row=r_tot, column=4, value=f"=SUM(D5:D8)").number_format = "#,##0.0"
    ws_pivot.cell(row=r_tot, column=5, value=f"=SUM(E5:E8)").number_format = "#,##0.0"
    ws_pivot.cell(row=r_tot, column=6, value=f"=SUM(F5:F8)").number_format = "#,##0.0"
    ws_pivot.cell(row=r_tot, column=7, value=f"=AVERAGE(G5:G8)").number_format = "0.0%"
    ws_pivot.cell(row=r_tot, column=8, value=f"=SUM(H5:H8)").number_format = "#,##0.0"
    ws_pivot.cell(row=r_tot, column=9, value=f"=H{r_tot}/D{r_tot}").number_format = "#,##0.00"
    for c in range(2, 10):
        cell = ws_pivot.cell(row=r_tot, column=c)
        cell.font = font_bold
        cell.border = border_all
        cell.fill = fill_accent
        
    for c in range(2, 10):
        ws_pivot.column_dimensions[get_column_letter(c)].width = 24
        
    # -------------------------------------------------------------
    # 8. Sheet Dashboard
    # -------------------------------------------------------------
    ws_dash = wb.create_sheet(title="Dashboard")
    ws_dash.views.sheetView[0].showGridLines = True
    
    # Title Header Banner
    ws_dash.merge_cells("B2:J2")
    ws_dash["B2"] = "EXECUTIVE MINING PRODUCTION & PERFORMANCE DASHBOARD"
    ws_dash["B2"].font = font_title
    ws_dash["B2"].alignment = Alignment(vertical="center")
    
    ws_dash.merge_cells("B3:J3")
    ws_dash["B3"] = "Monitoring Harian, Bulanan, Efisiensi Bahan Bakar, & Selisih Budget vs Actual"
    ws_dash["B3"].font = font_subtitle
    
    # Control pill display
    ws_dash["B4"] = "Evaluasi Proyek:"
    ws_dash["B4"].font = font_bold
    ws_dash["C4"] = "=Control!C4"
    ws_dash["C4"].font = Font(name="Segoe UI", size=10, bold=True, color=ACCENT_BLUE)
    
    ws_dash["D4"] = "Periode:"
    ws_dash["D4"].font = font_bold
    ws_dash["E4"] = "=Control!C5 & \" s/d \" & Control!C6"
    ws_dash["E4"].font = font_regular
    
    # 6 KPI Cards (Row 6-8)
    kpi_defs = [
        ("B", "C", "TOTAL OVERBURDEN", "=Pivot!D9", " BCM", "#,##0.0"),
        ("E", "F", "TOTAL BATUBARA", "=Pivot!E9", " Ton", "#,##0.0"),
        ("H", "I", "PHYSICAL AVAILABILITY", "=Pivot!G9", "", "0.0%"),
    ]
    
    kpi_defs_2 = [
        ("B", "C", "FLEET WORKING HOURS", "=Pivot!F9", " Jam", "#,##0.0"),
        ("E", "F", "FUEL RATIO RATA-RATA", "=Pivot!I9", " L/BCM", "#,##0.00"),
        ("H", "I", "TOTAL BIAYA SOLAR", "=SUMPRODUCT(Data_Fuel!C2:C7301, Data_Fuel!D2:D7301)", " IDR", "Rp #,##0"),
    ]
    
    def render_kpi(col_start, col_end, row_num, label, formula, suffix, num_format):
        c1, c2 = col_start, col_end
        ws_dash.merge_cells(f"{c1}{row_num}:{c2}{row_num}")
        ws_dash.merge_cells(f"{c1}{row_num+1}:{c2}{row_num+1}")
        
        lbl_cell = ws_dash[f"{c1}{row_num}"]
        lbl_cell.value = label
        lbl_cell.font = font_kpi_lbl
        lbl_cell.alignment = Alignment(horizontal="center", vertical="center")
        
        val_cell = ws_dash[f"{c1}{row_num+1}"]
        val_cell.value = formula
        val_cell.font = font_kpi_num
        val_cell.alignment = Alignment(horizontal="center", vertical="center")
        val_cell.number_format = num_format
        
        for r in range(row_num, row_num+2):
            for col_letter in [c1, c2]:
                ws_dash[f"{col_letter}{r}"].fill = fill_card
                ws_dash[f"{col_letter}{r}"].border = border_box
                
    for c_start, c_end, lbl, frm, suf, n_fmt in kpi_defs:
        render_kpi(c_start, c_end, 6, lbl, frm, suf, n_fmt)
        
    for c_start, c_end, lbl, frm, suf, n_fmt in kpi_defs_2:
        render_kpi(c_start, c_end, 9, lbl, frm, suf, n_fmt)
        
    # Budget vs Actual Summary Table (Row 12 to 18)
    ws_dash["B12"] = "RINGKASAN BUDGET VS ACTUAL PRODUKSI & BIAYA"
    ws_dash["B12"].font = Font(name="Segoe UI", size=12, bold=True, color=NAVY)
    
    dash_tbl_headers = ["Project", "Actual OB (BCM)", "Budget OB (BCM)", "Pencapaian (%)", "Actual Solar (L)", "Budget Solar (L)", "Selisih Solar (L)", "Status"]
    for c_idx, h in enumerate(dash_tbl_headers, start=2):
        cell = ws_dash.cell(row=13, column=c_idx, value=h)
        cell.font = font_header
        cell.fill = fill_header
        cell.border = border_all
        cell.alignment = Alignment(horizontal="center")
        
    for idx, (p_code, p_name) in enumerate(projects_meta, start=14):
        p_row_pivot = idx - 9 # 5, 6, 7, 8 in Pivot
        ws_dash.cell(row=idx, column=2, value=p_code).font = font_bold
        
        # Actual OB
        c_act = ws_dash.cell(row=idx, column=3, value=f"=Pivot!D{p_row_pivot}")
        c_act.number_format = "#,##0.0"
        
        # Budget OB
        c_bgt = ws_dash.cell(row=idx, column=4, value=f"=SUMIF(Budget!B:B, B{idx}, Budget!C:C)")
        c_bgt.number_format = "#,##0.0"
        
        # Target Achievement %
        c_ach = ws_dash.cell(row=idx, column=5, value=f"=C{idx}/D{idx}")
        c_ach.number_format = "0.0%"
        
        # Actual Solar
        c_s_act = ws_dash.cell(row=idx, column=6, value=f"=Pivot!H{p_row_pivot}")
        c_s_act.number_format = "#,##0.0"
        
        # Budget Solar
        c_s_bgt = ws_dash.cell(row=idx, column=7, value=f"=SUMIF(Budget!B:B, B{idx}, Budget!E:E)")
        c_s_bgt.number_format = "#,##0.0"
        
        # Variance Solar
        c_s_var = ws_dash.cell(row=idx, column=8, value=f"=F{idx}-G{idx}")
        c_s_var.number_format = "+#,##0.0;-#,##0.0;0.0"
        
        # Status
        c_stat = ws_dash.cell(row=idx, column=9, value=f'=IF(E{idx}>=1,"ACHIEVED","BEHIND TARGET")')
        c_stat.font = font_bold
        c_stat.alignment = Alignment(horizontal="center")
        
        for c in range(2, 10):
            ws_dash.cell(row=idx, column=c).border = border_all
            if c != 9:
                ws_dash.cell(row=idx, column=c).font = font_regular
                
    # Total row in Dashboard table
    r_dash_tot = 18
    ws_dash.cell(row=r_dash_tot, column=2, value="TOTAL").font = font_bold
    ws_dash.cell(row=r_dash_tot, column=3, value="=SUM(C14:C17)").number_format = "#,##0.0"
    ws_dash.cell(row=r_dash_tot, column=4, value="=SUM(D14:D17)").number_format = "#,##0.0"
    ws_dash.cell(row=r_dash_tot, column=5, value="=C18/D18").number_format = "0.0%"
    ws_dash.cell(row=r_dash_tot, column=6, value="=SUM(F14:F17)").number_format = "#,##0.0"
    ws_dash.cell(row=r_dash_tot, column=7, value="=SUM(G14:G17)").number_format = "#,##0.0"
    ws_dash.cell(row=r_dash_tot, column=8, value="=F18-G18").number_format = "+#,##0.0;-#,##0.0;0.0"
    ws_dash.cell(row=r_dash_tot, column=9, value='=IF(E18>=1,"ACHIEVED","BEHIND TARGET")').alignment = Alignment(horizontal="center")
    for c in range(2, 10):
        cell = ws_dash.cell(row=r_dash_tot, column=c)
        cell.font = font_bold
        cell.border = border_all
        cell.fill = fill_accent
        
    # Formatting widths
    col_widths = {"A": 4, "B": 14, "C": 18, "D": 18, "E": 16, "F": 18, "G": 18, "H": 18, "I": 18, "J": 14}
    for col_l, w in col_widths.items():
        ws_dash.column_dimensions[col_l].width = w
        
    # Page setup for A4 Landscape
    ws_dash.page_setup.orientation = ws_dash.ORIENTATION_LANDSCAPE
    ws_dash.page_setup.paperSize = ws_dash.PAPERSIZE_A4
    ws_dash.sheet_properties.pageSetUpPr.fitToPage = True
    ws_dash.page_setup.fitToWidth = 1
    ws_dash.page_setup.fitToHeight = 1
    
    # -------------------------------------------------------------
    # 9. Sheet Log
    # -------------------------------------------------------------
    ws_log = wb.create_sheet(title="Log")
    ws_log.views.sheetView[0].showGridLines = True
    log_headers = ["Timestamp", "Status", "Duration (s)", "Output File", "Message"]
    for c_idx, h in enumerate(log_headers, start=1):
        cell = ws_log.cell(row=1, column=c_idx, value=h)
        cell.font = font_header
        cell.fill = fill_header
        cell.border = border_all
        
    ws_log.cell(row=2, column=1, value="2026-10-12 20:50:00").font = font_regular
    ws_log.cell(row=2, column=2, value="INITIALIZED").font = font_bold
    ws_log.cell(row=2, column=3, value=0.0).font = font_regular
    ws_log.cell(row=2, column=4, value="Mining_Performance.xlsx").font = font_regular
    ws_log.cell(row=2, column=5, value="Workbook structure and formulas generated successfully.").font = font_regular
    for c_idx in range(1, 6):
        ws_log.cell(row=2, column=c_idx).border = border_all
        
    ws_log.column_dimensions["A"].width = 22
    ws_log.column_dimensions["B"].width = 16
    ws_log.column_dimensions["C"].width = 14
    ws_log.column_dimensions["D"].width = 30
    ws_log.column_dimensions["E"].width = 50
    
    out_path = os.path.join("week1-excel", "Mining_Performance.xlsx")
    wb.save(out_path)
    print(f"Successfully created workbook: {out_path}")

if __name__ == "__main__":
    build_workbook()
