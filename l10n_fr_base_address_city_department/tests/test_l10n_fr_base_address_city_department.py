# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jan 2026

from odoo.tests import Form, new_test_user
from odoo.tests.common import TransactionCase


class Testl10nFrBaseAddressCityDepartment(TransactionCase):
    def setUp(self):
        super().setUp()
        self.ResCity = self.env["res.city"]
        # create a user with `group_partner_manager` to be able to create/edit cities
        self.user = new_test_user(
            self.env,
            login="internal_user",
            groups="base.group_partner_manager",
            notification_type="email",
        )

    def test_01_field_names(self):
        self.assertIn("department_id", self.ResCity._fields)

    def test_02_onchange(self):
        with Form(self.ResCity.with_user(self.user)) as city_form:
            city_form.name = "Test City"
            city_form.department_id = self.env.ref(
                "l10n_fr_department.res_country_department_ain"
            )
            city = city_form.save()
        self.assertEqual(city.country_id, self.env.ref("base.fr"))
        self.assertEqual(
            city.state_id, self.env.ref("l10n_fr_state.res_country_state_auvergne")
        )
