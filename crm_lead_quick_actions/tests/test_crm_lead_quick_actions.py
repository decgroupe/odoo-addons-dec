# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2023

from lxml import etree

from odoo.tests.common import TransactionCase


class TestCrmLeadQuickActions(TransactionCase):
    """Tests for crm_lead_quick_actions module."""

    @classmethod
    def setUpClass(cls):
        """Set up shared test data."""
        super().setUpClass()
        cls.CrmLead = cls.env["crm.lead"]
        cls.Partner = cls.env["res.partner"]

    def test_01_lead_without_partner_can_be_deleted(self):
        """A lead without a partner can be deleted using the unlink action."""
        lead = self.CrmLead.create({"name": "Test Lead", "type": "lead"})
        lead_id = lead.id
        lead.unlink()
        self.assertFalse(self.CrmLead.search([("id", "=", lead_id)]))

    def test_02_lead_with_partner_can_be_deleted(self):
        """A lead with a partner can also be deleted via ORM."""
        partner = self.Partner.create({"name": "Test Partner"})
        lead = self.CrmLead.create(
            {"name": "Test Lead With Partner", "type": "lead", "partner_id": partner.id}
        )
        lead_id = lead.id
        lead.unlink()
        self.assertFalse(self.CrmLead.search([("id", "=", lead_id)]))

    def test_03_view_has_delete_button_with_invisible_modifier(self):
        """The leads list view has a delete button hidden when partner_id is set."""
        view = self.env.ref("crm_lead_quick_actions.crm_case_leads_tree_view")
        arch = etree.fromstring(view.arch_db)
        buttons = arch.xpath("//button[@name='unlink']")
        self.assertTrue(buttons, "no unlink button found in the view arch")
        btn = buttons[0]
        self.assertEqual(btn.get("invisible"), "partner_id != False")
