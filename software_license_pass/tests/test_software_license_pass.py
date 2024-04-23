# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Nov 2023

from datetime import datetime

from dateutil.relativedelta import relativedelta
from freezegun import freeze_time

from odoo import fields
from odoo.exceptions import UserError, ValidationError
from odoo.tests import new_test_user, Form
from odoo.tests.common import TransactionCase


class TestSoftwareLicensePass(TransactionCase):
    def setUp(self):
        super().setUp()
        self.application_model = self.env["software.application"]
        self.software_license = self.env["software.license"]
        self.pack = self.env["software.license.pack"]
        self.pack_line = self.env["software.license.pack.line"]
        self.license_pass = self.env["software.license.pass"]
        # create users
        ctx = {
            "mail_create_nolog": True,
            "mail_create_nosubscribe": True,
            "mail_notrack": True,
            "no_reset_password": True,
        }
        self.pass_user = new_test_user(
            self.env,
            login="pass-user",
            groups="software.group_software_user",
            context=ctx,
        )
        self.pass_manager = new_test_user(
            self.env,
            login="pass-manager",
            groups="software.group_software_manager",
            context=ctx,
        )
        self.pass_supermanager = new_test_user(
            self.env,
            login="pass-supermanager",
            groups="software.group_software_supermanager",
            context=ctx,
        )
        self.REGEX_SERIAL = r"[A-Z0-9]{5}-[A-Z0-9]{5}-[A-Z0-9]{5}-[A-Z0-9]{5}"

    def test_01_add_app_to_pack(self):
        pack_basic = self.env.ref("software_license_pass.sl_pack_basic")
        self.assertEqual(pack_basic.pass_count, 2)
        # add line to basic pack
        line_id = self.pack_line.create(
            {
                "pack_id": pack_basic.id,
                "application_id": self.env.ref("software_application.sa_brickgame").id,
            }
        )
        # there is 2 passes with a license each = 2 x licenses
        current_pass_license_ids = pack_basic.pass_ids.mapped("license_ids")
        self.assertEqual(len(current_pass_license_ids), 2)
        # resync existing pass
        pack_basic.action_resync()
        new_pass_license_ids = pack_basic.pass_ids.mapped("license_ids")
        self.assertEqual(len(new_pass_license_ids), 4)

    def test_02_edit_license_from_pass(self):
        pass_basic1 = self.env.ref("software_license_pass.pass_basic1")
        pass_basic2 = self.env.ref("software_license_pass.pass_basic2")
        license_id = pass_basic1.license_ids[0]

        def try_edit(license_id, field_name, value):
            self.assertIn(field_name, self.software_license.PASS_LOCKED_FIELDS)
            with self.assertRaisesRegex(
                UserError,
                r"It is forbidden to update these license's fields "
                "when owned by a pass.*\n%s" % (field_name,),
            ), self.cr.savepoint():
                license_id.write({field_name: value})

        self.assertEqual(len(self.software_license.PASS_LOCKED_FIELDS), 5)
        # try to change pass
        try_edit(license_id, "pass_id", pass_basic2)
        # try to archive license
        try_edit(license_id, "active", False)
        # try to edit partner
        try_edit(
            license_id, "partner_id", self.env.ref("base.res_partner_address_7").id
        )
        # try to edit max activations
        try_edit(license_id, "max_allowed_hardware", 0)
        try_edit(license_id, "max_allowed_hardware", -1)
        try_edit(license_id, "max_allowed_hardware", 10)
        # try to edit expiration date
        try_edit(license_id, "expiration_date", datetime(2021, 9, 29, 10, 0, 0))
        try_edit(license_id, "expiration_date", False)
        # force archive license
        license_id.with_context(override_from_pass=True).active = False

    def test_03_delete_license_from_pass(self):
        pass_basic1 = self.env.ref("software_license_pass.pass_basic1")
        license_id = pass_basic1.license_ids[0]
        # try delete with basic pass user
        with self.assertRaisesRegex(
            UserError,
            r"It is forbidden to delete a license own by a pass.*\n%s"
            % (pass_basic1.name,),
        ), self.cr.savepoint():
            license_id.with_user(self.pass_user).unlink()
        # try delete with manager pass user
        with self.assertRaisesRegex(
            UserError,
            r"It is forbidden to delete a license own by a pass.*\n%s"
            % (pass_basic1.name,),
        ), self.cr.savepoint():
            license_id.with_user(self.pass_manager).unlink()
        # try delete with super-manager pass user
        license_id.with_user(self.pass_supermanager).unlink()

    def test_04_license_name_from_pass(self):
        pass_basic1 = self.env.ref("software_license_pass.pass_basic1")
        pass_serial = pass_basic1.serial
        license_id = pass_basic1.license_ids[0]
        license_serial = license_id.serial
        self.assertNotEqual(license_serial, pass_serial)
        self.assertEqual(
            license_id.display_name,
            "[New Age] %s (%s for Basic)" % (license_serial, pass_serial),
        )

    def test_05_license_activation(self):
        pass_basic1 = self.env.ref("software_license_pass.pass_basic1")
        license_id = pass_basic1.license_ids[0]
        # test exported values (even if comes from a private function)
        lic_exported_vals = license_id._prepare_export_vals()
        self.assertEqual(lic_exported_vals["pack"], "Basic")
        self.assertEqual(lic_exported_vals["pass"], pass_basic1.name)

    def test_06_license_pass_state_without_pass(self):
        pass_basic1 = self.env.ref("software_license_pass.pass_basic1")
        self.assertEqual(pass_basic1.state, "draft")
        license_id = pass_basic1.license_ids[0]
        self.assertEqual(license_id.pass_state, "draft")
        license_id.with_context(override_from_pass=True).pass_id = False
        self.assertEqual(pass_basic1.state, "draft")
        self.assertEqual(license_id.pass_state, "none")

    def test_07_pass_send(self):
        pass_basic1 = self.env.ref("software_license_pass.pass_basic1")
        # remove responsible
        pass_basic1.user_id = False
        self.assertEqual(pass_basic1.state, "draft")
        license_id = pass_basic1.license_ids[0]
        self.assertEqual(license_id.pass_state, "draft")
        action = pass_basic1.with_user(self.pass_user).action_send()
        wizard = (
            self.env[action["res_model"]].with_context(action["context"]).create({})
        )
        wizard.action_send_mail()
        self.assertEqual(pass_basic1.state, "sent")
        self.assertEqual(license_id.pass_state, "sent")
        self.assertEqual(pass_basic1.user_id, self.pass_user)

    def test_08_pass_cancel(self):
        pass_basic1 = self.env.ref("software_license_pass.pass_basic1")
        self.assertEqual(pass_basic1.state, "draft")
        license_id = pass_basic1.license_ids[0]
        self.assertEqual(license_id.pass_state, "draft")
        pass_basic1.action_cancel()
        self.assertEqual(pass_basic1.state, "cancel")
        self.assertEqual(license_id.pass_state, "cancel")

    def test_09_license_activation(self):
        pass_basic1 = self.env.ref("software_license_pass.pass_basic1")
        pass_basic1.serial = "pass_serial"
        license_id = pass_basic1.license_ids[0]
        license_id.serial = "license_serial"
        self.assertNotEqual(license_id.activation_identifier, "license_serial")
        self.assertEqual(license_id.activation_identifier, "pass_serial")

    def test_10_check_max_activation(self):
        pass_prm1 = self.env.ref("software_license_pass.pass_premium1")
        pass_prm1.max_allowed_hardware = 3
        pass_lic1 = pass_prm1.license_ids[0]
        pass_lic2 = pass_prm1.license_ids[1]
        self.assertEqual(pass_prm1.get_remaining_activation(), 3)
        self.assertEqual(pass_lic1.get_remaining_activation(), 3)
        self.assertEqual(pass_lic2.get_remaining_activation(), 3)
        pass_lic1.activate("device_uuid_1/3")
        self.assertFalse(pass_lic1.check_max_activation_reached("device_uuid_1/3"))
        self.assertFalse(pass_lic1.check_max_activation_reached("uuid_random"))
        self.assertEqual(pass_prm1.get_remaining_activation(), 2)
        self.assertEqual(pass_lic1.get_remaining_activation(), 2)
        self.assertEqual(pass_lic2.get_remaining_activation(), 3)
        pass_lic1.activate("device_uuid_2/3")
        self.assertFalse(pass_lic1.check_max_activation_reached("device_uuid_2/3"))
        self.assertFalse(pass_lic1.check_max_activation_reached("uuid_random"))
        self.assertEqual(pass_prm1.get_remaining_activation(), 1)
        self.assertEqual(pass_lic1.get_remaining_activation(), 1)
        self.assertEqual(pass_lic2.get_remaining_activation(), 3)
        pass_lic2.activate("device_uuid_3/3")
        # max activation reached must always return False if the device is already in
        # the list of activated hardware ...
        self.assertFalse(pass_lic1.check_max_activation_reached("device_uuid_1/3"))
        self.assertFalse(pass_lic1.check_max_activation_reached("device_uuid_2/3"))
        self.assertFalse(pass_lic1.check_max_activation_reached("device_uuid_3/3"))
        self.assertFalse(pass_lic2.check_max_activation_reached("device_uuid_3/3"))
        self.assertFalse(pass_lic2.check_max_activation_reached("device_uuid_3/3"))
        self.assertFalse(pass_lic2.check_max_activation_reached("device_uuid_3/3"))
        # ... contrary to this case where the hardware in unknown
        self.assertTrue(pass_lic1.check_max_activation_reached("uuid_random"))
        self.assertEqual(pass_prm1.get_remaining_activation(), 0)
        self.assertEqual(pass_lic1.get_remaining_activation(), 1)
        self.assertEqual(pass_lic2.get_remaining_activation(), 2)
        # ..
        with self.assertRaisesRegex(
            ValidationError, r"Maximum hardware identifier count reached for pass"
        ), self.cr.savepoint():
            pass_lic1.activate("device_uuid_4/3")
        self.assertEqual(pass_lic1.get_remaining_activation(), 1)
        with self.assertRaisesRegex(
            ValidationError, r"Maximum hardware identifier count reached for pass"
        ), self.cr.savepoint():
            pass_lic1.activate("device_uuid_4/3")
        # check unlimited activation
        fitness_app = self.env.ref("software_application.sa_myfitnessapp")
        fitness_lic3 = self.software_license.create(
            {
                "application_id": fitness_app.id,
                "max_allowed_hardware": 0,
                "serial": "FIT_003",
            }
        )
        self.assertEqual(fitness_lic3.get_remaining_activation(), -1)
        fitness_lic4 = self.software_license.create(
            {
                "application_id": fitness_app.id,
                "max_allowed_hardware": -2,
                "serial": "FIT_004",
            }
        )
        self.assertEqual(fitness_lic4.get_remaining_activation(), -1)

    def test_11_new_pass_default_serial(self):
        mypass = self.license_pass.create({})
        self.assertRegex(mypass.serial, self.REGEX_SERIAL)

    def test_12_pass_duplicate(self):
        pass_prm1 = self.env.ref("software_license_pass.pass_premium1")
        pass_prm1.max_allowed_hardware = 3
        pass_lic1 = pass_prm1.license_ids[0]
        pass_lic2 = pass_prm1.license_ids[1]
        pass_lic1.activate("device_uuid_1/3")
        pass_lic1.activate("device_uuid_2/3")
        pass_lic2.activate("device_uuid_3/3")
        # duplicate existing pass
        new_pass1 = pass_prm1.copy()
        self.assertEqual(new_pass1.serial, "%s (copy)" % (pass_prm1.serial))
        self.assertEqual(len(new_pass1.license_ids), 0)

    @freeze_time("2023-12-01 12:00:00")
    def test_13_update_license_from_pass(self):
        pass_prm1 = self.env.ref("software_license_pass.pass_premium1")
        pass_lic1 = pass_prm1.license_ids[0]
        pass_lic2 = pass_prm1.license_ids[1]
        pass_prm1.partner_id = self.env.ref("base.res_partner_2")
        self.assertEqual(pass_lic1.partner_id, pass_prm1.partner_id)
        self.assertEqual(pass_lic2.partner_id, pass_prm1.partner_id)
        pass_prm1.max_allowed_hardware = 3
        self.assertEqual(pass_lic1.max_allowed_hardware, pass_prm1.max_allowed_hardware)
        self.assertEqual(pass_lic2.max_allowed_hardware, pass_prm1.max_allowed_hardware)
        pass_prm1.expiration_date = fields.Datetime.now() + relativedelta(days=7)
        self.assertEqual(pass_lic1.expiration_date, pass_prm1.expiration_date)
        self.assertEqual(pass_lic2.expiration_date, pass_prm1.expiration_date)
        pass_prm1.active = False
        self.assertEqual(pass_lic1.active, pass_prm1.active)
        self.assertEqual(pass_lic2.active, pass_prm1.active)

    def test_14_update_pack(self):
        brickgame_app = self.env.ref("software_application.sa_brickgame")
        pack_premium = self.env.ref("software_license_pass.sl_pack_premium")
        self.assertEqual(len(pack_premium.line_ids), 3)
        pack_premium.write({"line_ids": [(0, 0, {"application_id": brickgame_app.id})]})
        self.assertEqual(len(pack_premium.line_ids), 4)

    def test_16_hardware_group(self):
        pass_prm1 = self.env.ref("software_license_pass.pass_premium1")
        pass_prm1.max_allowed_hardware = 10
        pass_lic1 = pass_prm1.license_ids[0]
        pass_lic2 = pass_prm1.license_ids[1]
        pass_lic3 = pass_prm1.license_ids[1]
        pass_lic1.activate(
            "device_uuid_1",
            info="""{
                "telemetry": {
                    "NetworkInformation": {
                        "DomainName": "ad.readymat.com",
                        "HostName": "PC-ReadyMat1"
                    }
                }
            }""",
        )
        # same device id but different hostname => must generate a new hardware group
        pass_lic2.activate(
            "device_uuid_1",
            info="""{
                "telemetry": {
                    "NetworkInformation": {
                        "DomainName": "ad.readymat.com",
                        "HostName": "PC-ReadyMat1_RENAMED_RECENTLY"
                    }
                }
            }""",
        )
        pass_lic2.activate("device_uuid_2")
        pass_lic3.activate("device_uuid_3")
        pass_lic3.activate("device_uuid_4")
        # device_uuid_1 should be there twice
        self.assertEqual(len(pass_prm1.hardware_group_ids), 5)
        # remaining activation should only consider 4 hardwares
        self.assertEqual(pass_prm1.get_remaining_activation(), 6)

    def test_17_hardware_group_deactivate(self):
        pass_prm3 = self.env.ref("software_license_pass.pass_premium3")
        group_names = pass_prm3.hardware_group_ids.mapped("name")
        group_count = len(pass_prm3.hardware_group_ids)
        for identifier in pass_prm3._get_unique_hardware_names():
            self.assertIn(identifier, group_names)
        pass_prm3.license_ids[0].activate("123456789")
        self.assertEqual(len(pass_prm3.hardware_group_ids), group_count + 1)
        pass_prm3.hardware_group_ids[-1].action_deactivate()
        self.assertEqual(len(pass_prm3.hardware_group_ids), group_count)

    def test_18_referral_partner(self):
        pass_prm3 = self.env.ref("software_license_pass.pass_premium3")
        # Ready Mat
        self.assertEqual(pass_prm3.partner_id, self.env.ref("base.res_partner_4"))
        # Ready Mat, Edith Sanchez
        pass_prm3.partner_referral_id = self.env.ref("base.res_partner_address_14")
        with self.assertRaisesRegex(
            ValidationError,
            r"The referral partner must be a hierarchical "
            "descendant of the main partner!",
        ), self.cr.savepoint():
            # Gemini Furniture, Soham Palmer
            pass_prm3.partner_referral_id = self.env.ref("base.res_partner_address_11")

    def test_19_partner_change_referral_partner(self):
        pass_prm3 = self.env.ref("software_license_pass.pass_premium3")
        # Ready Mat
        self.assertEqual(pass_prm3.partner_id, self.env.ref("base.res_partner_4"))
        # Ready Mat, Edith Sanchez
        pass_prm3.partner_referral_id = self.env.ref("base.res_partner_address_14")
        with Form(pass_prm3) as pass_form:
            pass_form.partner_id = self.env.ref("base.res_partner_3")
        self.assertFalse(pass_prm3.partner_referral_id)
