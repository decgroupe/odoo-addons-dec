# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2023

from odoo.tests.common import TransactionCase


class TestMailActivityTeamOnly(TransactionCase):
    def setUp(self):
        super().setUp()
        self.partner = self.env.ref("base.res_partner_address_15")

    def _create_activity(self, **act_values):
        activity = self.partner.activity_schedule(
            act_type_xmlid="mail.mail_activity_data_todo",
            summary="summary",
            note="note",
            **act_values,
        )
        return activity

    def test_01_force_no_user(self):
        activity = self._create_activity(user_id=False)
        self.assertFalse(activity.user_id)

    def test_02_fallback_to_default(self):
        # if `user_id` not forced to False, then we fallback to default mode
        activity = self._create_activity()
        self.assertTrue(activity.user_id)
