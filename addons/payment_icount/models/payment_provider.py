# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from odoo.addons.payment.logging import get_payment_logger

from .. import const, utils

_logger = get_payment_logger(__name__, const.SENSITIVE_KEYS)


class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(selection_add=[('icount', 'iCount')], ondelete={'icount': 'set default'})
    icount_timeout = fields.Integer(string="Timeout (s)", default=30)
    icount_document_email = fields.Boolean(string="Email receipt", default=True)

    def _compute_feature_support_fields(self):
        super()._compute_feature_support_fields()
        self.filtered(lambda p: p.code == 'icount').update({
            'support_express_checkout': False,
            'support_manual_capture': False,
            'support_refund': 'partial',
            'support_tokenization': True,
        })

    def _get_default_payment_method_codes(self):
        self.ensure_one()
        if self.code != 'icount':
            return super()._get_default_payment_method_codes()
        return const.DEFAULT_PAYMENT_METHOD_CODES

    # === HELPERS === #

    def _icount_get_session(self):
        self.ensure_one()
        creds = utils.get_credentials()
        payload = {**creds}
        response = utils.api_post('auth/login', payload, timeout=self.icount_timeout)
        if not response.get('status'):
            raise ValidationError(response.get('error_description') or _('iCount authentication failed.'))
        return response.get('sid')
