# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2026

from odoo.tests import tagged

from odoo.addons.sale_timesheet.tests.common import TestCommonSaleTimesheet


@tagged("-at_install", "post_install")
class TestSaleTimesheetProjectCrmLink(TestCommonSaleTimesheet):
    """Test that creating a project from a sale order properly links the opportunity."""

    @classmethod
    def setUpClass(cls):
        """Set up shared test data: a partner and a CRM opportunity."""
        super().setUpClass()
        cls.opportunity = cls.env["crm.lead"].create(
            {
                "name": "Test Opportunity",
                "partner_id": cls.partner_a.id,
                "type": "opportunity",
            }
        )

    def _create_so(self, partner_id):
        """Create a sale order for the given partner."""
        return (
            self.env["sale.order"]
            .with_context(
                mail_notrack=True,
                mail_create_nolog=True,
            )
            .create(
                {
                    "partner_id": partner_id.id,
                    "partner_invoice_id": partner_id.id,
                    "partner_shipping_id": partner_id.id,
                }
            )
        )

    def test_01_get_create_project_data_with_opportunity(self):
        """Test that _get_create_project_data includes linked_lead_id when an
        opportunity is set on the sale order."""
        sale_order = self._create_so(self.partner_a)
        sale_order.opportunity_id = self.opportunity
        project_data = sale_order._get_create_project_data()
        self.assertIn("linked_lead_id", project_data)
        self.assertEqual(project_data["linked_lead_id"], self.opportunity.id)

    def test_02_get_create_project_data_without_opportunity(self):
        """Test that _get_create_project_data sets linked_lead_id to False when no
        opportunity is linked to the sale order."""
        sale_order = self._create_so(self.partner_a)
        self.assertFalse(sale_order.opportunity_id)
        project_data = sale_order._get_create_project_data()
        self.assertIn("linked_lead_id", project_data)
        self.assertFalse(project_data["linked_lead_id"])

    def test_03_create_project_links_opportunity(self):
        """Test the full flow: when a project is created from a sale order that has an
        opportunity, the project's linked_lead_id is set to that opportunity."""
        sale_order = self._create_so(self.partner_a)
        sale_order.opportunity_id = self.opportunity
        sale_order.action_create_project()
        self.assertTrue(sale_order.project_id)
        self.assertEqual(sale_order.project_id.linked_lead_id, self.opportunity)

    def test_04_create_project_without_opportunity_no_link(self):
        """Test that when no opportunity is set on the sale order, the created project
        has no linked_lead_id."""
        sale_order = self._create_so(self.partner_a)
        self.assertFalse(sale_order.opportunity_id)
        sale_order.action_create_project()
        self.assertTrue(sale_order.project_id)
        self.assertFalse(sale_order.project_id.linked_lead_id)
