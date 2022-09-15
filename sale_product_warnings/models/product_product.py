# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2022

from odoo import api, models, _
from odoo.exceptions import ValidationError


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.multi
    def _check_warn(self, warn_type):
        msg = False
        for rec in self.filtered(lambda x: x.sale_line_warn == warn_type):
            if not msg:
                msg = [_("Following products are blocking!")]
            msg += ['', '- %s' % (rec.name_get()[0][1], )]
            msg += [rec.sale_line_warn_msg]
        if msg:
            raise ValidationError('\n'.join(msg))
