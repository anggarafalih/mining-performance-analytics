# Dokumen Rekonsiliasi Data Lintas Platform (Tri-Stack Reconciliation)

> **DISCLAIMER:**  
> Seluruh dataset dalam proyek ini adalah **data sintetis** yang dibangkitkan secara matematis (`seed=42`). Data ini digunakan murni untuk keperluan studi kasus portofolio analitik pertambangan.

---

## 1. Tujuan & Metodologi Rekonsiliasi

Dalam arsitektur analitik modern di industri pertambangan (khususnya standar kontraktor tambang kelas dunia seperti PT Pamapersada Nusantara), integritas dan kebenaran data (*data truthfulness*) adalah aspek non-negosiasi. Ketika satu dataset operasional diproses di tiga tumpukan teknologi berbeda:

1. **Excel & VBA** (Client Spreadsheet Modeling)
2. **PostgreSQL & Python** (Data Warehouse & Advanced Analytics)
3. **SQL Server & C# .NET 8** (Enterprise Transactional & Operational Reporting)

Maka seluruh hasil agregasi tahunan **wajib menghasilkan angka yang identik hingga desimal terkecil (Selisih = 0)**.

---

## 2. Tabel Rekonsiliasi Utama (Golden Truth - Seed 42)

Evaluasi penuh periode 1 Januari 2025 sampai dengan 31 Desember 2025 (365 hari operasi penuh, 4 site tambang, 20 unit armada alat berat):

| Metrik Operasional Tahunan | Satuan | Excel (Weekend 1) | PostgreSQL (Weekend 2) | SQL Server & C# (Weekend 3) | Selisih Absolut | Status Rekonsiliasi |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Total Volume Overburden** | BCM | `54,411,010.6` | `54,411,010.6` | `54,411,010.6` | **0.00** | **PASS (100% Match)** |
| **Total Produksi Batubara** | Ton | `11,082,611.4` | `11,082,611.4` | `11,082,611.4` | **0.00** | **PASS (100% Match)** |
| **Total Konsumsi Solar** | Liter | `9,182,027.4` | `9,182,027.4` | `9,182,027.4` | **0.00** | **PASS (100% Match)** |
| **Total Biaya Bahan Bakar** | IDR | `Rp 141,294,470,890` | `Rp 141,294,470,890` | `Rp 141,294,470,890` | **Rp 0.00** | **PASS (100% Match)** |
| **Total Fleet Working Hours**| Jam | `101,363.5` | `101,363.5` | `101,363.5` | **0.00** | **PASS (100% Match)** |
| **Rata-rata Fleet PA** | % | `88.6%` | `88.6%` | `88.6%` | **0.00%** | **PASS (100% Match)** |
| **Rata-rata Fuel Ratio** | L/BCM | `1.687` | `1.687` | `1.687` | **0.000** | **PASS (100% Match)** |

---

## 3. Rincian Rekonsiliasi per Site Proyek

| Kode Site | Lokasi Tambang | Overburden (BCM) | Batubara (Ton) | Solar (Liter) | Biaya Solar (IDR) | Fuel Ratio (L/BCM) |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: |
| **P01** | Sangatta North | `13,382,109.2` | `2,710,488.5` | `2,207,185.8` | `Rp 33,965,066,960` | `1.649` |
| **P02** | Tutupan South | `14,561,043.9` | `2,869,471.2` | `2,450,119.5` | `Rp 37,705,334,130` | `1.683` |
| **P03** | Paser Ridge | `12,987,143.4` | `2,661,509.3` | `2,326,988.7` | `Rp 35,807,126,810` | `1.792` *(Anomaly)* |
| **P04** | Binungan West | `13,480,714.1` | `2,841,142.4` | `2,197,733.4` | `Rp 33,816,942,990` | `1.630` |
| **TOTAL** | **Semua Site** | **54,411,010.6** | **11,082,611.4** | **9,182,027.4** | **Rp 141,294,470,890** | **1.687** |

---

## 4. Pembuktian Rekonsiliasi 3-Way Variance Decomposition

Ketiga platform menerapkan formula dekomposisi varians anggaran yang sama secara eksak:

$$\text{Total Selisih Biaya Solar} = \text{Efek Volume} + \text{Efek Efisiensi} + \text{Efek Harga}$$

| Site Proyek | Total Variance (IDR) | Efek Volume (IDR) | Efek Efisiensi (IDR) | Efek Harga (IDR) | Residu Selisih Pembuktian |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **P01** | -Rp 3,191,933,040 | -Rp 5,084,078,088 | -Rp 1,050,477,072 | +Rp 2,942,622,120 | **Rp 0.0000** |
| **P02** | -Rp 3,863,165,870 | -Rp 4,865,524,677 | -Rp 1,048,641,193 | +Rp 2,051,000,000 | **Rp 0.0000** |
| **P03** | **+Rp 2,484,726,810** | -Rp 2,308,084,418 | **+Rp 2,212,811,228** | +Rp 2,580,000,000 | **Rp 0.0000** |
| **P04** | -Rp 1,250,557,010 | -Rp 1,972,002,499 | -Rp 1,288,554,511 | +Rp 2,010,000,000 | **Rp 0.0000** |
| **TOTAL** | **-Rp 5,820,929,110** | **-Rp 14,229,689,682** | **-Rp 1,174,861,548** | **+Rp 9,583,622,120** | **Rp 0.0000** |

---

## 5. Kesimpulan Audit Integritas Data

1. **Nol Inkonsistensi**: Tidak ditemukan deviasi pembulatan (*rounding errors*) maupun inkonsistensi tipe data di seluruh pipeline Excel, PostgreSQL, dan C#/SQL Server.
2. **Keterulangan Sempurna (100% Reproducibility)**: Dataset yang dibangkitkan dengan `seed=42` dapat diulang kapan saja dan menghasilkan angka yang persis sama di lingkungan manapun.
3. **Kepatuhan Terhadap Standar PAMA**: Struktur data, satuan BCM, metric PA, UA, dan Fuel Ratio sepenuhnya merefleksikan arsitektur analitik operasional tambang profesional.
