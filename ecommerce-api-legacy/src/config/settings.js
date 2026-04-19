require('dotenv').config();

module.exports = {
    port: parseInt(process.env.PORT) || 3000,
    dbPath: process.env.DB_PATH || './data/app.db',
    paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY,
    adminToken: process.env.ADMIN_TOKEN || 'dev-token',
    logLevel: process.env.LOG_LEVEL || 'info',
};
