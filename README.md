# Mining Production Performance Analytics (PT PAMA Portfolio Case Study)

> **DISCLAIMER:**  
> Seluruh dataset dalam proyek ini adalah **data sintetis** yang dibangkitkan secara matematis dengan skrip Python (`seed=42`) untuk keperluan simulasi portofolio analitik pertambangan. Proyek ini **bukan data riil perusahaan** dan tidak memuat informasi rahasia (*non-confidential*).

---

## Ringkasan Proyek

Proyek ini mendemonstrasikan kapabilitas analisis performa produksi operasional tambang batubara dan pemindahan tanah penutup (*overburden removal*) secara *end-to-end*. Proyek ini dirancang untuk menjawab kebutuhan industri kontraktor penambangan kelas dunia (seperti standar operasional PT Pamapersada Nusantara / PAMA) dengan menerapkan satu dataset fakta yang konsisten di tiga tumpukan teknologi berbeda (*tri-stack*):

1. **Weekend 1: Advanced MS Excel & VBA** (Power Query cleaning, dynamic KPI modeling, SUMIFS/XLOOKUP, PivotTable, VBA macro automation).
2. **Weekend 2: Python & PostgreSQL** (Dockerized PostgreSQL 16, SQL CTE & window functions, Root-cause Diagnostic variance decomposition, Predictive 30-day forecast with weather factors, Prescriptive PuLP linear programming optimization).
3. **Weekend 3: C# (.NET 8) & SQL Server** (Dockerized SQL Server 2022 Express, Clean Architecture CLI, ClosedXML reporting, xUnit testing, dan rekonsiliasi data lintas platform).

---

## Struktur Repositori

```text
PT PAMA WEEKEND PROJECT/
├── data/
│   ├── generate_data.py               # Generator data sintetis terpusat (seed 42)
│   ├── dim_project.csv                # 4 Master site (P01 - P04)
│   ├── dim_equipment.csv              # 20 Master unit alat berat (EX, DT, DZ)
│   ├── fact_production.csv            # 1,460 baris data produksi & curah hujan harian 2025
│   ├── fact_equipment_hours.csv       # 7,300 baris jam kerja alat harian (PA & UA)
│   ├── fact_fuel.csv                  # 7,300 baris konsumsi bahan bakar & fluktuasi harga
│   ├── budget_monthly.csv             # 48 baris anggaran biaya & target bulanan
│   └── raw/                           # Dataset mentah dengan anomali & baris kotor untuk Power Query
├── week1-excel/
│   ├── build_workbook.py              # Script pembangun file Excel otomatis
│   ├── Mining_Performance.xlsx        # Workbook Excel interaktif (disimpan juga sebagai .xlsm)
│   ├── RefreshAndExport.bas           # Source code makro VBA diekspor (.bas)
│   ├── README.md                      # Dokumentasi & panduan Weekend 1
│   └── output/                        # Folder ekspor PDF otomatis dari VBA
├── week2-python-pg/
│   ├── docker-compose.yml             # PostgreSQL 16 container setup
│   ├── schema.sql                     # DDL skema database, constraint CHECK, dan Views analitik
│   ├── load_data.py                   # Loader data idempotensial ke PostgreSQL
│   ├── analysis.ipynb                 # Jupyter notebook lengkap: Diagnostic, Predictive, Prescriptive
│   ├── sql/                           # Kumpulan query mandiri (P1 Validasi, P2 Varians, P3 Anomali)
│   └── README.md                      # Dokumentasi & panduan Weekend 2
├── week3-csharp-mssql/
│   ├── docker-compose.yml             # SQL Server 2022 Express container setup
│   ├── schema_sqlserver.sql           # Skema T-SQL & view analitik SQL Server
│   ├── MiningReport.sln               # Solusi .NET 8 Visual Studio / VS Code
│   ├── MiningReport/                  # Aplikasi Console CLI (.NET 8)
│   ├── MiningReport.Tests/            # xUnit Test Project (minimal 8 unit test)
│   └── README.md                      # Dokumentasi & panduan Weekend 3
├── docs/
│   ├── rekonsiliasi.md                # Tabel verifikasi rekonsiliasi lintas alat (selisih 0)
│   └── ringkasan_1_halaman.md         # One-pager portfolio summary untuk lampiran CV
└── README.md                          # Gambaran umum repositori ini
```

