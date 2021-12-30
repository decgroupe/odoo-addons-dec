# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Dec 2021

import logging

from odoo import api, models, _

_logger = logging.getLogger(__name__)


class MailMessage(models.AbstractModel):
    _inherit = 'mail.message'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            self._autoadd_record_name(vals)
        return super().create(vals_list)

    def _autoadd_record_name(self, vals):
        # Note that there is already a similar implementation in `create` of
        # `odoo/addons/mail/models/mail_message.py` but it doesn't take care
        # if `record_name` was set to False
        if 'default_record_name' in self.env.context:
            return
        if not vals.get('record_name'):
            if vals.get('model') and vals.get('res_id'):
                vals['record_name'] = self._get_record_name(vals)
