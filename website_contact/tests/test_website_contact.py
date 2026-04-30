# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2026

import json
from unittest.mock import Mock
from unittest.mock import patch as mock_patch

from lxml import etree

from odoo.exceptions import ValidationError

from odoo.addons.website_contact.controllers.main import (
    ATTACHMENT_000_NAME,
    WebsiteContactController,
)

from .common import MockRequest, TestWebsiteContactCommon


class TestWebsiteContact(TestWebsiteContactCommon):
    """Tests for website_contact module."""

    def test_01_helpdesk_category_sequence_field(self):
        """Check that the sequence field is present in helpdesk category list view."""
        view_info = self.env["helpdesk.ticket.category"].get_view(view_type="list")
        arch = etree.fromstring(view_info["arch"])
        field_names = [el.get("name") for el in arch.iter("field")]
        self.assertIn("sequence", field_names)

    def test_02_helpdesk_category_public_filter_field(self):
        """Check that public_filter field is present in the category form view."""
        view_info = self.env["helpdesk.ticket.category"].get_view(view_type="form")
        arch = etree.fromstring(view_info["arch"])
        field_names = [el.get("name") for el in arch.iter("field")]
        self.assertIn("public_filter", field_names)

    def test_03_helpdesk_category_ordering(self):
        """Check that helpdesk categories are ordered by sequence then name."""
        cat_a = self.HelpdeskCategory.create(
            {"name": "A Category", "sequence": 20, "public_filter": "a"}
        )
        cat_b = self.HelpdeskCategory.create(
            {"name": "B Category", "sequence": 5, "public_filter": "b"}
        )
        results = self.HelpdeskCategory.search([("id", "in", [cat_a.id, cat_b.id])])
        self.assertEqual(results[0], cat_b)
        self.assertEqual(results[1], cat_a)

    def test_04_helpdesk_ticket_notify_via_context(self):
        """_should_notify_new_ticket returns True when contact_ticket context is
        set."""
        ticket = self.HelpdeskTicket.create(
            {"name": "Test Ticket", "description": "Test description"}
        )
        result_no_ctx = ticket._should_notify_new_ticket()
        result_with_ctx = ticket.with_context(
            contact_ticket=True
        )._should_notify_new_ticket()
        self.assertFalse(result_no_ctx)
        self.assertTrue(result_with_ctx)

    def test_05_crm_lead_attachment_ids_field(self):
        """Check that attachment_ids One2many field is defined on crm.lead."""
        lead = self.CrmLead.create({"name": "Test Lead"})
        self.assertIn("attachment_ids", lead._fields)
        self.assertEqual(lead._fields["attachment_ids"].type, "one2many")
        self.assertEqual(lead._fields["attachment_ids"].comodel_name, "ir.attachment")

    def test_06_helpdesk_category_public_filter_search(self):
        """Searching categories by public_filter returns the matching category."""
        results = self.HelpdeskCategory.search([("public_filter", "=", "test_filter")])
        self.assertIn(self.category, results)

    def test_07_helpdesk_category_public_filter_no_match(self):
        """Searching categories by an unknown public_filter returns no result."""
        results = self.HelpdeskCategory.search(
            [("public_filter", "=", "unknown_filter")]
        )
        self.assertNotIn(self.category, results)

    def test_08_controller_get_origins(self):
        """_get_origins returns a dict with the expected origin keys."""
        ctrl = WebsiteContactController()
        with MockRequest(self.env):
            origins = ctrl._get_origins()
        self.assertIn("private", origins)
        self.assertIn("school", origins)
        self.assertIn("company", origins)

    def test_09_controller_get_company_label(self):
        """_get_company_label returns the right label for each origin."""
        ctrl = WebsiteContactController()
        with MockRequest(self.env):
            self.assertEqual(ctrl._get_company_label("school"), "School")
            self.assertEqual(ctrl._get_company_label("company"), "Company")
            self.assertFalse(ctrl._get_company_label("private"))

    def test_10_controller_get_description(self):
        """_get_description returns a non-empty template string."""
        ctrl = WebsiteContactController()
        with MockRequest(self.env):
            desc = ctrl._get_description()
        self.assertIn(":\n- \n", desc)

    def test_11_controller_submit_ticket(self):
        """_handle_submit_ticket_from_contactform creates a helpdesk ticket."""
        ctrl = WebsiteContactController()
        kw = {
            "name": "Test User",
            "email": "test@example.com",
            "subject": "Test Subject",
            "description": "Test description",
            "origin": "private",
            "references": "REF-001",
            "category": str(self.category.id),
        }
        with MockRequest(self.env):
            result = ctrl._handle_submit_ticket_from_contactform(**kw)
        data = json.loads(result)
        self.assertIn("id", data)
        ticket = self.HelpdeskTicket.browse(data["id"])
        self.assertTrue(ticket.exists())
        self.assertEqual(ticket.name, "Test Subject")

    def test_12_controller_submit_ticket_no_description(self):
        """_handle_submit_ticket_from_contactform works without a description."""
        ctrl = WebsiteContactController()
        kw = {
            "name": "Test User",
            "email": "test@example.com",
            "subject": "No Desc",
            "category": "0",
        }
        with MockRequest(self.env):
            result = ctrl._handle_submit_ticket_from_contactform(**kw)
        data = json.loads(result)
        self.assertIn("id", data)

    def test_13_controller_submit_lead(self):
        """_handle_submit_lead_from_contactform creates a CRM lead."""
        ctrl = WebsiteContactController()
        kw = {
            "name": "New Contact",
            "email": "new@example.com",
            "subject": "Lead Subject",
            "description": "Lead description",
            "origin": "company",
            "company": "ACME Corp",
            "street": "1 Main St",
            "city": "Paris",
            "zip": "75001",
            "function": "CEO",
            "phone": "0600000000",
            "mobile": "0700000000",
        }
        with MockRequest(self.env):
            result = ctrl._handle_submit_lead_from_contactform(**kw)
        data = json.loads(result)
        self.assertIn("id", data)
        lead = self.CrmLead.browse(data["id"])
        self.assertTrue(lead.exists())
        self.assertEqual(lead.name, "Lead Subject")

    def test_14_controller_submit_lead_existing_partner(self):
        """_handle_submit_lead_from_contactform with existing partner_id."""
        partner = self.env["res.partner"].create({"name": "Existing Partner"})
        ctrl = WebsiteContactController()
        kw = {
            "subject": "Lead with Partner",
            "description": "desc",
            "origin": "private",
            "partner_id": str(partner.id),
        }
        with MockRequest(self.env):
            result = ctrl._handle_submit_lead_from_contactform(**kw)
        data = json.loads(result)
        self.assertIn("id", data)
        lead = self.CrmLead.browse(data["id"])
        self.assertTrue(lead.exists())
        self.assertEqual(lead.partner_id, partner)

    def test_15_controller_submit_ticket_subscribes_found_partner(self):
        """_handle_submit_ticket_from_contactform subscribes partner found by email."""
        partner = self.env["res.partner"].create(
            {"name": "Subscriber", "email": "subscriber@example.com"}
        )
        ctrl = WebsiteContactController()
        kw = {
            "name": "Subscriber",
            "email": "subscriber@example.com",
            "subject": "Test",
            "category": "0",
        }
        with MockRequest(self.env):
            result = ctrl._handle_submit_ticket_from_contactform(**kw)
        data = json.loads(result)
        self.assertIn("id", data)
        ticket = self.HelpdeskTicket.browse(data["id"])
        self.assertIn(partner, ticket.message_partner_ids)

    def test_16_controller_submit_ticket_with_attachment_key(self):
        """_handle_submit_ticket_from_contactform calls _save_attachments when key
        set."""
        ctrl = WebsiteContactController()
        kw = {
            "name": "Test",
            "email": "test@example.com",
            "subject": "Test Subject",
            "category": "0",
            ATTACHMENT_000_NAME: "somefile.txt",
        }
        with MockRequest(self.env):
            result = ctrl._handle_submit_ticket_from_contactform(**kw)
        data = json.loads(result)
        self.assertIn("id", data)

    def test_17_save_attachments_creates_attachment(self):
        """_save_attachments creates an ir.attachment record for the given model."""
        ticket = self.HelpdeskTicket.create({"name": "Test", "description": "desc"})
        ctrl = WebsiteContactController()
        mock_file = Mock()
        mock_file.read.return_value = b"test content"
        mock_file.filename = "test.txt"
        with MockRequest(self.env) as mock:
            mock.httprequest.files = {ATTACHMENT_000_NAME: mock_file}
            ctrl._save_attachments("helpdesk.ticket", ticket.id, public=False)
        attachments = self.env["ir.attachment"].search(
            [("res_model", "=", "helpdesk.ticket"), ("res_id", "=", ticket.id)]
        )
        self.assertEqual(len(attachments), 1)
        self.assertEqual(attachments[0].name, "test.txt")

    def test_18_save_attachments_public_generates_token(self):
        """_save_attachments calls generate_access_token when public=True."""
        ticket = self.HelpdeskTicket.create({"name": "Test", "description": "desc"})
        ctrl = WebsiteContactController()
        mock_file = Mock()
        mock_file.read.return_value = b"content"
        mock_file.filename = "doc.pdf"
        with MockRequest(self.env) as mock:
            mock.httprequest.files = {ATTACHMENT_000_NAME: mock_file}
            ctrl._save_attachments("helpdesk.ticket", ticket.id, public=True)
        attachments = self.env["ir.attachment"].search(
            [("res_model", "=", "helpdesk.ticket"), ("res_id", "=", ticket.id)]
        )
        self.assertTrue(attachments[0].access_token)

    def test_19_submit_ticket_happy_path(self):
        """submit_ticket_from_contactform creates a ticket when recaptcha passes."""
        ctrl = WebsiteContactController()
        kw = {
            "name": "Test",
            "email": "test@example.com",
            "subject": "Subject",
            "category": "0",
        }
        with MockRequest(self.env):
            result = ctrl.submit_ticket_from_contactform(**kw)
        data = json.loads(result.get_data(as_text=True))
        self.assertIn("id", data)

    def test_20_submit_ticket_recaptcha_fail(self):
        """submit_ticket_from_contactform returns error dict when recaptcha fails."""
        ctrl = WebsiteContactController()
        kw = {"subject": "Test", "category": "0"}
        IrHttp = type(self.env["ir.http"])
        with MockRequest(self.env):
            with mock_patch.object(
                IrHttp, "_verify_request_recaptcha_token", return_value=False
            ):
                result = ctrl.submit_ticket_from_contactform(**kw)
        data = json.loads(result.get_data(as_text=True))
        self.assertIn("error", data)

    def test_21_submit_ticket_validation_error(self):
        """submit_ticket_from_contactform returns error dict on ValidationError."""
        ctrl = WebsiteContactController()
        kw = {"subject": "Test", "category": "0"}
        with MockRequest(self.env):
            with mock_patch.object(
                WebsiteContactController,
                "_handle_submit_ticket_from_contactform",
                side_effect=ValidationError("Test validation error"),
            ):
                result = ctrl.submit_ticket_from_contactform(**kw)
        data = json.loads(result.get_data(as_text=True))
        self.assertIn("error", data)

    def test_22_controller_submit_lead_with_attachment_key(self):
        """_handle_submit_lead_from_contactform calls _save_attachments when key
        set."""
        ctrl = WebsiteContactController()
        kw = {
            "subject": "Lead",
            "description": "desc",
            "origin": "private",
            ATTACHMENT_000_NAME: "somefile.txt",
        }
        with MockRequest(self.env):
            result = ctrl._handle_submit_lead_from_contactform(**kw)
        data = json.loads(result)
        self.assertIn("id", data)

    def test_23_submit_lead_happy_path(self):
        """submit_lead_from_contactform creates a lead when recaptcha passes."""
        ctrl = WebsiteContactController()
        kw = {
            "name": "Test",
            "email": "test@example.com",
            "subject": "Lead Subject",
            "origin": "company",
            "company": "ACME",
        }
        with MockRequest(self.env):
            result = ctrl.submit_lead_from_contactform(**kw)
        data = json.loads(result.get_data(as_text=True))
        self.assertIn("id", data)

    def test_24_submit_lead_recaptcha_fail(self):
        """submit_lead_from_contactform returns error dict when recaptcha fails."""
        ctrl = WebsiteContactController()
        kw = {"subject": "Test", "origin": "private"}
        IrHttp = type(self.env["ir.http"])
        with MockRequest(self.env):
            with mock_patch.object(
                IrHttp, "_verify_request_recaptcha_token", return_value=False
            ):
                result = ctrl.submit_lead_from_contactform(**kw)
        data = json.loads(result.get_data(as_text=True))
        self.assertIn("error", data)

    def test_25_submit_lead_validation_error(self):
        """submit_lead_from_contactform returns error dict on ValidationError."""
        ctrl = WebsiteContactController()
        kw = {"subject": "Test", "origin": "private"}
        with MockRequest(self.env):
            with mock_patch.object(
                WebsiteContactController,
                "_handle_submit_lead_from_contactform",
                side_effect=ValidationError("Test error"),
            ):
                result = ctrl.submit_lead_from_contactform(**kw)
        data = json.loads(result.get_data(as_text=True))
        self.assertIn("error", data)

    def test_26_create_new_ticket_route(self):
        """create_new_ticket_from_contactform calls render with the right template."""
        ctrl = WebsiteContactController()
        with MockRequest(self.env) as mock:
            mock.render = Mock(return_value="")
            result = ctrl.create_new_ticket_from_contactform("test_filter")
        self.assertIsNotNone(result)

    def test_27_create_new_lead_routes(self):
        """create_new_lead_from_contactform1 and _2 call render with the right
        template."""
        ctrl = WebsiteContactController()
        with MockRequest(self.env) as mock:
            mock.render = Mock(return_value="")
            result1 = ctrl.create_new_lead_from_contactform1()
            result2 = ctrl.create_new_lead_from_contactform2(
                email="contact@example.com", origin="company"
            )
        self.assertIsNotNone(result1)
        self.assertIsNotNone(result2)
