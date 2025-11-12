#!/usr/bin/env node

const { program } = require('commander');
const { table, getBorderCharacters } = require('table');
const service = require('./service');

function printTable(rows, headers) {
  if (!rows || rows.length === 0) {
    console.log('Tidak ada data.');
    return;
  }
  console.log(
    table([headers, ...rows], {
      border: getBorderCharacters('void'),
      columnDefault: { alignment: 'left' }
    })
  );
}

function formatCurrency(amount) {
  return Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR' }).format(amount);
}

program
  .name('client-product-tracker')
  .description('Aplikasi untuk melacak data client, produk, dan pembayaran.');

program
  .command('client:add')
  .requiredOption('--id <id>', 'ID client')
  .requiredOption('--name <name>', 'Nama client')
  .requiredOption('--phone <phone>', 'Nomor HP client')
  .option('--email <email>', 'Email client')
  .option('--ad-product <product>', 'Produk iklan yang dibeli')
  .option('--ad-date <date>', 'Tanggal pembelian iklan (YYYY-MM-DD)')
  .option('--ad-ec <ec>', 'Nama EC (sales) iklan')
  .option('--ad-note <note>', 'Catatan pembayaran iklan')
  .option('--ad-status <status>', 'Status pembayaran iklan (paid/unpaid)')
  .action((options) => {
    const client = service.registerOrUpdateClient({
      id: options.id,
      name: options.name,
      phone: options.phone,
      email: options.email,
      ad_product: options.adProduct,
      ad_purchase_date: options.adDate,
      ad_ec_name: options.adEc,
      ad_payment_note: options.adNote,
      ad_payment_status: options.adStatus
    });
    console.log('Client tersimpan:', client);
  });

program
  .command('client:search <term>')
  .description('Cari client berdasarkan ID, nomor HP, atau nama')
  .action((term) => {
    const results = service.searchClient(term);
    printTable(
      results.map((client) => [client.id, client.name, client.phone, client.email || '-', client.ad_product || '-', client.ad_payment_status || '-']),
      ['ID', 'Nama', 'No HP', 'Email', 'Produk Iklan', 'Status Iklan']
    );
  });

program
  .command('client:detail <identifier>')
  .description('Tampilkan detail lengkap client')
  .action((identifier) => {
    const { client, products, payments } = service.getClientDetails(identifier);
    console.log('=== DATA CLIENT ===');
    console.table({
      ID: client.id,
      Nama: client.name,
      'Nomor HP': client.phone,
      Email: client.email,
      'Produk Iklan': client.ad_product,
      'Tanggal Pembelian Iklan': client.ad_purchase_date,
      'Nama EC Iklan': client.ad_ec_name,
      'Catatan Pembayaran': client.ad_payment_note,
      'Status Pembayaran': client.ad_payment_status
    });

    console.log('\n=== PRODUK YANG DICLOSING ===');
    printTable(
      products.map((product) => [
        product.id,
        product.product_name,
        formatCurrency(product.amount),
        product.status,
        product.closing_date || '-',
        product.ec_name || '-',
        product.time_to_close_days != null ? `${product.time_to_close_days} hari` : '-'
      ]),
      ['ID', 'Produk', 'Nominal', 'Status', 'Tanggal Closing', 'EC', 'Durasi dari Iklan']
    );

    console.log('\n=== TRACK RECORD PEMBAYARAN ===');
    printTable(
      payments.map((payment) => [
        payment.id,
        payment.product_name,
        payment.payment_date,
        formatCurrency(payment.amount),
        payment.status,
        payment.method || '-',
        payment.notes || '-'
      ]),
      ['ID', 'Produk', 'Tanggal', 'Nominal', 'Status', 'Metode', 'Catatan']
    );
  });

program
  .command('product:add')
  .requiredOption('--client-id <clientId>', 'ID client atau nomor HP')
  .requiredOption('--name <productName>', 'Nama produk')
  .requiredOption('--amount <amount>', 'Total harga', (value) => parseInt(value, 10))
  .requiredOption('--status <status>', 'Status pembayaran (DP/Lunas/Pelunasan/Angsuran/Cicilan)')
  .option('--code <code>', 'Kode unik deal')
  .option('--date <date>', 'Tanggal closing produk (YYYY-MM-DD)')
  .option('--ec <ec>', 'Nama EC yang closing')
  .option('--notes <notes>', 'Catatan tambahan')
  .action((options) => {
    const product = service.recordProduct(options.clientId, {
      product_name: options.name,
      amount: options.amount,
      status: options.status,
      unique_code: options.code,
      closing_date: options.date,
      ec_name: options.ec,
      notes: options.notes
    });
    console.log('Produk tersimpan:', product);
  });

program
  .command('payment:add')
  .requiredOption('--product-id <productId>', 'ID produk')
  .requiredOption('--date <date>', 'Tanggal pembayaran (YYYY-MM-DD)')
  .requiredOption('--amount <amount>', 'Nominal pembayaran', (value) => parseInt(value, 10))
  .requiredOption('--status <status>', 'Status pembayaran (DP/Pelunasan/Angsuran/Cicilan/Lunas)')
  .option('--method <method>', 'Metode pembayaran')
  .option('--notes <notes>', 'Catatan tambahan')
  .action((options) => {
    const payments = service.recordPayment(options.productId, {
      payment_date: options.date,
      amount: options.amount,
      status: options.status,
      method: options.method,
      notes: options.notes
    });
    console.log('Riwayat pembayaran terkini:');
    printTable(
      payments.map((payment) => [
        payment.id,
        payment.payment_date,
        formatCurrency(payment.amount),
        payment.status,
        payment.method || '-',
        payment.notes || '-'
      ]),
      ['ID', 'Tanggal', 'Nominal', 'Status', 'Metode', 'Catatan']
    );
  });

program.parse(process.argv);
