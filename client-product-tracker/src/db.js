const Database = require('better-sqlite3');
const path = require('path');

const db = new Database(path.join(__dirname, '..', 'data', 'client-products.db'));

db.pragma('foreign_keys = ON');

db.exec(`
CREATE TABLE IF NOT EXISTS clients (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  phone TEXT UNIQUE NOT NULL,
  email TEXT,
  ad_product TEXT,
  ad_purchase_date TEXT,
  ad_ec_name TEXT,
  ad_payment_note TEXT,
  ad_payment_status TEXT CHECK(ad_payment_status IN ('paid','unpaid')),
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS products (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  client_id TEXT NOT NULL,
  unique_code TEXT,
  product_name TEXT NOT NULL,
  status TEXT CHECK(status IN ('DP','Lunas','Pelunasan','Angsuran','Cicilan')),
  amount INTEGER NOT NULL,
  closing_date TEXT,
  ec_name TEXT,
  notes TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  FOREIGN KEY(client_id) REFERENCES clients(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS product_payments (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  product_id INTEGER NOT NULL,
  payment_date TEXT NOT NULL,
  amount INTEGER NOT NULL,
  status TEXT CHECK(status IN ('DP','Pelunasan','Angsuran','Cicilan','Lunas')),
  method TEXT,
  notes TEXT,
  FOREIGN KEY(product_id) REFERENCES products(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_clients_phone ON clients(phone);
CREATE INDEX IF NOT EXISTS idx_products_client ON products(client_id);
CREATE INDEX IF NOT EXISTS idx_payments_product ON product_payments(product_id);
`);

module.exports = db;

