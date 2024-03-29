# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Dec 2021

from odoo import models, api


class Attachment(models.Model):
    _inherit = 'ir.attachment'

    @api.multi
    @api.onchange("datas")
    def onchange_datas(self):
        for rec in self:
            rec.name = rec.datas_fname
