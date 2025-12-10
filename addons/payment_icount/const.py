# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.addons.payment.const import SENSITIVE_KEYS as PAYMENT_SENSITIVE_KEYS

SENSITIVE_KEYS = {
    'sid', 'cid', 'user', 'pass', 'cc_number', 'cc_cvv', 'cc_validity', 'authorization', 'token',
}
PAYMENT_SENSITIVE_KEYS.update(SENSITIVE_KEYS)

API_BASE_URL = 'https://api.icount.co.il/api/v3.php/'
DEFAULT_PAYMENT_METHOD_CODES = {'card'}
