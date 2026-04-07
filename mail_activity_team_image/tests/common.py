# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2026

from odoo.tests.common import TransactionCase


class MailActivityTeamImageCommon(TransactionCase):
    """Common setup for mail_activity_team_image tests."""

    @classmethod
    def setUpClass(cls):
        """Set up shared test data."""
        super().setUpClass()
        cls.team = cls.env["mail.activity.team"].create({"name": "Test Team"})
