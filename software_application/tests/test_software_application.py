# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Nov 2023

from datetime import date

from freezegun import freeze_time

from odoo.tests.common import Form, TransactionCase


class TestSoftwareApplication(TransactionCase):
    """ """

    def setUp(self):
        super().setUp()
        self.application_model = self.env["software.application"]
        self.release_model = self.env["software.application.release"]

    def test_01_delete_application(self):
        fitness_app = self.env.ref("software_application.sa_myfitnessapp")
        fitness_app.unlink()
        self.assertFalse(fitness_app.exists())

    def test_02_delete_application_release(self):
        fitness_app_release = self.env.ref("software_application.sa_myfitnessapp_r0")
        fitness_app_release.unlink()
        self.assertFalse(fitness_app_release.exists())

    def test_03_delete_application_resource(self):
        fitness_app_resource = self.env.ref(
            "software_application.res_myfitnessapp_userguide"
        )
        fitness_app_resource.unlink()
        self.assertFalse(fitness_app_resource.exists())

    def test_04_release_parser(self):
        # test simple release format
        fitness_app_release = self.env.ref("software_application.sa_myfitnessapp_r1")
        self.assertEqual(fitness_app_release.version_major, 1)
        self.assertEqual(fitness_app_release.version_minor, 0)
        self.assertEqual(fitness_app_release.version_patch, 1)
        self.assertEqual(fitness_app_release.version_prerelease, False)
        self.assertEqual(fitness_app_release.version_build, False)
        # test advanced release format
        calm_app_release = self.env.ref("software_application.sa_calm_r0")
        self.assertEqual(calm_app_release.version_major, 1)
        self.assertEqual(calm_app_release.version_minor, 0)
        self.assertEqual(calm_app_release.version_patch, 1)
        self.assertEqual(calm_app_release.version_prerelease, "beta")
        self.assertEqual(calm_app_release.version_build, "Q3")
        # test custom release format
        calm_app_release.version = "1.2.3-alpha+B4"
        self.assertEqual(calm_app_release.version_major, 1)
        self.assertEqual(calm_app_release.version_minor, 2)
        self.assertEqual(calm_app_release.version_patch, 3)
        self.assertEqual(calm_app_release.version_prerelease, "alpha")
        self.assertEqual(calm_app_release.version_build, "B4")
        # test invert
        calm_app_release.version_major = 2
        self.assertEqual(calm_app_release.version, "2.2.3-alpha+B4")
        calm_app_release.version_minor = "123"
        calm_app_release.version_build = "INTERNAL_ONLY"
        calm_app_release.version_prerelease = "pre-release"
        self.assertEqual(calm_app_release.version, "2.123.3-pre-release+INTERNAL_ONLY")

    @freeze_time("2023-11-08 08:10:20")
    def test_05_release_default_values(self):
        newage_app = self.env.ref("software_application.sa_newage")
        newage_app_release = self.release_model.create(
            {"application_id": newage_app.id}
        )
        self.assertEqual(newage_app_release.version, "1.0.0")
        self.assertEqual(newage_app_release.date, date(2023, 11, 8))
        self.assertRegex(newage_app_release.content, "What's New")
        self.assertRegex(newage_app_release.content, "Fixes")
        self.assertRegex(newage_app_release.content, "Known Issues")
        self.assertFalse(newage_app_release.url)

    def test_06_application_form(self):
        myapp = self.application_model.create({"name": "MyApp"})
        with Form(myapp) as myapp_form:
            with myapp_form.release_ids.new() as release_form:
                self.assertEqual(release_form.version, "1.0.0")
                release_form.url = "https://cdn.mydomain.com/fake1"
            with myapp_form.release_ids.new() as release_form:
                self.assertEqual(release_form.version, "2.0.0")
                release_form.url = "https://cdn.mydomain.com/fake2"
        # exiting the `with Form()` statement will save our changes
        self.assertEqual(len(myapp.release_ids), 2)
        with Form(myapp) as myapp_form:
            with myapp_form.release_ids.new() as release_form:
                self.assertEqual(release_form.version, "3.0.0")
                release_form.url = "https://cdn.mydomain.com/fake3"
        self.assertEqual(len(myapp.release_ids), 3)

    def test_07_application_type(self):
        calm_app = self.env.ref("software_application.sa_calm")
        self.assertEqual(calm_app.type, "inhouse")
        self.assertTrue(calm_app.product_id)
        calm_app.type = "other"
        # converting to `other` should remove product reference
        self.assertFalse(calm_app.product_id)
        # converting to `other` should remove product reference
        fitness_app = self.env.ref("software_application.sa_myfitnessapp")
        self.assertEqual(len(fitness_app.resource_ids), 1)
        self.assertEqual(len(fitness_app.tag_ids), 1)
        fitness_app.type = "other"
        # converting to `other` should remove all resource references
        self.assertEqual(len(fitness_app.resource_ids), 0)
        self.assertEqual(len(fitness_app.tag_ids), 0)

    def test_08_application_image(self):
        base64_1x1_png = b"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADElEQVR4nGNgYGAAAAAEAAH2FzhVAAAAAElFTkSuQmCC"
        fitness_app = self.env.ref("software_application.sa_myfitnessapp")
        fitness_app.image = base64_1x1_png
        self.assertEqual(fitness_app.attachment_image, fitness_app.image)
