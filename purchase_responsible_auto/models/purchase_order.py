# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2020

from odoo import models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def _replace_default_user(self):
        """Set or replace the default user (usually root) by the current user to avoid
        confusion and mistakes when printing documents or sending emails"""
        for order in self:
            if (
                not order.user_id
                or order.user_id == self.env.ref("base.user_root")
                or order.user_id == self.env.ref("base.user_admin")
            ):
                order.user_id = self.env.user

    def print_quotation(self):
        self._replace_default_user()
        return super().print_quotation()
