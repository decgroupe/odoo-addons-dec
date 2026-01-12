# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2025

import logging
from contextlib import contextmanager
from unittest.mock import patch

from odoo.tests.common import TransactionCase

_test_logger = logging.getLogger("odoo.tests")


class TestHelpdeskNotify(TransactionCase):
    """Test helpdesk notify functionalities"""

    @contextmanager
    def patch_mail_unlink(self):
        """ """
        _origin = type(self.Mail).unlink

        def _disabled_unlink(self):
            _test_logger.warning("Unlink disabled for `mail.mail`")

        with patch.object(type(self.Mail), "unlink", _disabled_unlink):
            yield

    def _get_ticket_data(self, name, assign_team=False, assign_user=False):
        res = {
            "name": f"{name} Ticket",
            "description": f"{name} Description",
        }
        if assign_team:
            res["team_id"] = self.team_localization.id
        if assign_user:
            res["user_id"] = self.user_marc.id
        return res

    def setUp(self):
        super().setUp()
        # Create company default alias domain (replacing `mail.catchall.domain` param)
        # needed otherwise an error will be raised when creating a ticket:
        #   AssertionError: Malformed 'Return-Path' or 'From' address:
        #   'general-alias-for-tickets' - It should contain one valid plain ASCII email
        self.env["mail.alias.domain"].create(
            {
                "name": "yourcompany.com",
                "bounce_alias": "bounce",
                "catchall_alias": "catchall",
            }
        )
        self.Mail = self.env["mail.mail"]
        self.Ticket = self.env["helpdesk.ticket"]
        self.user_admin = self.env.ref("base.user_admin")
        self.user_marc = self.env.ref("base.user_demo")
        # this team only contains the user_marc
        self.team_localization = self.env.ref("helpdesk_mgmt.helpdesk_team_1")

    def test_01_create_ticket_without_notification(self):
        with self.patch_mail_unlink():
            mail_ids = self.env["mail.mail"].search([])
            ticked_id = self.Ticket.create(
                self._get_ticket_data("test_01"),
            )
            self.assertTrue(ticked_id, "Ticket should be created")
            mail_id = self.env["mail.mail"].search([]) - mail_ids
            self.assertFalse(mail_id, "No mail should be created if no team is set")
            ticked_id = self.Ticket.create(
                self._get_ticket_data("test_01", assign_team=True),
            )
            self.assertTrue(ticked_id, "Ticket should be created")
            mail_id = self.env["mail.mail"].search([]) - mail_ids
            self.assertFalse(
                mail_id,
                "No mail should be created if notify is not "
                "enforced via a context key",
            )

    def _test_ticket_notify(self, ticket_model_with_context, name):
        with self.patch_mail_unlink():
            Ticket = ticket_model_with_context
            mail_ids = self.env["mail.mail"].search([])
            ticked_id = Ticket.create(self._get_ticket_data(name))
            self.assertTrue(ticked_id, "Ticket should be created")
            mail_id = self.env["mail.mail"].search([]) - mail_ids
            self.assertFalse(mail_id, "No mail should be created if no team is set")
            ticked_id = Ticket.create(self._get_ticket_data(name, assign_team=True))
            self.assertTrue(ticked_id, "Ticket should be created")
            mail_id = self.env["mail.mail"].search([]) - mail_ids
            self.assertEqual(len(mail_id), 1, "One mail should be created")
            self.assertRegex(
                mail_id.subject, f"The ticket {ticked_id.number} has been created"
            )
            self.assertRegex(
                mail_id.body, f"A new ticket « {name} Ticket » has been created"
            )
            self.assertRegex(
                mail_id.body, "Someone from your team should assign himself to it"
            )
            self.assertRegex(mail_id.body, f"View Ticket {ticked_id.number}")
            # this time we enforce the assignation of the ticket to a user
            mail_ids = self.env["mail.mail"].search([])
            ticked_id = Ticket.create(
                self._get_ticket_data("name", assign_team=True, assign_user=True),
            )
            self.assertTrue(ticked_id, "Ticket should be created")
            mail_id = self.env["mail.mail"].search([]) - mail_ids
            self.assertFalse(mail_id, "No mail should be created if user is set")
            self.assertEqual(ticked_id.user_id, self.user_marc)
            self.assertEqual(ticked_id.team_id, self.team_localization)

    def test_02_notify_create_ticket_from_fetchmail(self):
        self._test_ticket_notify(
            self.Ticket.with_context(fetchmail_cron_running=True), "test_02"
        )

    def test_03_force_notify_create_ticket(self):
        self._test_ticket_notify(
            self.Ticket.with_context(force_helpdesk_notify=True), "test_03"
        )

    def test_04_notify_create_ticket_from_portal(self):
        self._test_ticket_notify(
            self.Ticket.with_context(portal_ticket=True), "test_04"
        )
