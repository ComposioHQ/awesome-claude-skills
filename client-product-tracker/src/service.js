const repository = require('./repository');

function registerOrUpdateClient(payload) {
  const required = ['id', 'name', 'phone'];
  for (const field of required) {
    if (!payload[field]) {
      throw new Error(`Field ${field} is required`);
    }
  }

  return repository.upsertClient({
    id: payload.id,
    name: payload.name,
    phone: payload.phone,
    email: payload.email || null,
    ad_product: payload.ad_product || null,
    ad_purchase_date: payload.ad_purchase_date || null,
    ad_ec_name: payload.ad_ec_name || null,
    ad_payment_note: payload.ad_payment_note || null,
    ad_payment_status: payload.ad_payment_status || 'unpaid'
  });
}

function searchClient(term) {
  if (!term) {
    throw new Error('Search term is required');
  }
  return repository.searchClients(term);
}

function getClientDetails(identifier) {
  if (!identifier) {
    throw new Error('Identifier is required');
  }
  const details = repository.getClientFullDetails(identifier);
  if (!details) {
    throw new Error('Client not found');
  }
  return details;
}

function recordProduct(clientId, payload) {
  if (!clientId) {
    throw new Error('Client ID is required');
  }
  const client = repository.getClientByIdOrPhone(clientId);
  if (!client) {
    throw new Error('Client not found');
  }
  if (!payload.product_name || !payload.amount || !payload.status) {
    throw new Error('Missing product fields');
  }
  const productId = repository.addProduct(client.id, payload);
  return repository.getProductsForClient(client.id).find((p) => p.id === productId);
}

function recordPayment(productId, payload) {
  if (!productId) {
    throw new Error('Product ID is required');
  }
  if (!payload.payment_date || !payload.amount || !payload.status) {
    throw new Error('Missing payment fields');
  }
  repository.addPayment(productId, payload);
  return repository.getPaymentsForProduct(productId);
}

module.exports = {
  registerOrUpdateClient,
  searchClient,
  getClientDetails,
  recordProduct,
  recordPayment
};

