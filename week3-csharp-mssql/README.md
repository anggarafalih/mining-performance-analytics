# Weekend 3: C# (.NET 8) & SQL Server Analytics CLI

> **DISCLAIMER:**  
> Seluruh dataset dalam modul ini adalah **data sintetis** yang dibangkitkan secara matematis (`seed=42`). Proyek ini murni dibuat untuk demonstrasi portofolio analitik pertambangan.

---

## 1. Ringkasan & Tujuan Deliverable

Modul **Weekend 3** melengkapi rangkaian keahlian (*tri-stack*) dengan menghadirkan aplikasi tingkat *enterprise* menggunakan bahasa C-family (C# .NET 8) dan basis data transaksional Microsoft SQL Server 2022.

### Deliverable yang Dihasilkan:
1. **`MiningReport.sln`**: Solusi .NET 8 modern yang memuat proyek aplikasi konsol dan proyek *automated testing*.
2. **`MiningReport/`**: Aplikasi CLI Clean Architecture yang mengimplementasikan:
   - Pola *Repository* dengan `Microsoft.Data.SqlClient` dan `Dapper`.
   - *Graceful Connection Fallback*: jika server basis data offline, otomatis beralih ke pembacaan CSV master secara mulus.
   - Layanan pelaporan `PerformanceReportService` dan kalkulator domain `MetricsCalculator`.
   - Ekspor otomatis ke CSV (`CsvExporter`) dan Excel bergaya korporat (`ClosedXML`).
3. **`MiningReport.Tests/`**: Test suite unit xUnit dengan **10 unit test** yang menguji kalkulasi metrik tambang (PA, UA, Produktivitas, Fuel Ratio, dan dekomposisi 3-way varians), seluruhnya lulus (*100% Pass*).
4. **`schema_sqlserver.sql`**: Konversi skema PostgreSQL ke T-SQL dengan `IDENTITY`, `NVARCHAR`, `DECIMAL`, dan `CREATE OR ALTER VIEW`.
5. **`docker-compose.yml`**: Konfigurasi container SQL Server 2022 Express.
6. **Contoh Hasil Ekspor Laporan** di folder `output/`.

---

## 2. Perbedaan Sintaks Antara PostgreSQL & SQL Server (T-SQL)

Untuk membuktikan pemahaman lintas DBMS, berikut pemetaan konversi yang diterapkan pada skema basis data:

| Aspek / Fitur | PostgreSQL 16 (Weekend 2) | SQL Server 2022 (Weekend 3) | Catatan Desain |
| :--- | :--- | :--- | :--- |
| **Auto Increment Primary Key** | `SERIAL` / `BIGSERIAL` | `INT IDENTITY(1,1)` | SQL Server menggunakan penomoran seed identity. |
| **Tipe Data Teks** | `VARCHAR`, `TEXT` | `NVARCHAR(len)` | `NVARCHAR` mendukung penyimpanan Unicode. |
| **Tipe Data Desimal** | `NUMERIC(p, s)` | `DECIMAL(p, s)` | Menjaga presisi tinggi volume dan biaya. |
| **Fungsi Tanggal ke Teks** | `TO_CHAR(date, 'YYYY-MM')` | `FORMAT(date, 'yyyy-MM')` | Standar formatting bulanan di T-SQL. |
| **Definisi View Modifikasi** | `CREATE OR REPLACE VIEW` | `CREATE OR ALTER VIEW` | Sintaks modern SQL Server 2016+. |
| **Penanganan Pembagian Nol** | `NULLIF(col, 0)` | `NULLIF(col, 0)` | Logika seragam untuk mencegah *divide-by-zero*. |

---

## 3. Menjalankan Unit Test xUnit

Seluruh logika perhitungan analitik telah diverifikasi melalui pengujian otomatis:

```bash
# Menjalankan seluruh test suite
dotnet test week3-csharp-mssql/MiningReport.sln
```

**Hasil Pengujian:**
```text
Passed!  - Failed: 0, Passed: 10, Skipped: 0, Total: 10, Duration: 70 ms
```

Daftar 10 Unit Test yang Diuji:
1. `CalculatePhysicalAvailability_ValidInputs_ReturnsExpectedPercentage`
2. `CalculatePhysicalAvailability_ZeroAvailableHours_ReturnsZero`
3. `CalculateUtilization_ValidInputs_ReturnsExpectedPercentage`
4. `CalculateProductivity_ValidInputs_ReturnsCorrectBcmPerHour`
5. `CalculateFuelRatio_ValidInputs_ReturnsLitersPerBcm`
6. `CalculateTargetAchievement_ValidInputs_ReturnsPercentage`
7. `CalculateVolumeEffect_ValidInputs_ComputesExpectedIDR`
8. `CalculateEfficiencyEffect_ValidInputs_ComputesExpectedIDR`
9. `CalculatePriceEffect_ValidInputs_ComputesExpectedIDR`
10. `VarianceDecomposition_SumOfThreeEffects_MatchesTotalVarianceExactly` (Pembuktian matematis residu = 0)

---

## 4. Panduan Penggunaan CLI (`MiningReport`)

Aplikasi CLI dapat dijalankan melalui terminal dengan berbagai opsi perintah:

### 1. Menampilkan Ringkasan Produksi Harian (`daily`)
```bash
dotnet run --project week3-csharp-mssql/MiningReport -- daily --start 2025-01-01 --end 2025-01-15 --project P01
```

### 2. Menampilkan Ringkasan Pencapaian Target Bulanan (`monthly`)
```bash
dotnet run --project week3-csharp-mssql/MiningReport -- monthly --project P02
```

### 3. Menampilkan Analisis Selisih Anggaran Biaya Solar (`variance`)
```bash
dotnet run --project week3-csharp-mssql/MiningReport -- variance
```

### 4. Mengekspor Laporan ke CSV dan Excel (`export`)
```bash
dotnet run --project week3-csharp-mssql/MiningReport -- export --output week3-csharp-mssql/output
```

---

## 5. Tabel Rekonsiliasi Golden Truth

Angka agregasi tahunan yang dihasilkan oleh aplikasi C# ini terbukti **100% identik** dengan hasil Excel (Weekend 1) dan PostgreSQL (Weekend 2):

| Metrik Operasional Tahunan | Excel (Weekend 1) | PostgreSQL (Weekend 2) | SQL Server & C# (Weekend 3) | Selisih Lintas Alat |
| :--- | :---: | :---: | :---: | :---: |
| **Total Overburden (BCM)** | `54,411,010.6` | `54,411,010.6` | `54,411,010.6` | **0.00 (Match)** |
| **Total Batubara (Ton)** | `11,082,611.4` | `11,082,611.4` | `11,082,611.4` | **0.00 (Match)** |
| **Total Konsumsi Solar (Liter)** | `9,182,027.4` | `9,182,027.4` | `9,182,027.4` | **0.00 (Match)** |
| **Total Biaya Solar (IDR)** | `Rp 141,294,470,890` | `Rp 141,294,470,890` | `Rp 141,294,470,890` | **Rp 0 (Match)** |

---
*Dibuat sebagai bagian dari rangkaian portofolio Mining Production Performance Analytics.*
