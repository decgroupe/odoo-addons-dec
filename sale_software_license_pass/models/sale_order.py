# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2021

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    license_pass_ids = fields.One2many(
        comodel_name='software.license.pass',
        inverse_name='sale_order_id',
        string="Passes",
    )
    license_pass_count = fields.Integer(
        compute='_compute_license_pass_count',
        string="Number of Passes",
    )

    @api.depends("license_pass_ids")
    def _compute_license_pass_count(self):
        for sale in self:
            sale.license_pass_count = len(sale.license_pass_ids)

    def action_view_application_pass(self):
        return self.license_pass_ids.action_view()

    def action_cancel(self):
        result = super(SaleOrder, self).action_cancel()
        # When a sale person cancel a SO, he might not have the rights to write
        # on AP. But we need the system to create an activity on the AP (so
        # 'write' access), hence the `sudo`.
        self.sudo()._activity_cancel_on_application_pass()
        return result

    def _activity_cancel_on_application_pass(self):
        """ If some SO are cancelled, we need to put an activity on their
            generated application passes. We only want one activity to
            be attached.
        """
        for license_pass_id in self.mapped('license_pass_ids'):
            if license_pass_id.state == 'draft':
                license_pass_id.action_cancel()
            else:
                license_pass_id.activity_schedule_with_view(
                    'mail.mail_activity_data_warning',
                    user_id=license_pass_id.user_id.id or self.env.uid,
                    views_or_xmlid='sale_software_license_pass.'
                    'exception_application_pass_sale_cancellation',
                    render_context={
                        'sale_orders': self,
                    }
                )
