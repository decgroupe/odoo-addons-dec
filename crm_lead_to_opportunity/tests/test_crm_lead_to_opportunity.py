# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jan 2025

from odoo.tests import Form
from odoo.tests.common import users

from odoo.addons.crm.tests import common as crm_common


class TestCrmLeadToOpportunity(crm_common.TestLeadConvertCommon):
    def setUp(self):
        super().setUp()

    @users("user_sales_manager")
    def test_01_lead_to_opportunity(self):
        wizard = Form(
            self.env["crm.lead2opportunity.partner"].with_context(
                **{
                    "active_model": "crm.lead",
                    "active_id": self.lead_1.id,
                    "active_ids": self.lead_1.ids,
                }
            )
        )
        self.assertEqual(wizard.user_id, self.user_sales_manager)