---

## Matriks Rekonsiliasi Baseline (Golden Truth - Seed 42)

Untuk membuktikan integritas dan ketelitian data, total agregat tahunan dihitung dan direkonsiliasi di ketiga alat tanpa selisih (selisih = 0):

| Metrik Operasional Tahunan | Excel (Weekend 1) | PostgreSQL (Weekend 2) | SQL Server & C# (Weekend 3) | Selisih Lintas Alat |
| :--- | :---: | :---: | :---: | :---: |
| **Total Overburden (BCM)** | `54,411,010.6` | `54,411,010.6` | `54,411,010.6` | **0.00 (Match)** |
| **Total Batubara (Ton)** | `11,082,611.4` | `11,082,611.4` | `11,082,611.4` | **0.00 (Match)** |
| **Total Bahan Bakar (Liter)** | `9,182,027.4` | `9,182,027.4` | `9,182,027.4` | **0.00 (Match)** |
| **Total Biaya Solar (IDR)** | `Rp 141,294,470,890` | `Rp 141,294,470,890` | `Rp 141,294,470,890` | **Rp 0 (Match)** |

---

## Fitur Utama & Keunggulan Analitik

1. **Pemodelan Data Operasional Tambang Standar**:
   - Menghitung metrik baku: *Physical Availability* (PA), *Utilization of Availability* (UA), *Produktivitas Unit* (BCM/jam), dan *Fuel Ratio* (Liter/BCM).
   - Menegakkan integritas data operasional: $\text{Jam Kerja} + \text{Jam Standby} + \text{Jam Breakdown} = 24.0\text{ jam/hari}$.

2. **Injeksi Anomali Terencana**:
   - **Anomali Cuaca**: 3 hari hujan ekstrem (>115 mm) yang memicu *slippery/standby* masif dan penurunan produksi harian hingga 75%.
   - **Anomali Alat**: 2 kerusakan mayor tak terencana (*major breakdown* >5 hari beruntun) pada unit Excavator primer EX02 dan Dump Truck DT05.
   - **Anomali Efisiensi**: Kenaikan bertahap *fuel ratio* pada Proyek P03 akibat penurunan efisiensi mesin / degradasi *haul road*.

3. **Analisis Lanjutan Tiga Dimensi**:
   - **Diagnostic**: Pemecahan selisih biaya anggaran (*variance analysis*) menjadi 3 komponen eksak: **Efek Volume**, **Efek Harga Bahan Bakar**, dan **Efek Efisiensi (Fuel Ratio)**.
   - **Predictive**: Peramalan produksi dan konsumsi solar 30 hari ke depan dengan model regresi berbasis fitur cuaca (`rainfall_mm`) serta pembanding time-series (*Seasonal Naive* baseline), divalidasi dengan MAPE & RMSE.
   - **Prescriptive**: Optimasi alokasi jam kerja alat berat antar site tambang menggunakan Linear Programming (PuLP) untuk memaksimalkan produksi BCM di bawah batasan jam kerja tersedia, target kuota minimum, dan kuota bahan bakar.

---

## Panduan Cepat Menjalankan Proyek

### 1. Pembangkitan Data Sintetis
```bash
python data/generate_data.py
```

### 2. Weekend 1: Excel & VBA
- Buka file `week1-excel/Mining_Performance.xlsx` (atau versi makro `.xlsm`).
- File `week1-excel/RefreshAndExport.bas` berisi makro otomasi yang dapat diimpor langsung ke VBE (Visual Basic Editor) Excel.

### 3. Weekend 2: Python & PostgreSQL
```bash
cd week2-python-pg
docker compose up -d
python load_data.py
jupyter notebook analysis.ipynb
```

### 4. Weekend 3: C# & SQL Server
```bash
cd week3-csharp-mssql
docker compose up -d
dotnet test MiningReport.Tests
dotnet run --project MiningReport -- export
```

---
*Dibuat oleh @faleh sebagai portofolio Mining Production Performance Analytics.*
