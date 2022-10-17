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

        if self.product_id:
            warning = {
                'title': _("Warning for %s") % self.product_id.name,
            }

            description = self.product_id.description or _('No internal notes')
            responsible = (
                self.product_id.responsible_id and
                self.product_id.responsible_id.name or
                _('No responsible for this product')
            )

            if self.product_id.state == 'obsolete':
                warning['message'] = _(
                    'Obsolete product!\n '
                    '(This product must not be sold anymore.)\n\n %s'
                ) % (description)
            elif self.product_id.state == 'review':
                warning['message'] = _(
                    'This product needs to be reviewed:\n\n - %s \n\n - '
                    'Please contact "%s"'
                ) % (description, responsible)
            elif self.product_id.state == 'quotation':
                warning['message'] = _(
                    'This product is currently in quotation, prices may '
                    'not be correct:\n\n - %s \n\n - '
                    'You can take contact with "%s"'
                ) % (description, responsible)
            else:
                warning = False

            if warning:
                res = {'warning': warning}
        return res

    @api.model
    def create(self, vals):
        rec = super().create(vals)
        if rec.product_id.state == 'review':
            rec.order_id.with_context(
                mail_activity_noautofollow=True
            ).activity_schedule_with_view(
                'sale_product_warnings.mail_activity_data_review',
                user_id=rec.product_id.responsible_id.id or
                rec.order_id.user_id.id or self.env.uid,
                views_or_xmlid='sale_product_warnings.exception_product_review',
                render_context={
                    'product_id':
                        rec.product_id,
                    'product_state':
                        dict(
                            rec.product_id._fields['state'].
                            _description_selection(self.env)
                        ).get(rec.product_id.state),
                    'order_id':
                        rec.order_id,
                    'order_state':
                        dict(
                            rec.order_id._fields['state'].
                            _description_selection(self.env)
                        ).get(rec.order_id.state),
                }
            )
        return rec

    @api.multi
    def _write(self, vals):
        # Note that we need to override internal `_write` since related
        # fields bypass the common `write` function
        check_warn = (vals.get('state') == 'sale')
        res = super()._write(vals)
        if check_warn:
            self.mapped('product_id')._check_warn('block_confirm')
        return res
