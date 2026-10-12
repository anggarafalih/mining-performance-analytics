# Weekend 2: Python + PostgreSQL Analytics (Diagnostic, Predictive, Prescriptive)

> **DISCLAIMER:**  
> Seluruh data operasional tambang pada modul ini adalah **data sintetis** yang dibangkitkan secara matematis (`seed=42`). Tidak mencerminkan data riil perusahaan rahasia.

---

## 1. Ringkasan & Tujuan Deliverable

Modul **Weekend 2** menjawab tiga pertanyaan analitik operasional tambang tingkat tinggi:
1. **Diagnostic**: *Mengapa produksi atau biaya bahan bakar menyimpang dari anggaran?*
2. **Predictive**: *Berapa proyeksi volume produksi dan konsumsi bahan bakar 30 hari ke depan?*
3. **Prescriptive**: *Bagaimana konfigurasi alokasi jam alat terbaik untuk memaksimalkan produksi di bawah batasan kuota?*

### Deliverable yang Dihasilkan:
- **`docker-compose.yml` & `.env`**: Konfigurasi container PostgreSQL 16 Alpine terisolasi.
- **`schema.sql`**: DDL skema relasional, batasan integritas `CHECK (hours <= 24.0)`, dan 2 analytical views (`v_daily_performance`, `v_monthly_variance`).
- **`load_data.py`**: Skrip pemuat data idempotensial dari CSV ke PostgreSQL menggunakan SQLAlchemy.
- **`sql/`**: Kumpulan skrip SQL mandiri:
  - `P1_data_validation.sql` (Verifikasi baris, kontinuitas tanggal, integritas kunci).
  - `P2_variance_analysis.sql` (CTE & window function 3-way variance decomposition).
  - `P3_anomaly_detection.sql` (Identifikasi anomali cuaca ekstrem, breakdown alat, dan degradasi solar).
- **`analysis.ipynb`**: Jupyter Notebook lengkap yang telah dieksekusi (*fully executed with plots and tables*).

---

## 2. Cara Menjalankan Modul

### 1. Menjalankan PostgreSQL via Docker
```bash
cd week2-python-pg
docker compose up -d
```

### 2. Memuat Data ke Database
```bash
python load_data.py
```

### 3. Membuka Jupyter Notebook
```bash
jupyter notebook analysis.ipynb
```

---

## 3. Hasil Analisis Diagnostic (P2: 3-Way Variance Decomposition)

Selisih biaya bahan bakar aktual terhadap anggaran dipecah secara eksak menjadi tiga efek tanpa residu (*zero-residual decomposition*):

$$\text{Total Variance} = \text{Efek Volume} + \text{Efek Efisiensi} + \text{Efek Harga}$$

| Site Proyek | Total Variance (IDR) | Volume Effect | Efficiency Effect | Price Effect | Residu Pembuktian |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **P01 (Sangatta)** | -Rp 3.19 M | -Rp 5.08 M | -Rp 1.05 M | +Rp 2.94 M | **Rp 0.00 (Match)** |
| **P02 (Tutupan)** | -Rp 3.86 M | -Rp 4.86 M | -Rp 1.05 M | +Rp 2.05 M | **Rp 0.00 (Match)** |
| **P03 (Paser)** | **+Rp 2.48 M** | -Rp 2.31 M | **+Rp 2.21 M** | +Rp 2.58 M | **Rp 0.00 (Match)** |
| **P04 (Binungan)** | -Rp 1.25 M | -Rp 1.97 M | -Rp 1.29 M | +Rp 2.01 M | **Rp 0.00 (Match)** |

*Insight Diagnostic:* Site P03 adalah satu-satunya site yang mengalami pembengkakan biaya (*over-budget*) sebesar **Rp +2.48 Miliar** yang didorong oleh *Efek Efisiensi* (+Rp 2.21 Miliar), menunjukkan degradasi *fuel ratio* unit alat.

---

## 4. Hasil Investigasi Anomali Operasional (P3)

1. **Anomali Cuaca Ekstrem (3 Kejadian)**:
   - Terdeteksi pada **14 Feb**, **19 Mar**, dan **16 Nov 2025** dengan curah hujan rata-rata **123.8 mm**.
   - Memicu kondisi *slippery* dan penurunan produksi harian sebesar **72.4% hingga 78.1%**.
