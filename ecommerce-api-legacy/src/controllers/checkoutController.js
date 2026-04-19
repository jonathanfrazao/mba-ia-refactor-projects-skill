const { processCheckout } = require('../services/checkoutService');

async function checkout(req, res) {
    const { usr: userName, eml: email, pwd: password, c_id: courseId, card: cardNumber } = req.body;

    if (!userName || !email || !courseId || !cardNumber) {
        return res.status(400).json({ error: 'Bad Request' });
    }

    try {
        const result = await processCheckout({ userName, email, password, courseId, cardNumber });
        res.status(200).json({ msg: 'Sucesso', enrollment_id: result.enrollmentId });
    } catch (err) {
        if (err.message === 'Curso não encontrado') return res.status(404).json({ error: err.message });
        if (err.message === 'Pagamento recusado') return res.status(400).json({ error: err.message });
        res.status(500).json({ error: 'Internal Server Error' });
    }
}

module.exports = { checkout };
