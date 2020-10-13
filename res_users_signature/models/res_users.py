# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Oct 2020

from odoo import fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    signature_text = fields.Text(
        string='Text Signature',
        help="This field is only used on reports when the report engine does "
        "not support html rendering",
    )

    def __init__(self, pool, cr):
        """ Override of __init__ to add access rights on notification_email_send
            and alias fields. Access rights are disabled by default, but allowed
            on some specific fields defined in self.SELF_{READ/WRITE}ABLE_FIELDS.
        """
        init_res = super().__init__(pool, cr)
        type(self).SELF_WRITEABLE_FIELDS = list(
            set(self.SELF_WRITEABLE_FIELDS + ['signature_text'])
        )
        return init_res
