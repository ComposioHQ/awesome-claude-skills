# Client Product Tracker CLI

Aplikasi CLI sederhana untuk mencatat data client, produk yang dibeli, dan riwayat pembayaran. Data disimpan menggunakan SQLite embedded via `better-sqlite3` sehingga tidak membutuhkan server database terpisah.

## Fitur Utama

- Pencarian client berdasarkan ID, nomor HP, atau nama.
- Rekap lengkap data client beserta histori pembelian iklan.
- Pencatatan produk yang di-closing lengkap dengan status pembayaran.
- Pencatatan detail pembayaran produk per termin.
- Tampilan ringkas track record pembayaran dalam bentuk tabel.

## Instalasi

```bash
npm install
```

## Inisialisasi Database

Database akan otomatis dibuat di `data/client-products.db` saat perintah pertama dijalankan. Pastikan folder `data/` tersedia atau biarkan aplikasi membuatnya saat runtime.

## Cara Pakai

Jalankan perintah dari root project:

### 1. Tambah / Update Client

```bash
node src/cli.js client:add \
  --id C001 \
  --name "Andi Wijaya" \
  --phone 08123456789 \
  --email andi@example.com \
  --ad-product "Paket Iklan A" \
  --ad-date 2024-01-10 \
  --ad-ec "Budi" \
  --ad-note "Sudah bayar DP" \
  --ad-status paid
```

### 2. Cari Client

```bash
node src/cli.js client:search andi
```

### 3. Lihat Detail Client

```bash
node src/cli.js client:detail 08123456789
```

### 4. Rekam Produk

```bash
node src/cli.js product:add \
  --client-id 08123456789 \
  --name "Paket Konsultasi" \
  --amount 5000000 \
  --status DP \
  --code PK001 \
  --date 2024-02-01 \
  --ec "Sari" \
  --notes "Deal pertama"
```

### 5. Rekam Pembayaran

```bash
node src/cli.js payment:add \
  --product-id 1 \
  --date 2024-02-05 \
  --amount 2000000 \
  --status DP \
  --method Transfer \
  --notes "Pembayaran awal"
```

## Struktur Proyek

- `src/db.js` – Inisialisasi database dan definisi schema.
- `src/repository.js` – Query database (CRUD) untuk client, produk, dan pembayaran.
- `src/service.js` – Validasi dan logika bisnis tingkat aplikasi.
- `src/cli.js` – Antarmuka CLI menggunakan Commander.js.
- `docs/data-model.md` – Dokumentasi struktur data dan relasi.

## Pengembangan Lanjutan

- Tambah validasi format tanggal dan nomor HP.
- Ekspor laporan ke CSV atau Excel.
- Integrasi API/web dashboard untuk akses multi-user.

