# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jan 2025

import logging

from odoo_test_helper import FakeModelLoader

from odoo import fields
from odoo.tests import new_test_user
from odoo.tests.common import SavepointCase

_test_logger = logging.getLogger("odoo.tests")


class TestBaseTypefast(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.loader = FakeModelLoader(cls.env, cls.__module__)
        cls.loader.backup_registry()

        # The fake class is imported here !! After the backup_registry
        # pylint: disable=import-outside-toplevel
        from .models import (
            FakeModel,
            FakeModelCharName,
            FakeModelIntName,
            FakeModelM2oName,
            FakeModelCustomNameGet,
        )

        cls.loader.update_registry(
            (
                FakeModel,
                FakeModelCharName,
                FakeModelIntName,
                FakeModelM2oName,
                FakeModelCustomNameGet,
            )
        )

    @classmethod
    def tearDownClass(cls):
        cls.loader.restore_registry()
        super().tearDownClass()

    def setUp(self):
        super().setUp()

    def test_01_basic_model(self):
        fake_model = self.env["fake.model"]
        obj_id = fake_model.create({"name": "⌛ Hello Guys"})
        self.assertEqual(obj_id.typefast_name, "HelloGuys")

    def test_02_model_char_name(self):
        fake_model = self.env["fake.model.char.name"]
        obj_id = fake_model.create({"serial": "#123-456 (789)"})
        self.assertEqual(obj_id.typefast_name, "123456789")

    def test_03_model_int_name(self):
        fake_model = self.env["fake.model.int.name"]
        obj_id = fake_model.create(
            {
                "number": 9,
            }
        )
        self.assertEqual(obj_id.display_name, "9")
        # Integer field are not supported
        self.assertEqual(obj_id.typefast_name, False)

    def test_04_model_m2o_name(self):
        fake_model = self.env["fake.model.m2o.name"]
        # Azure Interior, Brandon Freeman
        partner_id = self.env.ref("base.res_partner_address_15")
        self.assertEqual(partner_id.display_name, "Azure Interior, Brandon Freeman")
        obj_id = fake_model.create(
            {
                "partner_id": partner_id.id,
            }
        )
        self.assertEqual(obj_id.typefast_name, "AzureInteriorBrandonFreeman")

    def test_04_typefast_custom_source(self):
        fake_model = self.env["fake.model.custom.name.get"]
        obj_id = fake_model.create(
            {
                "name": "Bob",
                "prefix": "Mr",
                "suffix": "Junior",
            }
        )
        self.assertEqual(
            fake_model._typefast_options,
            {
                "source": "name_get",
            },
        )
        self.assertEqual(obj_id.typefast_name, "Mr Bob Junior")
        fake_model._typefast_options["strip"] = True
        # change name to force recomputation
        obj_id.name = "Will"
        self.assertEqual(obj_id.typefast_name, "MrWillJunior")
        # invalid source should disable typefast
        fake_model._typefast_options["source"] = "unknown"
        obj_id.name = "Marty"
        self.assertFalse(obj_id.typefast_name)

    def test_05_search(self):
        fake_model = self.env["fake.model"]
        r1 = fake_model.create({"name": "⌛ Hello Guys", "value": 1})
        r2 = fake_model.create({"name": "HelloKitty", "value": 1})
        r3 = fake_model.create({"name": "Hel lo Jo Wick"})
        r4 = fake_model.create({"name": "🚀 By Guys", "value": 1})
        rec_ids = list(fake_model._name_search("hello"))
        self.assertIn(r1.id, rec_ids)
        self.assertIn(r2.id, rec_ids)
        self.assertIn(r3.id, rec_ids)
        self.assertNotIn(r4.id, rec_ids)
        # search with specific operator (everything other than ilike should disable
        # typefast behaviour)
        rec_ids = list(fake_model._name_search("hello", operator="="))
        self.assertFalse(rec_ids)
        # search with specific domain
        domain = [("value", "=", "1")]
        rec_ids = list(fake_model._name_search("hello", args=domain))
        self.assertIn(r1.id, rec_ids)
        self.assertIn(r2.id, rec_ids)
        self.assertNotIn(r3.id, rec_ids)
        self.assertNotIn(r4.id, rec_ids)
