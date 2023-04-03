# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2021

from odoo import _, api, fields, models


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    def _should_notify_new_ticket(self):
        res = super()._should_notify_new_ticket()
        if not res:
            res = self.env.context.get("contact_ticket", False)
        return res
