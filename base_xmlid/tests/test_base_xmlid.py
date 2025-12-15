# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jan 2025

from odoo.exceptions import UserError
from odoo.tests import new_test_user
from odoo.tests.common import TransactionCase


class TestBaseXmlid(TransactionCase):
    def _get_model_data(self, record):
        return self.imd.search(
            [("model", "=", record._name), ("res_id", "=", record.id)]
        )

    def _generate_xmlid(self, noupdate):
        module, name = self.imd.get_xmlid(self.user1)
        self.assertIsNone(module)
        self.assertIsNone(name)
        module, name = self.imd.get_xmlid(self.user1.partner_id)
        self.assertIsNone(module)
        self.assertIsNone(name)
        # create model data (aka xml-ids)
        data = self.imd.record_to_xmlid(
            self.user1, "fake_module", "my_user_01", noupdate
        )
        self.assertTrue(data.exists())
        module, name = self.imd.get_xmlid(self.user1)
        self.assertEqual(module, "fake_module")
        self.assertEqual(name, "my_user_01")
        # check parents (inherits) xml-ids
        module, name = self.imd.get_xmlid(self.user1.partner_id)
        self.assertEqual(module, "fake_module")
        self.assertEqual(name, "my_user_01_res_partner")
        parent_data = self._get_model_data(self.user1.partner_id)
        self.assertTrue(parent_data.exists())
        return data, parent_data

    def setUp(self):
        super().setUp()
        self.imd = self.env["ir.model.data"]
        # Azure Interior, Brandon Freeman
        self.partner_id = self.env.ref("base.res_partner_address_15")
        ctx = {
            "mail_create_nolog": True,
            "mail_create_nosubscribe": True,
            "mail_notrack": True,
            "no_reset_password": True,
        }
        self.user1 = new_test_user(
            self.env,
            login="user1",
            groups="base.group_user",
            context=ctx,
        )

    def test_01_get_xmlid(self):
        module, name = self.imd.get_xmlid(self.partner_id)
        self.assertEqual(module, "base")
        self.assertEqual(name, "res_partner_address_15")
        module_and_name = self.imd.get_xmlid_as_string(self.partner_id)
        self.assertEqual(module_and_name, "base.res_partner_address_15")

    def test_02_fail_generate_xmlid(self):
        module, name = self.imd.get_xmlid(self.user1)
        self.assertIsNone(module)
        self.assertIsNone(name)
        data = self.imd.record_to_xmlid(self.user1, module="", name="")
        self.assertFalse(data)
        data = self.imd.record_to_xmlid(self.user1, module="fake_module", name="")
        self.assertFalse(data)
        data = self.imd.record_to_xmlid(self.user1, module="", name="fake_module")
        self.assertFalse(data)

    def test_03_generate_xmlid(self):
        data, parent_data = self._generate_xmlid(noupdate=False)
        self.assertFalse(data.noupdate)
        self.assertFalse(parent_data.noupdate)

    def test_04_generate_xmlid(self):
        data, parent_data = self._generate_xmlid(noupdate=True)
        self.assertTrue(data.noupdate)
        self.assertTrue(parent_data.noupdate)

    def test_05_generate_xmlid(self):
        module, name = self.imd.get_xmlid(self.user1)
        self.assertIsNone(module)
        self.assertIsNone(name)
        # create model data (aka xml-ids)
        uid = self.user1.id
        data_id = self.imd.id_to_xmlid("res.users", uid, "fake_module", "my_user_01")
        self.assertTrue(data_id > 0)
        self.assertEqual(data_id, self._get_model_data(self.user1).id)
        module, name = self.imd.get_xmlid(self.user1)
        self.assertEqual(module, "fake_module")
        self.assertEqual(name, "my_user_01")

    def test_06_generate_xmlid_over_existing(self):
        ERROR_MSG = (
            "This record already owns an external ID: base.res_partner_address_15"
        )
        with self.assertRaisesRegex(UserError, ERROR_MSG), self.cr.savepoint():
            self.imd.record_to_xmlid(self.partner_id, "fake_module", "my_partner_01")
        # add replace options
        data = self.imd.record_to_xmlid(
            self.partner_id, "fake_module", "my_partner_01", replace=True
        )
        self.assertTrue(data.exists())
        module, name = self.imd.get_xmlid(self.partner_id)
        self.assertEqual(module, "fake_module")
        self.assertEqual(name, "my_partner_01")
