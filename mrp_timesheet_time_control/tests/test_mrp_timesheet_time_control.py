# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2023

from freezegun import freeze_time

from odoo import fields
from odoo.tests import Form

from odoo.addons.mrp_timesheet.tests.common import TestMrpTimesheetBase


class TestMrpTimesheetTimeControl(TestMrpTimesheetBase):
    """Tests for MRP Timesheet Timecontrol module."""

    def setUp(self):
        super().setUp()
        self.production_user.groups_id |= self.env.ref(
            "hr_timesheet.group_hr_timesheet_user"
        )

    @freeze_time("2020-11-25 10:30:00")
    def test_01_entry_datetime(self):
        prod1_id = self.production_model.with_user(self.production_user).create(
            {
                "name": "WH/MO/TEST_01A",
                "product_id": self.product1.id,
                "product_uom_id": self.product1.uom_id.id,
                "allow_timesheets": True,
            }
        )
        # create a timesheet entry with only `date_time` set, the date should be the
        # one of `date_time` and `date_time_end` should be `date_time + unit_amount`
        with Form(
            prod1_id, view="mrp_timesheet_time_control.mrp_production_form_view"
        ) as prod_form:
            with prod_form.timesheet_ids.new() as al_form:
                self.assertEqual(
                    al_form.date_time,
                    fields.Datetime.from_string("2020-11-25 10:30:00"),
                )
                al_form.unit_amount = 2
                al_form.name = "My first entry"

        self.assertEqual(len(prod1_id.timesheet_ids), 1)
        self.assertEqual(
            prod1_id.timesheet_ids.date, fields.Date.from_string("2020-11-25")
        )
        self.assertEqual(
            prod1_id.timesheet_ids.date_time_end,
            fields.Datetime.from_string("2020-11-25 12:30:00"),
        )
