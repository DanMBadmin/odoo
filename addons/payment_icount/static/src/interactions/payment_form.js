import { patch } from '@web/core/utils/patch';
import { RPCError } from '@web/core/network/rpc_service';
import { _t } from '@web/core/l10n/translation';

import { PaymentForm } from '@payment/interactions/payment_form';

patch(PaymentForm.prototype, {
    async _prepareInlineForm(providerId, providerCode, paymentOptionId, paymentMethodCode, flow) {
        if (providerCode !== 'icount') {
            await super._prepareInlineForm(...arguments);
            return;
        }
        this._setPaymentFlow('direct');
    },

    async _processDirectFlow(providerCode, paymentOptionId, paymentMethodCode, processingValues) {
        if (providerCode !== 'icount') {
            await super._processDirectFlow(...arguments);
            return;
        }

        const container = document.querySelector(`#o_payment_icount_inline_${paymentOptionId}`);
        if (!container) {
            this._displayErrorDialog(_t('Payment processing failed'), _t('Payment form not found.'));
            this._enableButton();
            return;
        }

        const cardNumber = container.querySelector('[name="icount_card_number"]').value;
        const expMonth = container.querySelector('[name="icount_exp_month"]').value;
        const expYear = container.querySelector('[name="icount_exp_year"]').value;
        const cvv = container.querySelector('[name="icount_cvv"]').value;
        const holderName = container.querySelector('[name="icount_holder_name"]').value;
        if (!cardNumber || !expMonth || !expYear || !cvv || !holderName) {
            this._displayErrorDialog(_t('Payment processing failed'), _t('Please complete all card details.'));
            this._enableButton();
            return;
        }

        try {
            await this.waitFor(this.rpc('/payment/icount/pay', {
                reference: processingValues.reference,
                card_number: cardNumber,
                exp_month: expMonth,
                exp_year: expYear,
                cvv: cvv,
                holder_name: holderName,
            }));
            window.location = '/payment/status';
        } catch (error) {
            if (error instanceof RPCError) {
                this._displayErrorDialog(_t('Payment processing failed'), error.data.message);
                this._enableButton();
            } else {
                throw error;
            }
        }
    },
});
