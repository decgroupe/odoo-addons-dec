# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2025

from odoo.tests import Form
from odoo.tests.common import TransactionCase


class TestHelpdeskReferences(TransactionCase):
    def setUp(self):
        super().setUp()
        self.ticket5 = self.env.ref("helpdesk_mgmt.helpdesk_ticket_5")
        self.ticket6 = self.env.ref("helpdesk_mgmt.helpdesk_ticket_6")

    def test_01_referencing_another_ticket(self):
        with Form(self.ticket6) as t6_form:
            with t6_form.reference_ids.new() as ref1:
                ref1.model_ref_id = f"{self.ticket5._name},{self.ticket5.id}"
        self.assertEqual(len(self.ticket6.reference_ids), 1)
        self.assertEqual(self.ticket6.reference_ids[0].ticket_id, self.ticket6)
        self.assertEqual(self.ticket6.reference_ids[0].model_ref_id, self.ticket5)
