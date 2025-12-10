# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Payment Provider: iCount',
    'version': '1.0',
    'category': 'Accounting/Payment Providers',
    'sequence': 350,
    'summary': "iCount payment provider with immediate capture, tokenization, and receipt creation.",
    'description': " ",
    'depends': ['payment'],
    'data': [
        'views/payment_provider_views.xml',
        'views/payment_icount_templates.xml',
        'views/payment_templates.xml',
        'data/payment_provider_data.xml',
    ],
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
    'assets': {
        'web.assets_frontend': [
            'payment_icount/static/src/interactions/payment_form.js',
        ],
    },
    'author': 'Odoo S.A.',
    'license': 'LGPL-3',
}