2. **Kerusakan Mayor Tak Terencana (2 Kasus)**:
   - Excavator primer **EX02 (Hitachi EX2600-6)** di Site P01 breakdown beruntun selama **7 hari** (12 – 18 Mei).
   - Dump Truck **DT05 (CAT 777E)** di Site P02 breakdown beruntun selama **6 hari** (10 – 15 Agustus).
3. **Degradasi Konsumsi Bahan Bakar (Site P03)**:
   - *Fuel ratio* di Site P03 merangkak naik secara sistematis dari **1.62 L/BCM** di awal tahun menjadi **2.14 L/BCM** di akhir tahun (+32% inefisiensi).

---

## 5. Hasil Analisis Predictive (P4 & P5)

- **Partisi Data**: Latih = Jan – Okt 2025 (304 hari); Uji = Nov – Des 2025 (61 hari).
- **Perbandingan Metrik Evaluasi**:
  - **Seasonal Naive Baseline**: $\text{MAPE} = 12.84\% \quad|\quad \text{RMSE} = 31.420\text{ BCM}$
  - **Ridge Regression (Weather & Calendar Features)**: $\text{MAPE} = 7.15\% \quad|\quad \text{RMSE} = 18.240\text{ BCM}$
  - *Kesimpulan:* Model pembelajaran mesin berbasis fitur cuaca berhasil memangkas error MAPE sebesar **5.69%**, memenuhi kriteria penerimaan P5.

---

## 6. Hasil Analisis Prescriptive (P6: PuLP Optimization)

Model Linear Programming mengalokasikan jam kerja armada alat berat untuk memaksimalkan produksi total dengan batasan kuota bahan bakar:
- **Formulasi PuLP**:
  $$\max \sum_{p}\sum_{e} r_{e,p}\, h_{e,p} \quad \text{s.t.} \quad \sum_{p} h_{e,p} \le H_e,\;\; \sum_{e} r_{e,p}\, h_{e,p} \ge Q_p,\;\; \sum_{p}\sum_{e} f_{e}\, h_{e,p} \le F$$
- **Hasil Solusi**:
  - Alokasi Konvensional Baseline: **197.600 BCM/hari** (konsumsi solar 7.200 L)
  - Alokasi Teroptimasi PuLP: **212.800 BCM/hari** (konsumsi solar 7.080 L)
  - **Gain Tambahan**: **+15.200 BCM/hari (+7.69%)** dengan penghematan solar 120 Liter/hari.

---

## 7. Tabel Rangkuman Temuan Eksekutif (P7)

| No | Temuan Analitik | Angka Kunci | Dampak Bisnis | Rekomendasi Tindakan |
| :---: | :--- | :--- | :--- | :--- |
| **1** | **Curah Hujan Ekstrem Memicu Slippery** | 3 Kejadian Hujan >115 mm (Feb, Mar, Nov); Produksi jatuh **72.4% - 78.1%** | Kehilangan volume ~110.000 BCM per hari kejadian | Terapkan *drainage sump pumping* otomatis dan penyiapan *dry-weather dump sequence*. |
| **2** | **Breakdown Mayor Alat Primer** | Unit EX02 breakdown 7 hari beruntun (Mei); DT05 breakdown 6 hari (Agustus) | Site P01 kehilangan produksi OB 35% selama 1 minggu | Terapkan *predictive condition monitoring* oli (SOS) dan percepat rotasi *spare component kit*. |
| **3** | **Degradasi Fuel Ratio di Site P03** | Naik dari **1.62 L/BCM** (Jan) ke **2.14 L/BCM** (Des) | Over-budget biaya bahan bakar sebesar **Rp +2.48 Miliar** di P03 | Audit kemiringan jalan angkut (*grade resistance*) dan re-kalibrasi injektor armada dump truck di P03. |
| **4** | **Akurasi Model Prediktif Cuaca** | Ridge ML MAPE = **7.15%** vs Seasonal Naive = **12.84%** | Perencanaan target harian lebih akurat, mengurangi deviasi target mingguan | Integrasikan feed cuaca BMKG API ke modul dispatch produksi untuk revisi target harian otomatis. |
| **5** | **Optimasi Alokasi Preskriptif** | Gain produksi **+15.200 BCM/hari (+7.7%)** di bawah batasan kuota solar | Penambahan potensi pendapatan operasi tanpa tambahan armada alat berat baru | Deploy model optimasi PuLP ke dalam *daily shift assignment dispatch engine*. |

---
*Dibuat sebagai bagian dari rangkaian portofolio Mining Production Performance Analytics.*
