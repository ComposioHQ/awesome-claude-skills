# Data Model Overview

## Entities

- **Client**
  - `id` (`TEXT`, primary key): ID client.
  - `name` (`TEXT`): Nama lengkap client.
  - `phone` (`TEXT`, unique): Nomor HP client.
  - `email` (`TEXT`): Email client.
  - `ad_product` (`TEXT`): Nama produk iklan yang dibeli.
  - `ad_purchase_date` (`TEXT`, ISO 8601): Tanggal pembelian iklan.
  - `ad_ec_name` (`TEXT`): Nama EC (sales) yang menjual iklan.
  - `ad_payment_note` (`TEXT`): Catatan pembayaran iklan.
  - `ad_payment_status` (`TEXT`): Status pembayaran iklan (`paid`, `unpaid`).
  - `created_at` (`TEXT`, ISO 8601): Waktu pencatatan client.
  - `updated_at` (`TEXT`, ISO 8601): Waktu pembaruan data client.

- **Product**
  - `id` (`INTEGER`, primary key autoincrement): Identitas internal produk.
  - `client_id` (`TEXT`, FK → Client.id): Client terkait.
  - `unique_code` (`TEXT`): Kode unik deal.
  - `product_name` (`TEXT`): Nama produk yang di-closing.
  - `status` (`TEXT`): Status pembayaran (`DP`, `Lunas`, `Pelunasan`, `Angsuran`, `Cicilan`).
  - `amount` (`INTEGER`): Jumlah harga dalam rupiah.
  - `closing_date` (`TEXT`, ISO 8601): Tanggal closing produk.
  - `ec_name` (`TEXT`): Nama EC yang menutup penjualan.
  - `notes` (`TEXT`): Catatan tambahan.
  - `created_at` (`TEXT`, ISO 8601): Waktu pencatatan produk.
  - `updated_at` (`TEXT`, ISO 8601): Waktu pembaruan produk.

- **ProductPayment**
  - `id` (`INTEGER`, primary key autoincrement): Identitas pembayaran.
  - `product_id` (`INTEGER`, FK → Product.id): Produk yang dibayar.
  - `payment_date` (`TEXT`, ISO 8601): Tanggal pembayaran.
  - `amount` (`INTEGER`): Nominal pembayaran.
  - `status` (`TEXT`): Jenis pembayaran (`DP`, `Pelunasan`, `Angsuran`, `Cicilan`, `Lunas`).
  - `method` (`TEXT`): Metode pembayaran (opsional).
  - `notes` (`TEXT`): Keterangan tambahan.

## Derived Fields

- **time_to_close_days**: Selisih hari antara `ad_purchase_date` milik client dan `closing_date` pada setiap produk. Dihitung saat melakukan query agregasi.
- **client_payment_history**: Rekap gabungan dari `ProductPayment` untuk seluruh produk milik client, ditampilkan dalam hasil pencarian client.

## Indexes & Constraints

- `Client.phone` diberi indeks unik agar pencarian nomor HP cepat dan bebas duplikasi.
- `Product.client_id` dan `ProductPayment.product_id` memiliki indeks untuk mempercepat lookup data relasional.

