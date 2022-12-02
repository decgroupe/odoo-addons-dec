# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Nov 2022

import logging

from odoo import api, models, fields
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)


class Partner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def action_clean_with_users(self, days):
        partners_to_delete = self.env["res.partner"]

        domain = [
            (
                "create_date", "<=",
                fields.datetime.today() - timedelta(days=days)
            ),
            ("signup_type", "=", "reset"),
        ]
        inactive_users = self.env["res.users"].search(
            domain, order="create_date"
        )

        # `login_date` is non-stored relative field that cannot be used
        # directly as a domain filter
        for user_id in inactive_users.filtered(lambda x: x.login_date is False):
            _logger.info(
                "%s %s %s %s %s %s %s", user_id, user_id.create_date,
                user_id.create_uid, user_id.login_date, user_id.name,
                user_id.login, user_id.signup_type
            )
            if user_id.partner_id:
                if user_id.partner_id.create_uid.id > 1:
                    # Ignore when contact was created manually by an employee
                    pass
                if user_id.partner_id.meeting_count > 0:
                    # Ignore when contact has already been planned to a meeting
                    pass
                elif user_id.partner_id.phonecall_count > 0:
                    # Ignore when contact is already mapped to a phonecall
                    pass
                elif user_id.partner_id.opportunity_count > 0:
                    # Ignore when contact is already mapped to an opportunity
                    pass
                elif user_id.partner_id.sale_order_count > 0:
                    # Ignore when contact is already mapped to a sale order
                    pass
                elif user_id.partner_id.helpdesk_ticket_count > 0:
                    # Ignore when contact is already mapped to a ticket
                    pass
                elif user_id.partner_id.total_invoiced > 0:
                    # Ignore when contact is already mapped to an invoice
                    pass
                else:
                    partners_to_delete += user_id.partner_id

        if partners_to_delete:
            users_to_delete_raw_ids = partners_to_delete.mapped("user_ids").ids
            for id in users_to_delete_raw_ids:
                user_id = self.env["res.users"].browse(id)
                _logger.info(
                    "Deleting user %s (%s)",
                    user_id.name_get()[0][1], user_id.login
                )
                user_id.unlink()
            partners_to_delete.unlink()
