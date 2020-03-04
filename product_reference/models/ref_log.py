# Copyright (C) DEC SARL, Inc - All Rights Reserved.
#
# CONFIDENTIAL NOTICE: Unauthorized copying and/or use of this file,
# via any medium is strictly prohibited.
# All information contained herein is, and remains the property of
# DEC SARL and its suppliers, if any.
# The intellectual and technical concepts contained herein are
# proprietary to DEC SARL and its suppliers and may be covered by
# French Law and Foreign Patents, patents in process, and are
# protected by trade secret or copyright law.
# Dissemination of this information or reproduction of this material
# is strictly forbidden unless prior written permission is obtained
# from DEC SARL.
# Written by Yann Papouin <y.papouin@dec-industrie.com>, Mar 2020

import time
import logging

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class ref_log(models.Model):
    """ Reference log for all operations """

    _name = 'ref.log'
    _description = 'Log'
    _rec_name = 'operation'
    _order = 'id desc'

    operation = fields.Text('operation', required=True)
    username = fields.Text('username', required=True)
    localcomputername = fields.Text('localcomputername', required=True)
    localusername = fields.Text('localusername', required=True)
    ipaddress = fields.Text('ipaddress', required=True)
    datetime = fields.Datetime('Modification date', default=fields.Datetime.now)
