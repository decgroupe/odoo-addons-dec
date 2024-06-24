# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jun 2024

from odoo.tests.common import TransactionCase, Form
from odoo.exceptions import ValidationError

from odoo.addons.crm.tests import common as crm_common


class TestCrmLeadToHelpdeskTicket(crm_common.TestCrmCommon):

    def setUp(self):
        super().setUp()

    def _get_lead(self):
        lead_id = self.env.ref("crm.crm_case_10")
        lead_id.description = "This is a design software issue"
        return lead_id

    def _create_wizard(self, lead_id):
        ctx = {
            "active_model": lead_id._name,
            "active_id": lead_id.id,
        }
        wizard_form = Form(self.env["crm.lead.to.helpdesk.ticket"].with_context(ctx))
        wizard_id = wizard_form.save()
        return wizard_id

    def test_01_wizard_action(self):
        lead_id = self.env.ref("crm.crm_case_10")
        action = lead_id.action_convert_to_helpdesk_ticket()
        self.assertEqual(action["name"], "Convert to ticket")

    def test_02_nouser_noteam(self):
        lead_id = self._get_lead()
        wizard_id = self._create_wizard(lead_id)
        with self.assertRaisesRegex(
            ValidationError, r"A user \(or at least a team\) is required!"
        ):
            wizard_id.action_create_ticket()

    def test_03_noemail(self):
        lead_id = self._get_lead()
        lead_id.partner_id.email = False
        lead_id.email_from = False
        wizard_id = self._create_wizard(lead_id)
        wizard_id.partner_email = False
        wizard_id.user_id = self.env.ref("base.user_demo")
        with self.assertRaisesRegex(ValidationError, r"An email is required!"):
            wizard_id.action_create_ticket()

    def test_04_user_noteam(self):
        lead_id = self._get_lead()
        wizard_id = self._create_wizard(lead_id)
        wizard_id.user_id = self.env.ref("base.user_demo")
        wizard_id.action_create_ticket()
        ticket_id = wizard_id.ticket_id
        self.assertTrue(ticket_id.exists())

    def test_05_team_nouser(self):
        lead_id = self._get_lead()
        wizard_id = self._create_wizard(lead_id)
        wizard_id.team_id = self.env.ref("helpdesk_mgmt.helpdesk_team_2")
        wizard_id.action_create_ticket()
        ticket_id = wizard_id.ticket_id
        self.assertTrue(ticket_id.exists())

    def test_06_data(self):
        lead_id = self._get_lead()
        wizard_id = self._create_wizard(lead_id)
        wizard_id.user_id = self.env.ref("base.user_demo")
        wizard_id.action_create_ticket()
        ticket_id = wizard_id.ticket_id
        self.assertEqual(ticket_id.name, lead_id.name)
        self.assertIn(lead_id.description, ticket_id.description)
        self.assertEqual(ticket_id.user_id, lead_id.user_id)
        self.assertEqual(ticket_id.partner_email, lead_id.email_from)
        self.assertEqual(ticket_id.partner_name, lead_id.partner_name)
        self.assertEqual(ticket_id.partner_id, lead_id.partner_id)

    def test_07_data_email_nodescription(self):
        lead_id = self.env.ref("crm.crm_case_8")
        self.assertFalse(lead_id.description)
        wizard_id = self._create_wizard(lead_id)
        wizard_id.team_id = self.env.ref("helpdesk_mgmt.helpdesk_team_2")
        wizard_id.action_create_ticket()
        ticket_id = wizard_id.ticket_id
        self.assertEqual(ticket_id.name, lead_id.name)
        self.assertFalse(ticket_id.user_id)
        self.assertEqual(ticket_id.team_id, wizard_id.team_id)
        self.assertEqual(ticket_id.partner_email, lead_id.email_from)
        self.assertEqual(ticket_id.partner_name, lead_id.partner_name)
        self.assertEqual(ticket_id.partner_id, lead_id.partner_id)
