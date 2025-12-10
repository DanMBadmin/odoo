# Part of Odoo. See LICENSE file for full copyright and licensing details.

import os
import requests

from odoo import _
from odoo.exceptions import ValidationError

from . import const


def get_credentials():
    cid = os.getenv('ICOUNT_CID')
    user = os.getenv('ICOUNT_USER')
    password = os.getenv('ICOUNT_PASS')
    if not all([cid, user, password]):
        raise ValidationError(_(
            "Missing iCount credentials. Please set ICOUNT_CID, ICOUNT_USER, and ICOUNT_PASS environment variables."
        ))
    return {'cid': cid, 'user': user, 'pass': password}


def api_post(endpoint, payload, *, timeout=30):
    url = const.API_BASE_URL + endpoint.lstrip('/')
    response = requests.post(url, json=payload, timeout=timeout)
    response.raise_for_status()
    return response.json()
