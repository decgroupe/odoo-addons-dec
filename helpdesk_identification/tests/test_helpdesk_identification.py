# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2026

import logging

from odoo.tests.common import TransactionCase

_logger = logging.getLogger(__name__)


class TestHelpdeskTicketIdentification(TransactionCase):
    """Test the helpdesk ticket identification features, especially the display name
    and name_search behavior"""

    def _append_symbol_to_stages(self):
        self.stage_new.name = "💍 " + self.stage_new.name
        self.stage_in_progress.name = "💐 " + self.stage_in_progress.name
        self.stage_awaiting.name = "👰🏻‍ " + self.stage_awaiting.name
        self.stage_done.name = "🤵🏻 " + self.stage_done.name
        self.stage_cancelled.name = "💝 " + self.stage_cancelled.name
        self.stage_rejected.name = "🦋 " + self.stage_rejected.name

    def assertNameSearch(self, record, name, expected_result):
        Model = self.env[record._name]
        Model.invalidate_model(["display_name"])
        res = Model.name_search(name=name)
        if not expected_result:
            self.assertFalse(res)
            return
        try:
            self.assertEqual(res[0][0], record.id)
            self.assertEqual(res[0][1], expected_result)
        except IndexError:
            self.fail(
                f"Expected to find a record with name_search '{name}' "
                f"but found {res}.\n"
                f"Value is '{record.display_name}'"
            )

    def assertDisplayName(self, record, context, normal_name, identification_name):
        Model = self.env[record._name]
        Model.invalidate_model(["display_name"])
        self.assertEqual(record.display_name, normal_name)
        Model.invalidate_model(["display_name"])
        self.assertEqual(
            record.with_context(**context).display_name, identification_name
        )

    def setUp(self):
        super().setUp()
        self.Ticket = self.env["helpdesk.ticket"]

        # tracks stages
        self.stage_new = self.env.ref("helpdesk_mgmt.helpdesk_ticket_stage_new")
        self.stage_in_progress = self.env.ref(
            "helpdesk_mgmt.helpdesk_ticket_stage_in_progress"
        )
        self.stage_awaiting = self.env.ref(
            "helpdesk_mgmt.helpdesk_ticket_stage_awaiting"
        )
        self.stage_done = self.env.ref("helpdesk_mgmt.helpdesk_ticket_stage_done")
        self.stage_cancelled = self.env.ref(
            "helpdesk_mgmt.helpdesk_ticket_stage_cancelled"
        )
        self.stage_rejected = self.env.ref(
            "helpdesk_mgmt.helpdesk_ticket_stage_rejected"
        )
        # Problem with the delivery of goods
        self.ticket_1 = self.env.ref("helpdesk_mgmt.helpdesk_ticket_1")
        # Damaged Products
        self.ticket_2 = self.env.ref("helpdesk_mgmt.helpdesk_ticket_2")
        # Document related problems
        self.ticket_3 = self.env.ref("helpdesk_mgmt.helpdesk_ticket_3")
        # Product quality not maintained
        self.ticket_4 = self.env.ref("helpdesk_mgmt.helpdesk_ticket_4")
        # unset state before assign to `zip_id` to avoid exception from `_check_zip`
        self.ticket_4.partner_id.state_id = False
        self.ticket_4.partner_id.zip_id = self.env.ref(
            "base_location.demo_brussels_zip"
        )
        # Some products missing
        self.ticket_5 = self.env.ref("helpdesk_mgmt.helpdesk_ticket_5")
        # Problem with the delivery of assignments
        self.ticket_6 = self.env.ref("helpdesk_mgmt.helpdesk_ticket_6")
        # Documents unclear
        self.ticket_7 = self.env.ref("helpdesk_mgmt.helpdesk_ticket_7")
        # Product quality not maintained
        self.ticket_8 = self.env.ref("helpdesk_mgmt.helpdesk_ticket_8")

        # enforce numbers for static compare
        self.ticket_1.number = "HT/01"
        self.ticket_2.number = "HT/02"
        self.ticket_3.number = "HT/03"
        self.ticket_4.number = "HT/04"
        self.ticket_5.number = "HT/05"
        self.ticket_6.number = "HT/06"
        self.ticket_7.number = "HT/07"
        self.ticket_8.number = "HT/08"
        self.ticket_ids = (
            self.ticket_1
            + self.ticket_2
            + self.ticket_3
            + self.ticket_4
            + self.ticket_5
            + self.ticket_6
            + self.ticket_7
            + self.ticket_8
        )
        for ticket in self.ticket_ids:
            _logger.debug(
                "Ticket %s display name is \n'%s'",
                ticket.id,
                ticket.with_context(name_search=True).display_name,
            )
        # re-enforce email for test stability as it is edited by crm module
        self.ticket_1.partner_id.email = "gemini_furniture@fake.geminifurniture.com"
        self.ticket_2.partner_id.email = "acme_corp@yourcompany.example.com"
        self.ticket_5.partner_id.email = "azure.Interior24@example.com"

    def test_01_display_name(self):
        self.assertDisplayName(
            self.ticket_1,
            context={"name_search": True},
            normal_name="[HT/01] Problem with the delivery of goods",
            identification_name="[HT/01] Problem with the delivery of goods "
            "→ Helpdesk 🏢 Gemini Furniture "
            "→ (94535 Fairfield) 📧 gemini_furniture@fake.geminifurniture.com",
        )
        self.assertDisplayName(
            self.ticket_1,
            context={
                "name_search": True,
                "idf_no_email": True,
            },
            normal_name="[HT/01] Problem with the delivery of goods",
            identification_name="[HT/01] Problem with the delivery of goods "
            "→ Helpdesk 🏢 Gemini Furniture "
            "→ (94535 Fairfield)",
        )
        self.assertDisplayName(
            self.ticket_1,
            context={
                "name_search": True,
                "idf_no_email": True,
                "idf_no_location": True,
            },
            normal_name="[HT/01] Problem with the delivery of goods",
            identification_name="[HT/01] Problem with the delivery of goods "
            "→ Helpdesk 🏢 Gemini Furniture",
        )
        self._append_symbol_to_stages()
        self.assertDisplayName(
            self.ticket_1,
            context={"name_search": True},
            normal_name="[HT/01] Problem with the delivery of goods",
            identification_name="💍 [HT/01] Problem with the delivery of goods "
            "→ Helpdesk 🏢 Gemini Furniture "
            "→ (94535 Fairfield) 📧 gemini_furniture@fake.geminifurniture.com",
        )

    def test_02_name_search(self):
        self._append_symbol_to_stages()
        # search using code
        self.assertNameSearch(
            self.ticket_1,
            "HT/01",
            "💍 [HT/01] Problem with the delivery of goods "
            "→ Helpdesk 🏢 Gemini Furniture "
            "→ (94535 Fairfield) 📧 gemini_furniture@fake.geminifurniture.com",
        )
        # search using name
        self.assertNameSearch(
            self.ticket_2,
            "Damaged Products",
            "💍 [HT/02] Damaged Products "
            "→ Localization team 🏢 Acme Corporation "
            "→ (94523 Pleasant Hill) 📧 acme_corp@yourcompany.example.com",
        )
        # search using name
        self.assertNameSearch(
            self.ticket_3,
            "Document related problems",
            "💝 [HT/03] Document related problems "
            "→ Localization team 🏢 Lumber Inc "
            "→ (95202 Stockton) 📧 lumber-inv92@example.com",
        )
        # search using code (without brackets) with stage symbol
        self.assertNameSearch(
            self.ticket_4,
            "💐 HT/04",
            "💐 [HT/04] Product quality not maintained "
            "→ Consultants 🏢 The Jackson Group "
            "→ (🗺️ 1000 Brussels, Belgium) 📧 jackson.group82@example.com",
        )
        # search using code (with brackets)
        self.assertNameSearch(
            self.ticket_5,
            "[HT/05]",
            "💐 [HT/05] Some products missing "
            "→ Consultants 🏢 Azure Interior "
            "→ (94538 Fremont) 📧 azure.Interior24@example.com",
        )
        # search using symbol, code and name
        self.assertNameSearch(
            self.ticket_6,
            "👰 [HT/06] Problem with the delivery of assignments",
            "👰 [HT/06] Problem with the delivery of assignments "
            "→ Consultants 🏢 Azure Interior "
            "→ (94538 Fremont) 📧 azure.Interior24@example.com",
        )
        # search using code and partial name
        self.assertNameSearch(
            self.ticket_7,
            "[HT/07] Docu",
            "🤵 [HT/07] Documents unclear "
            "→ Localization team 🏢 Acme Corporation "
            "→ (94523 Pleasant Hill) 📧 acme_corp@yourcompany.example.com",
        )
        # search using partial code and name
        self.assertNameSearch(
            self.ticket_8,
            "08] Prod",
            "💐 [HT/08] Product quality not maintained "
            "→ Consultants 🏢 The Jackson Group "
            "→ (🗺️ 1000 Brussels, Belgium) 📧 jackson.group82@example.com",
        )
