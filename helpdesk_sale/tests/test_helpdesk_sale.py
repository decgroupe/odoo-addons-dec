# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2025

from odoo.tests.common import TransactionCase
from odoo import fields


class TestHelpdeskSale(TransactionCase):

    def setUp(self):
        super().setUp()
        self.ticket5 = self.env.ref("helpdesk_mgmt.helpdesk_ticket_5")
        self.ticket6 = self.env.ref("helpdesk_mgmt.helpdesk_ticket_6")
        # references ticket stages
        self.stage_new = self.env.ref(
            "helpdesk_mgmt.helpdesk_ticket_stage_new",
        )
        self.stage_progress = self.env.ref(
            "helpdesk_mgmt.helpdesk_ticket_stage_in_progress",
        )
        self.stage_awaiting = self.env.ref(
            "helpdesk_mgmt.helpdesk_ticket_stage_awaiting",
        )
        self.stage_done = self.env.ref(
            "helpdesk_mgmt.helpdesk_ticket_stage_done",
        )
        self.stage_cancelled = self.env.ref(
            "helpdesk_mgmt.helpdesk_ticket_stage_cancelled",
        )

    def test_01_create_sale_quotation(self):
        self.assertEqual(self.ticket5.stage_id, self.stage_progress)
        so_mapping = self.ticket5.action_create_quotation()
        self.assertEqual(self.ticket5.stage_id, self.stage_done)
        sale_id = self.env["sale.order"].browse(so_mapping[self.ticket5.id])
        self.assertTrue(sale_id.exists())
        self.assertEqual(sale_id.state, "draft")
        self.assertEqual(sale_id.partner_id, self.ticket5.partner_id)
        self.assertEqual(sale_id.origin, self.ticket5.number)
        self.assertEqual(sale_id.date_order, fields.Datetime.today())
        self.assertEqual(
            sale_id.summary, ("Case %s: %s") % (self.ticket5.number, self.ticket5.name)
        )
        self.assertRegex(
            sale_id.message_ids[0].body,
            ("Created from helpdesk ticket.*%s") % (self.ticket5.number),
        )
        self.assertRegex(
            self.ticket5.message_ids[0].body,
            ("New quotation.*%s") % (sale_id.name),
        )
