const db = require('./db');

const now = () => new Date().toISOString();

const insertClientStmt = db.prepare(`
  INSERT INTO clients (id, name, phone, email, ad_product, ad_purchase_date, ad_ec_name, ad_payment_note, ad_payment_status, created_at, updated_at)
  VALUES (@id, @name, @phone, @email, @ad_product, @ad_purchase_date, @ad_ec_name, @ad_payment_note, @ad_payment_status, @created_at, @updated_at)
  ON CONFLICT(id) DO UPDATE SET
    name=excluded.name,
    phone=excluded.phone,
    email=excluded.email,
    ad_product=excluded.ad_product,
    ad_purchase_date=excluded.ad_purchase_date,
    ad_ec_name=excluded.ad_ec_name,
    ad_payment_note=excluded.ad_payment_note,
    ad_payment_status=excluded.ad_payment_status,
    updated_at=excluded.updated_at
`);

const findClientStmt = db.prepare(`
  SELECT * FROM clients WHERE id = ? OR phone = ?
`);

const searchClientsStmt = db.prepare(`
  SELECT * FROM clients
  WHERE id LIKE ? OR phone LIKE ? OR name LIKE ?
  ORDER BY updated_at DESC
`);

const insertProductStmt = db.prepare(`
  INSERT INTO products (client_id, unique_code, product_name, status, amount, closing_date, ec_name, notes, created_at, updated_at)
  VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
`);

const listProductsStmt = db.prepare(`
  SELECT *,
    (julianday(closing_date) - julianday(ad_purchase_date)) AS time_to_close_days
  FROM products
  JOIN clients ON clients.id = products.client_id
  WHERE client_id = ?
  ORDER BY closing_date DESC
`);

const insertPaymentStmt = db.prepare(`
  INSERT INTO product_payments (product_id, payment_date, amount, status, method, notes)
  VALUES (?, ?, ?, ?, ?, ?)
`);

const listPaymentsStmt = db.prepare(`
  SELECT * FROM product_payments WHERE product_id = ? ORDER BY payment_date DESC
`);

const getClientWithDetailsStmt = db.prepare(`
  SELECT * FROM clients WHERE id = ? OR phone = ? OR email = ?
`);

const listClientProductsStmt = db.prepare(`
  SELECT p.*, c.ad_purchase_date,
    (julianday(p.closing_date) - julianday(c.ad_purchase_date)) AS time_to_close_days
  FROM products p
  JOIN clients c ON c.id = p.client_id
  WHERE p.client_id = ?
  ORDER BY p.closing_date DESC
`);

const listClientPaymentsStmt = db.prepare(`
  SELECT pp.*, p.product_name
  FROM product_payments pp
  JOIN products p ON p.id = pp.product_id
  WHERE p.client_id = ?
  ORDER BY pp.payment_date DESC
`);

function upsertClient(data) {
  const timestamp = now();
  insertClientStmt.run({
    ...data,
    created_at: data.created_at || timestamp,
    updated_at: timestamp
  });
  return getClientByIdOrPhone(data.id, data.phone);
}

function getClientByIdOrPhone(idOrPhone) {
  return findClientStmt.get(idOrPhone, idOrPhone);
}

function searchClients(term) {
  const needle = `%${term}%`;
  return searchClientsStmt.all(needle, needle, needle);
}

function addProduct(clientId, payload) {
  const timestamp = now();
  const info = insertProductStmt.run(
    clientId,
    payload.unique_code || null,
    payload.product_name,
    payload.status,
    payload.amount,
    payload.closing_date || null,
    payload.ec_name || null,
    payload.notes || null,
    timestamp,
    timestamp
  );
  return info.lastInsertRowid;
}

function getProductsForClient(clientId) {
  return listClientProductsStmt.all(clientId).map((row) => ({
    ...row,
    time_to_close_days: row.time_to_close_days != null ? Number(row.time_to_close_days.toFixed(2)) : null
  }));
}

function addPayment(productId, payload) {
  const info = insertPaymentStmt.run(
    productId,
    payload.payment_date,
    payload.amount,
    payload.status,
    payload.method || null,
    payload.notes || null
  );
  return info.lastInsertRowid;
}

function getPaymentsForProduct(productId) {
  return listPaymentsStmt.all(productId);
}

function getClientFullDetails(identifier) {
  const client = getClientWithDetailsStmt.get(identifier, identifier, identifier);
  if (!client) return null;
  const products = getProductsForClient(client.id);
  const payments = listClientPaymentsStmt.all(client.id);
  return {
    client,
    products,
    payments
  };
}

module.exports = {
  upsertClient,
  getClientByIdOrPhone,
  searchClients,
  addProduct,
  getProductsForClient,
  addPayment,
  getPaymentsForProduct,
  getClientFullDetails
};

