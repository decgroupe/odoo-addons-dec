# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, May 2021

from odoo import api, fields, models


class SoftwareLicenseApplication(models.Model):
    _inherit = 'software.license.application'

    portal_published = fields.Boolean(
        'In Portal',
        default=True,
    )

    @api.multi
    def action_portal_publish(self):
        self.ensure_one()
        return self.write({'portal_published': not self.portal_published})
