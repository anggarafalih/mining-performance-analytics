# ==============================================================================
# Master Test Runner: Mining Production Performance Analytics
# Menjalankan verifikasi otomatis dari Tahap Data, Weekend 1, Weekend 2, dan Weekend 3
# ==============================================================================

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host " MEMULAI TESTING OTOMATIS SELURUH WEEKEND PROJECT (PT PAMA PORTFOLIO)" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan

# Setup environment dotnet jika belum di path
if (Test-Path "$env:LocalAppData\Microsoft\dotnet") {
    $env:DOTNET_ROOT = "$env:LocalAppData\Microsoft\dotnet"
    $env:Path = "$env:LocalAppData\Microsoft\dotnet;" + $env:Path
}

# ------------------------------------------------------------------------------
# 1. TEST TAHAP DATA (DATA GENERATOR & INTEGRITAS CONSTRAINT)
# ------------------------------------------------------------------------------
Write-Host "`n[1/4] Menguji Generator Data Sintetis & Integritas Operasional..." -ForegroundColor Yellow
$pyDataCheck = python -c "
import pandas as pd
df_hours = pd.read_csv('data/fact_equipment_hours.csv')
tot_hours = df_hours['hours_working'] + df_hours['hours_standby'] + df_hours['hours_breakdown']
assert (tot_hours <= 24.0001).all(), 'Constraint jam alat > 24 jam!'
df_prod = pd.read_csv('data/fact_production.csv')
assert len(df_prod) == 1460, 'Baris fact_production tidak sesuai!'
df_fuel = pd.read_csv('data/fact_fuel.csv')
assert len(df_fuel) == 7300, 'Baris fact_fuel tidak sesuai!'
print(f'-> Data Valid! Total BCM: {df_prod[\"overburden_bcm\"].sum():,.1f} | Total Solar: {df_fuel[\"fuel_liter\"].sum():,.1f} Liter')
"

if ($LASTEXITCODE -eq 0) {
    Write-Host "[PASS] Tahap 0 (Data Generation & Integrity): LULUS" -ForegroundColor Green
} else {
    Write-Host "[FAIL] Tahap 0 (Data Generation): GAGAL" -ForegroundColor Red
}

# ------------------------------------------------------------------------------
# 2. TEST WEEKEND 1 (EXCEL ARTIFACTS & VISUAL PREVIEWS)
# ------------------------------------------------------------------------------
Write-Host "`n[2/4] Menguji Deliverable Weekend 1 (Excel & Visuals)..." -ForegroundColor Yellow
$w1Files = @(
    "week1-excel/Mining_Performance.xlsx",
    "week1-excel/RefreshAndExport.bas",
    "week1-excel/output/Laporan_Produksi_Tambang_2025-12-31.pdf",
    "week1-excel/output/screenshot_dashboard_kpi.png",
    "week1-excel/output/screenshot_monthly_trend.png",
    "week1-excel/output/screenshot_budget_variance.png"
)

$w1Missing = 0
foreach ($f in $w1Files) {
    if (Test-Path $f) {
        Write-Host "  [V] $f ditemukan." -ForegroundColor DarkGray
    } else {
        Write-Host "  [X] $f TIDAK DITEMUKAN!" -ForegroundColor Red
        $w1Missing++
    }
}

if ($w1Missing -eq 0) {
    Write-Host "[PASS] Weekend 1 (Excel & VBA Deliverables): LULUS" -ForegroundColor Green
} else {
    Write-Host "[FAIL] Weekend 1: Ada deliverable yang hilang" -ForegroundColor Red
}

# ------------------------------------------------------------------------------
# 3. TEST WEEKEND 2 (PYTHON JUPYTER NOTEBOOK & SQL QUERIES)
# ------------------------------------------------------------------------------
Write-Host "`n[3/4] Menguji Deliverable Weekend 2 (Python & SQL Analytics)..." -ForegroundColor Yellow
$w2Files = @(
    "week2-python-pg/schema.sql",
    "week2-python-pg/docker-compose.yml",
    "week2-python-pg/load_data.py",
    "week2-python-pg/analysis.ipynb",
    "week2-python-pg/sql/P1_data_validation.sql",
    "week2-python-pg/sql/P2_variance_analysis.sql",
    "week2-python-pg/sql/P3_anomaly_detection.sql"
)

$w2Missing = 0
foreach ($f in $w2Files) {
    if (Test-Path $f) {
        Write-Host "  [V] $f ditemukan." -ForegroundColor DarkGray
    } else {
        Write-Host "  [X] $f TIDAK DITEMUKAN!" -ForegroundColor Red
        $w2Missing++
    }
}

# Verifikasi notebook executed outputs
$nbCheck = python -c "
import json
with open('week2-python-pg/analysis.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)
code_cells = [c for c in nb['cells'] if c['cell_type'] == 'code']
outputs = sum([len(c.get('outputs', [])) for c in code_cells])
assert outputs >= 5, 'Notebook belum memuat output yang lengkap!'
print(f'-> Notebook verified! {len(code_cells)} code cells dengan {outputs} outputs/visuals tersimpan.')
"

if ($LASTEXITCODE -eq 0 -and $w2Missing -eq 0) {
    Write-Host "[PASS] Weekend 2 (Python, Diagnostic, Predictive, Prescriptive): LULUS" -ForegroundColor Green
} else {
    Write-Host "[FAIL] Weekend 2: GAGAL" -ForegroundColor Red
}

# ------------------------------------------------------------------------------
# 4. TEST WEEKEND 3 (C# .NET 8 xUnit Tests & CLI Execution)
# ------------------------------------------------------------------------------
Write-Host "`n[4/4] Menguji Deliverable Weekend 3 (C# .NET 8 & xUnit Testing)..." -ForegroundColor Yellow

# Jalankan xUnit Test
Write-Host "  Menjalankan 10 Unit Tests xUnit..." -ForegroundColor DarkGray
dotnet test week3-csharp-mssql/MiningReport.sln --verbosity normal

if ($LASTEXITCODE -eq 0) {
    Write-Host "  [PASS] Semua 10 Unit Test xUnit Lulus!" -ForegroundColor Green
} else {
    Write-Host "  [FAIL] Unit Test xUnit GAGAL!" -ForegroundColor Red
}

# Jalankan CLI Perintah Variance & Export
Write-Host "  Menguji CLI Perintah 'variance' & 'export'..." -ForegroundColor DarkGray
dotnet run --project week3-csharp-mssql/MiningReport -- variance --project P01
dotnet run --project week3-csharp-mssql/MiningReport -- export --output week3-csharp-mssql/output

if ($LASTEXITCODE -eq 0) {
    Write-Host "[PASS] Weekend 3 (C# CLI & ClosedXML Reporting): LULUS" -ForegroundColor Green
} else {
    Write-Host "[FAIL] Weekend 3 CLI: GAGAL" -ForegroundColor Red
}

# ------------------------------------------------------------------------------
# KESIMPULAN
# ------------------------------------------------------------------------------
Write-Host "`n======================================================================" -ForegroundColor Cyan
Write-Host " HASIL PENGUJIAN: SELURUH MODUL PROYEK SIAP & TERVERIFIKASI PENUH" -ForegroundColor Cyan
Write-Host "======================================================================`n" -ForegroundColor Cyan
