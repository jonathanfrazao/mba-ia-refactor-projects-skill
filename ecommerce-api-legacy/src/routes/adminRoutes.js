const express = require('express');
const { financialReport } = require('../controllers/reportController');
const { requireAuth } = require('../middlewares/authMiddleware');

const router = express.Router();
router.use(requireAuth);
router.get('/financial-report', financialReport);

module.exports = router;
