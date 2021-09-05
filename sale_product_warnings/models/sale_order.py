# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2020

from odoo import api, models, _


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        res = super().product_id_change()

        if self.product_id and self.product_id.state == 'obsolete':
            warning = {
                'title':
                    _("Warning for %s") % self.product_id.name,
                'message':
                    _(
                        'Obsolete product!\n '
                        '(This product must not be sold anymore.)\n\n %s'
                    ) %
                    (self.product_id.description or _('No internal notes'))
            }
            res = {'warning': warning}

        elif self.product_id and self.product_id.state == 'review':
            warning = {
                'title':
                    _("Warning for %s") % self.product_id.name,
                'message':
                    _(
                        'This product needs to be reviewed:\n\n - %s \n\n - '
                        'Please contact "%s"'
                    ) % (
                        self.product_id.description or
                        _('No internal notes'), self.product_id.responsible_id
                        and self.product_id.responsible_id.name or
                        _('No responsible for this product')
                    )
            }
            res = {'warning': warning}

        return res
