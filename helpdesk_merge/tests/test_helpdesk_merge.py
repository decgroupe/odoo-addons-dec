# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2023

from odoo.tests.common import TransactionCase


class TestHelpdeskMerge(TransactionCase):
    """ """

    def setUp(self):
        super().setUp()
        self.ticket_model = self.env["helpdesk.ticket"]
        self.merge_ticket_wizard_model = self.env["merge.helpdesk.ticket.wizard"]
        self.group_do_merge = self.env.ref("helpdesk_merge.res_group_do_merge")

    def test_01_merge(self):
        # get a first ticket reference
        ticket_ht4 = self.ticket_model.search([("number", "=", "HT00004")])
        # keep current data for future comparison
        ticket_ht4_data = ticket_ht4.read()[0]
        # get another ticket reference that will be merged in to the first one
        ticket_ht7 = self.ticket_model.search([("number", "=", "HT00007")])
        # edit some values
        ticket_ht7.write(
            {
                "partner_email": "mrbob@bob.com",
            }
        )
        # keep current data for future comparison
        ticket_ht7_data = ticket_ht7.read()[0]
        wizard_id = self.merge_ticket_wizard_model.create(
            {
                "object_ids": (ticket_ht4 + ticket_ht7).ids,
                "dst_object_id": ticket_ht4.id,
            }
        )
        wizard_id.action_merge()
        self.assertTrue(ticket_ht4.exists())
        self.assertFalse(ticket_ht7.exists())
        ticket_ht4_new_data = ticket_ht4.read()[0]
        self.assertEqual(
            ticket_ht4_new_data["partner_id"], ticket_ht4_data["partner_id"]
        )
        self.assertEqual(
            ticket_ht4_new_data["partner_id"], ticket_ht4_data["partner_id"]
        )
        self.assertEqual(ticket_ht4_new_data["stage_id"], ticket_ht4_data["stage_id"])
        self.assertEqual(ticket_ht4_new_data["tag_ids"], ticket_ht7_data["tag_ids"])
        self.assertEqual(
            ticket_ht4_new_data["description"], ticket_ht4_data["description"]
        )
        self.assertEqual(ticket_ht4_new_data["partner_email"], "mrbob@bob.com")
        self.assertEqual(
            set(ticket_ht4_new_data["message_ids"]),
            set(ticket_ht4_data["message_ids"] + ticket_ht7_data["message_ids"]),
        )