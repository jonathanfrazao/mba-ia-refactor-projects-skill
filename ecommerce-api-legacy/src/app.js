const express = require('express');
const settings = require('./config/settings');
const { initDb } = require('./database');
const checkoutRoutes = require('./routes/checkoutRoutes');
const adminRoutes = require('./routes/adminRoutes');
const userRoutes = require('./routes/userRoutes');
const { errorHandler } = require('./middlewares/errorHandler');
const logger = require('./middlewares/logger');

const app = express();
app.use(express.json());

app.use('/api', checkoutRoutes);
app.use('/api/admin', adminRoutes);
app.use('/api/users', userRoutes);
app.use(errorHandler);

initDb()
    .then(() => {
        app.listen(settings.port, () => {
            logger.info({ port: settings.port }, 'LMS API running');
        });
    })
    .catch((err) => {
        logger.error({ err: err.message }, 'Failed to initialize database');
        process.exit(1);
    });
