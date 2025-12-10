# Part of Odoo. See LICENSE file for full copyright and licensing details.

import requests

from odoo import _, api, fields, models

from odoo.addons.payment.logging import get_payment_logger

from .. import const, utils

_logger = get_payment_logger(__name__, const.SENSITIVE_KEYS)


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    icount_confirmation_code = fields.Char(readonly=True)
    icount_document_id = fields.Char(readonly=True)
    icount_token_id = fields.Char(readonly=True)

    def _get_specific_processing_values(self, processing_values):
        if self.provider_code != 'icount':
            return super()._get_specific_processing_values(processing_values)
        return {'reference': self.reference}

    def _icount_process_payment(self, card_details):
        self.ensure_one()
        if self.provider_code != 'icount':
            return

        provider = self.provider_id
        try:
            sid = provider._icount_get_session()
            validity = f"{card_details['exp_year']}-{int(card_details['exp_month']):02d}"
            charge_payload = {
                'sid': sid,
                'sum': self.amount,
                'currency_code': self.currency_id.name,
                'client_name': self.partner_name,
                'email': self.partner_email,
                'cc_number': card_details['card_number'],
                'cc_cvv': card_details['cvv'],
                'cc_validity': validity,
                'cc_holder_name': card_details['holder_name'],
                'payment_description': self.reference,
                'is_test': self.provider_id.state == 'test',
            }
            charge_response = utils.api_post('cc/bill', charge_payload, timeout=provider.icount_timeout)
            if not charge_response.get('status') or not charge_response.get('success'):
                reason = charge_response.get('error_description') or charge_response.get('reason') or _('Payment failed.')
                self._set_error(reason)
                return

            token_payload = {
                'sid': sid,
                'client_name': self.partner_name,
                'email': self.partner_email,
                'cc_number': card_details['card_number'],
                'cc_cvv': card_details['cvv'],
                'cc_validity': validity,
                'cc_holder_name': card_details['holder_name'],
            }
            token_response = utils.api_post('cc_storage/store', token_payload, timeout=provider.icount_timeout)
            if not token_response.get('status'):
                self._set_error(token_response.get('error_description') or _('Unable to tokenize card.'))
                return

            receipt_payload = {
                'sid': sid,
                'doctype': 'receipt',
                'client_name': self.partner_name,
                'email': self.partner_email,
                'tax_exempt': 1,
                'items': [
                    {
                        'description': self.reference,
                        'unitprice': self.amount,
                        'quantity': 1,
                    }
                ],
                'cc': {
                    'sum': self.amount,
                    'num_of_payments': 1,
                    'card_number': str(card_details['card_number'])[-4:],
                    'exp_year': card_details['exp_year'],
                    'exp_month': int(card_details['exp_month']),
                    'holder_id': '',
                    'holder_name': card_details['holder_name'],
                    'confirmation_code': charge_response.get('confirmation_code'),
                },
                'send_email': int(provider.icount_document_email),
                'email_to_client': int(provider.icount_document_email),
            }
            receipt_response = utils.api_post('doc/create', receipt_payload, timeout=provider.icount_timeout)
            if not receipt_response.get('status'):
                self._set_error(receipt_response.get('error_description') or _('Unable to create receipt.'))
                return
        except requests.RequestException as exc:
            _logger.error('iCount communication failed: %s', exc)
            self._set_error(_('Unable to reach iCount. Please try again.'))
            return
        except Exception as exc:
            _logger.error('Unexpected iCount error: %s', exc)
            self._set_error(_('Payment failed.'))
            return

        payment_data = {
            'reference': self.reference,
            'confirmation_code': charge_response.get('confirmation_code'),
            'cc_token_id': token_response.get('cc_token_id'),
            'card_last4': str(card_details['card_number'])[-4:],
            'exp_month': int(card_details['exp_month']),
            'exp_year': int(card_details['exp_year']),
            'document_id': receipt_response.get('doc_id') or receipt_response.get('id'),
            'status': 'done',
        }
        self.tokenize = True
        tx = self._process('icount', payment_data)
        if tx and not tx.token_id:
            tx._tokenize(payment_data)

    def _apply_updates(self, payment_data):
        if self.provider_code != 'icount':
            return super()._apply_updates(payment_data)

        status = payment_data.get('status')
        if status == 'done':
            self._set_done()
        elif status == 'authorized':
            self._set_authorized()
        elif status == 'cancel':
            self._set_canceled()
        elif status == 'pending':
            self._set_pending()
        else:
            self._set_error(_('Payment failed.'))

        self.write({
            'provider_reference': payment_data.get('confirmation_code') or self.provider_reference,
            'icount_confirmation_code': payment_data.get('confirmation_code'),
            'icount_document_id': payment_data.get('document_id'),
            'icount_token_id': payment_data.get('cc_token_id'),
        })

    def _extract_token_values(self, payment_data):
        if self.provider_code != 'icount':
            return super()._extract_token_values(payment_data)

        token_id = payment_data.get('cc_token_id')
        if not token_id:
            return {}

        return {
            'provider_ref': str(token_id),
            'payment_details': _('Card ending in %(last4)s', last4=payment_data.get('card_last4')),
            'provider_code': 'icount',
            'name': _('iCount card %(last4)s', last4=payment_data.get('card_last4')),
            'exp_month': payment_data.get('exp_month'),
            'exp_year': payment_data.get('exp_year'),
        }
