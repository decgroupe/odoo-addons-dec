# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2025

import json

import odoo.tests


class TestHelpdeskPublic(odoo.tests.HttpCase):
    "Test Helpdesk Public API"

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

    def _api_new_ticket(self, data):
        """Create a new ticket using the API."""
        payload = {"params": data}
        response = self.url_open(
            "/api/helpdesk/v1/Ticket/New",
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"},
        )
        self.assertEqual(response.status_code, 200, "API should return 200")
        self.assertIn("result", response.json())
        return response

    def _create_and_get_ticket(self, data):
        """Create a new ticket and return the ticket object."""
        response = self._api_new_ticket(data)
        number = response.json().get("result").get("ticket")
        ticket_id = self.env["helpdesk.ticket"].search([("number", "=", number)])
        self.assertTrue(ticket_id, "Ticket should be created")
        self.assertEqual(len(ticket_id), 1, "Only one ticket should be created")
        return ticket_id

    def test_01a_new_ticket_basic(self):
        # generate some partners without email to test the ticket creation and its
        # internal `_retrieve_partner_from_email` method
        Partner = self.env["res.partner"]
        for i in range(3):
            Partner.create({"name": "partner%d" % i})
        data = {
            "subject": "New Ticket",
            "description": "This is a test ticket from test_01a",
        }
        ticket_id = self._create_and_get_ticket(data)
        self.assertEqual(ticket_id.name, "New Ticket")
        self.assertRegex(ticket_id.description, r"This is a test ticket from test_01a")

    def test_01b_new_ticket_basic(self):
        data = {
            "subject": "New Ticket",
            "description": "This is a test ticket from test_01b",
        }
        ticket_id = self._create_and_get_ticket(data)
        self.assertEqual(ticket_id.name, "New Ticket")
        self.assertRegex(ticket_id.description, r"This is a test ticket from test_01b")

    def test_02_new_ticket_with_channel(self):
        data = {
            "subject": "New Ticket",
            "description": "This is a test ticket from test_02",
            "channel": "Email",
        }
        ticket_id = self._create_and_get_ticket(data)
        self.assertEqual(ticket_id.name, "New Ticket")
        self.assertRegex(ticket_id.description, r"This is a test ticket from test_02")
        self.assertEqual(ticket_id.channel_id.name, "Email")

    def test_03_new_ticket_with_category(self):
        data = {
            "subject": "New Ticket",
            "description": "This is a test ticket from test_03",
            "category": "Software",
        }
        ticket_id = self._create_and_get_ticket(data)
        self.assertEqual(ticket_id.name, "New Ticket")
        self.assertRegex(ticket_id.description, r"This is a test ticket from test_03")
        self.assertEqual(ticket_id.category_id.name, "Software")

    def test_04_new_ticket_with_project(self):
        data = {
            "subject": "New Ticket",
            "description": "This is a test ticket from test_04",
            "project": "Research & Development",
        }
        ticket_id = self._create_and_get_ticket(data)
        self.assertEqual(ticket_id.name, "New Ticket")
        self.assertRegex(ticket_id.description, r"This is a test ticket from test_04")
        self.assertEqual(ticket_id.project_id.name, "Research & Development")

    def test_05_new_ticket_with_project(self):
        data = {
            "subject": "New Ticket",
            "description": "This is a test ticket from test_05",
            "team": "Helpdesk",
        }
        ticket_id = self._create_and_get_ticket(data)
        self.assertEqual(ticket_id.name, "New Ticket")
        self.assertRegex(ticket_id.description, r"This is a test ticket from test_05")
        self.assertEqual(ticket_id.team_id.name, "Helpdesk")

    def test_06_new_ticket_from_partner(self):
        data = {
            "subject": "New Ticket",
            "description": "This is a test ticket from test_06",
            "name": "Thomas Jefferson",
            "email": "potu@worldcompany.com",
        }
        ticket_id = self._create_and_get_ticket(data)
        self.assertEqual(ticket_id.name, "New Ticket")
        self.assertRegex(ticket_id.description, r"This is a test ticket from test_06")
        self.assertEqual(ticket_id.partner_name, "Thomas Jefferson")
        self.assertEqual(ticket_id.partner_email, "potu@worldcompany.com")
        self.assertFalse(ticket_id.partner_id, "Partner should not be set")
        # create a partner
        partner_id = self.env["res.partner"].create(
            {
                "name": "Thomas Jefferson",
                "email": "potu@worldcompany.com",
            }
        )
        # recreate the ticket
        ticket_id = self._create_and_get_ticket(data)
        self.assertEqual(ticket_id.partner_name, "Thomas Jefferson")
        self.assertEqual(ticket_id.partner_email, "potu@worldcompany.com")
        self.assertEqual(ticket_id.partner_id, partner_id, "Partner should be set")
