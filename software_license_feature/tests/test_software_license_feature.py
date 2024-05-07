# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Nov 2023

import contextlib
from unittest.mock import Mock

import odoo
from odoo.exceptions import UserError
from odoo.tests.common import Form, TransactionCase
from odoo.tools.misc import DotDict


@contextlib.contextmanager
def MockDebugRequest(env):
    request = Mock(
        db=None,
        env=env,
        session=DotDict(
            debug=True,
        ),
    )
    with contextlib.ExitStack() as s:
        odoo.http._request_stack.push(request)
        s.callback(odoo.http._request_stack.pop)
        yield request


class TestSoftwareLicenseFeature(TransactionCase):
    """ """

    def setUp(self):
        super().setUp()
        self.application_model = self.env["software.application"]
        self.software_license = self.env["software.license"]
        self.feature_model = self.env["software.license.feature"]
        self.feature_property_model = self.env["software.license.feature.property"]
        self.feature_value_model = self.env["software.license.feature.value"]

    def test_01_sync_with_template(self):
        fitness_lic2 = self.env.ref("software_license.sl_myfitnessapp2")
        self.assertFalse(fitness_lic2.feature_ids)
        # sync features with application license template
        fitness_lic2.action_sync_features_with_template()
        self.assertEqual(len(fitness_lic2.feature_ids), 3)
        lic_feature1 = fitness_lic2.feature_ids[0]
        lic_feature2 = fitness_lic2.feature_ids[1]
        self.assertEqual(lic_feature1.name, "Edition")
        self.assertEqual(lic_feature2.name, "Year")
        # compare with the template
        fitness_lic_template = self.env.ref("software_license.sl_myfitnessapp_tpl1")
        self.assertEqual(fitness_lic2.application_id.template_id, fitness_lic_template)
        tmpl_feature1 = fitness_lic_template.feature_ids[0]
        tmpl_feature2 = fitness_lic_template.feature_ids[1]
        # ensure features are the same
        self.assertEqual(tmpl_feature1.name, lic_feature1.name)
        self.assertEqual(tmpl_feature2.name, lic_feature2.name)
        # and their values too
        self.assertEqual(tmpl_feature1.value_id, lic_feature1.value_id)
        self.assertEqual(tmpl_feature2.value, lic_feature2.value)
        # resync
        fitness_lic2.action_sync_features_with_template()
        self.assertEqual(len(fitness_lic2.feature_ids), 3)
        # check that previous features are deleted
        self.assertFalse(lic_feature1.exists())
        self.assertFalse(lic_feature2.exists())

    def test_02_application_feature_edit_form(self):
        fitness_app = self.env.ref("software_application.sa_myfitnessapp")
        lic3_form = Form(self.software_license)
        self.assertEqual(len(lic3_form.feature_ids), 0)
        lic3_form.application_id = fitness_app
        self.assertEqual(len(lic3_form.feature_ids), 3)
        # features are added but no value is set, check that the `required` keyword
        # set in the view is working properly
        with self.assertRaisesRegex(
            AssertionError, "is a required field"
        ), self.cr.savepoint():
            lic3_form.save()
        # set edition value
        with lic3_form.feature_ids.edit(0) as feature_line_form:
            feature_line_form.value_id = self.env.ref(
                "software_license_feature.feature_edition_prop_gold"
            )
        # set year value
        with lic3_form.feature_ids.edit(1) as feature_line_form:
            feature_line_form.value = 2024
        # add a second edition feature
        with lic3_form.feature_ids.new() as feature_line_form:
            feature_line_form.property_id = self.env.ref(
                "software_license_feature.feature_edition"
            )
            feature_line_form.value_id = self.env.ref(
                "software_license_feature.feature_edition_prop_platinum"
            )
        # edit this line and replace the property "Edition" with "Year"
        with lic3_form.feature_ids.edit(2) as feature_line_form:
            feature_line_form.property_id = self.env.ref(
                "software_license_feature.feature_year"
            )
            # check that the previous property value has been correctly unset
            self.assertFalse(feature_line_form.value_id)
            feature_line_form.value = 2025
        fitness_lic3 = lic3_form.save()

    def test_03_create_feature(self):
        brickgame_lic1 = self.env.ref("software_license.sl_brickgame1")
        # sub-test with missing `value_id`
        data1 = {
            "license_id": brickgame_lic1.id,
            "sequence": 0,
            "property_id": self.env.ref("software_license_feature.feature_edition").id,
        }
        with self.assertRaisesRegex(
            UserError, r"Missing value for property .* Edition"
        ), self.cr.savepoint():
            self.feature_model.create(data1)
        data1["value_id"] = (
            self.env.ref("software_license_feature.feature_edition_prop_silver").id,
        )
        feature1_id = self.feature_model.create(data1)
        self.assertEqual(feature1_id.value_id.name, "Silver")
        # also test `name_get``
        self.assertEqual(feature1_id.value_id.display_name, "Silver")
        # retry with debug mode enabled in mocked http request
        with MockDebugRequest(self.env):
            feature1_id.value_id.invalidate_cache()
            self.assertEqual(feature1_id.value_id.display_name, "Silver (Edition)")
        # sub-test with missing `value`
        data2 = {
            "license_id": brickgame_lic1.id,
            "sequence": 1,
            "property_id": self.env.ref("software_license_feature.feature_year").id,
        }
        with self.assertRaisesRegex(
            UserError, r"Missing value for property .* Year"
        ), self.cr.savepoint():
            self.feature_model.create(data2)
        data2["value"] = 1998
        feature2_id = self.feature_model.create(data2)
        self.assertEqual(feature2_id.value, "1998")

    def test_05_license_activation(self):
        fitness_lic1 = self.env.ref("software_license.sl_myfitnessapp1")
        self.assertEqual(fitness_lic1.activation_identifier, fitness_lic1.serial)
        # test exported values (even if comes from a private function)
        lic_exported_vals = fitness_lic1._prepare_export_vals()
        self.assertEqual(lic_exported_vals["features"]["Edition"], ["Silver"])
        self.assertEqual(len(lic_exported_vals["features"]["Year"]), 2)
        self.assertIn("2022", lic_exported_vals["features"]["Year"])
        self.assertIn("2023", lic_exported_vals["features"]["Year"])
        # test exported values from hardware
        fitness_activation1 = self.env.ref("software_license.sl_myfitnessapp1_hw1")
        hw_exported_vals = fitness_activation1._prepare_export_vals()
        self.assertEqual(hw_exported_vals["features"]["Edition"], ["Silver"])
        self.assertEqual(len(hw_exported_vals["features"]["Year"]), 2)
        self.assertIn("2022", hw_exported_vals["features"]["Year"])
        self.assertIn("2023", hw_exported_vals["features"]["Year"])
