const { getFinancialReport } = require('../services/reportService');
const logger = require('../middlewares/logger');

async function financialReport(req, res) {
    try {
        const report = await getFinancialReport();
        res.json(report);
    } catch (err) {
        logger.error({ err: err.message }, 'Financial report failed');
        res.status(500).json({ error: 'Internal Server Error' });
    }
}

module.exports = { financialReport };
