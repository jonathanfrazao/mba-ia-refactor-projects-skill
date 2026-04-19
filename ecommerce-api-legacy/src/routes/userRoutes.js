const express = require('express');
const { removeUser } = require('../controllers/userController');
const { requireAuth } = require('../middlewares/authMiddleware');

const router = express.Router();
router.delete('/:id', requireAuth, removeUser);

module.exports = router;
