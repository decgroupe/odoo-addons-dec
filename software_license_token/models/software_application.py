# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2021

from Crypto.PublicKey import RSA
from odoo import api, fields, models


class SoftwareApplication(models.Model):
    _inherit = 'software.application'

    private_key = fields.Text()
    public_key = fields.Text()

    @api.multi
    def action_generate_rsa_keypair(self):
        for rec in self:
            key = RSA.generate(2048)
            rec.private_key = key.export_key()
            rec.public_key = key.publickey().export_key()
