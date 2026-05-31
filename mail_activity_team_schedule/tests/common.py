# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2026

from odoo import Command, fields
from odoo.tests.common import TransactionCase


class TestMailActivityTeamScheduleCommon(TransactionCase):
    """Common fixtures for mail_activity_team_schedule tests."""

    @classmethod
    def setUpClass(cls):
        """Set up reusable records for team schedule tests."""
        super().setUpClass()
        cls.MailActivity = cls.env["mail.activity"]
        cls.MailActivityTeam = cls.env["mail.activity.team"]
        cls.ResModel = cls.env["ir.model"]
        cls.res_partner_model = cls.ResModel._get("res.partner")
        cls.user_partner = cls.env.user.partner_id
        cls.activity_type = cls.env.ref("mail.mail_activity_data_call")
        cls.activity_team = cls.MailActivityTeam.create(
            {
                "name": "Support Team",
                "member_ids": [Command.link(cls.env.user.id)],
            }
        )

    def _create_activity(self, values=None):
        """Create a mail activity with sensible defaults for assertions."""
        activity_vals = {
            "res_model_id": self.res_partner_model.id,
            "res_id": self.user_partner.id,
            "activity_type_id": self.activity_type.id,
            "summary": "Team schedule test",
            "date_deadline": fields.Date.today(),
            "team_id": self.activity_team.id,
        }
        if values:
            activity_vals.update(values)
        return self.MailActivity.create(activity_vals)
