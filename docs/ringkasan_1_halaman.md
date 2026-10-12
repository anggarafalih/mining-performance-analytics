# Ringkasan Eksekutif Portofolio: Mining Production Performance Analytics

**Kandidat:** @faleh | **Target Peran:** Mining Data Analyst / Operational Analytics Engineer  
**Teknologi:** Advanced Excel & VBA, Python, PostgreSQL, C# (.NET 8), SQL Server, Docker  
**Status Portofolio:** Selesai & Tereproduksi Penuh (Seed 42)

---

### 1. Latar Belakang & Problem Statement
Dalam operasi penambangan batubara skala besar (kontraktor tambang seperti PT Pamapersada Nusantara), tantangan analitik terbesar adalah memastikan **sinkronisasi data operasional harian**, **analisis akar masalah penyimpangan anggaran biaya**, dan **ketepatan peramalan di tengah variabilitas cuaca ekstrem**. Studi kasus ini mengintegrasikan seluruh rantai analitik di tiga tumpukan teknologi industri dengan dataset tunggal yang konsisten.

---

### 2. Arsitektur Solusi & Deliverable Tri-Stack

```
                [ DATASET MASTER OPERASIONAL TAMBANG (Seed 42) ]
                  4 Site Tambang | 20 Alat Berat | 365 Hari 2025
                                        │
        ┌───────────────────────────────┼───────────────────────────────┐
        ▼                               ▼                               ▼
 [ WEEKEND 1: EXCEL ]       [ WEEKEND 2: PYTHON & PG ]      [ WEEKEND 3: C# & MSSQL ]
 • Power Query Data Cleaning • PostgreSQL 16 & Views         • .NET 8 CLI Clean Arch
 • SUMIFS / XLOOKUP Modeling • 3-Way Variance Decomposition  • Dapper / SqlClient DAL
 • A4 Landscape KPI Cards    • Weather-Aware ML Forecasting  • ClosedXML Multi-Export
 • VBA Macro Otomasi PDF     • Prescriptive PuLP (Linear LP) • xUnit Test Suite
```

---

### 3. Temuan Kunci & Dampak Bisnis (Diagnostic, Predictive, Prescriptive)

1. **Diagnostic (Akar Masalah Varians Biaya Solar)**:
   - Berhasil memecah total selisih biaya solar **Rp -5.82 Miliar** menjadi 3 komponen eksak tanpa residu: **Efek Volume** (-Rp 14.23 M), **Efek Efisiensi** (-Rp 1.17 M), dan **Efek Harga Pasar** (+Rp 9.58 M).
   - Menemukan anomali pembengkakan biaya di **Site P03 sebesar +Rp 2.48 Miliar** yang murni diakibatkan oleh degradasi *fuel ratio* alat berat (+Rp 2.21 M).
2. **Predictive (Peramalan Produksi Berbasis Cuaca)**:
   - Model Ridge Regression yang memanfaatkan fitur curah hujan harian (`rainfall_mm`) menghasilkan akurasi tinggi dengan **MAPE 7.15% & RMSE 18.240 BCM**, secara signifikan mengungguli baseline konvensional *Seasonal Naive* (**MAPE 12.84%**).
3. **Prescriptive (Optimasi Alokasi Jam Alat Antar Site)**:
   - Formulasi Linear Programming (PuLP) mengoptimalkan distribusi jam kerja armada di bawah batasan kuota solar, menghasilkan peningkatan output produksi sebesar **+15.200 BCM/hari (+7.7%)** tanpa perlu penambahan alat baru.

---

### 4. Matriks Integritas & Rekonsiliasi Lintas Alat (Zero-Difference Audit)

| Metrik Operasional Tahunan | Excel (.xlsm) | PostgreSQL | C# & SQL Server | Selisih Lintas Alat |
| :--- | :---: | :---: | :---: | :---: |
| **Total Overburden (BCM)** | 54,411,010.6 | 54,411,010.6 | 54,411,010.6 | **0.00 (Match)** |
| **Total Batubara (Ton)** | 11,082,611.4 | 11,082,611.4 | 11,082,611.4 | **0.00 (Match)** |
| **Total Konsumsi Solar (Liter)** | 9,182,027.4 | 9,182,027.4 | 9,182,027.4 | **0.00 (Match)** |
| **Total Biaya Solar (IDR)** | Rp 141,294,470,890 | Rp 141,294,470,890 | Rp 141,294,470,890 | **Rp 0 (Match)** |

---

### 5. Nilai Tambah untuk Perusahaan
- **Kesiapan Kerja Langsung (*Plug & Play*)**: Menguasai alat kerja operasional harian (Excel/VBA) hingga sistem analitik backend korporasi (SQL Server & PostgreSQL).
- **Ketelitian & Integritas Tinggi**: Terbiasa melakukan audit rekonsiliasi data hingga selisih 0.
- **Berorientasi Nilai Bisnis**: Mampu menyajikan temuan teknis kompleks ke dalam rekomendasi strategis yang dapat dieksekusi oleh manajemen tambang.
