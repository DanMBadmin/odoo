# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.http import request


class IcountController(http.Controller):
    _payment_route = '/payment/icount/pay'

    @http.route(_payment_route, type='jsonrpc', auth='public')
    def icount_pay(self, reference, card_number, exp_month, exp_year, cvv, holder_name):
        tx_sudo = request.env['payment.transaction'].sudo().search([
            ('reference', '=', reference),
            ('provider_code', '=', 'icount'),
        ])
        if tx_sudo:
            tx_sudo._icount_process_payment({
                'card_number': card_number,
                'exp_month': exp_month,
                'exp_year': exp_year,
                'cvv': cvv,
                'holder_name': holder_name,
            })
        return True
