# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2023

from odoo.tests.common import TransactionCase
from odoo.tests.common import Form


class TestCrmLeadPartnerLocation(TransactionCase):
    def setUp(self):
        super().setUp()
        self.partner_id = self.env.ref("base.res_partner_2")
        # add a delivery contact
        self.partner_shipping_id = self.env["res.partner"].create(
            {
                "name": "Delivery Contact",
                "type": "delivery",
                "parent_id": self.partner_id.id,
            }
        )

    def _create_lead_with_form(self, form_xmlid=False):
        # use specific view
        if form_xmlid:
            view_id = self.env.ref(form_xmlid).id
        else:
            view_id = False
        crm_form = Form(self.env["crm.lead"].with_context({}), view=view_id)
        crm_form.partner_id = self.partner_id
        lead_id = crm_form.save()
        return lead_id

    def test_01_shipping_address_with_standard_form(self):
        lead_id = self._create_lead_with_form()
        self.assertEqual(lead_id.partner_id, self.partner_id)
        self.assertEqual(lead_id.partner_shipping_id, self.partner_shipping_id)

    def test_02_shipping_address_with_quick_form(self):
        lead_id = self._create_lead_with_form("crm.quick_create_opportunity_form")
        self.assertEqual(lead_id.partner_id, self.partner_id)
        self.assertEqual(lead_id.partner_shipping_id, self.partner_shipping_id)
