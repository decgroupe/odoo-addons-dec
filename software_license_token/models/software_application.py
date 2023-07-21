# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2021

from Crypto.PublicKey import RSA

from odoo import fields, models


class SoftwareApplication(models.Model):
    _inherit = "software.application"

    private_key = fields.Text()
    public_key = fields.Text()

    def action_generate_rsa_keypair(self):
        for rec in self:
            key = RSA.generate(2048)
            rec.private_key = key.export_key()
            rec.public_key = key.publickey().export_key()

    def write(self, vals):
        if "type" in vals:
            if vals.get("type") != "inhouse":
                vals.update(
                    {
                        "private_key": False,
                        "public_key": False,
                    }
                )
        return super().write(vals)
