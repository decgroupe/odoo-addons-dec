# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2025

import logging

import odoo.tests

from .common import TestSoftwareApplicationLauncherBase

_logger = logging.getLogger(__name__)


@odoo.tests.tagged("post_install", "-at_install")
class TestSoftwareApplicationLauncher(TestSoftwareApplicationLauncherBase):
    """HTTP controller tests for software_application_launcher."""

    def setUp(self):
        super().setUp()

    def test_10_api_v1_get_manifest_route(self):
        """GET /api/launcher/v1/Manifest must return a manifest structure."""
        result = self._api_v1_get_manifest()
        self.assertIsNotNone(result)
        self.assertIn("applications", result)
        self.assertIn("resources", result)

    def test_11_api_v1_get_manifest_images_route(self):
        """GET /api/launcher/v1/Manifest/Images must return a manifest with tooltips."""
        result = self._api_v1_get_manifest_with_images()
        self.assertIsNotNone(result)

    def test_12_api_v1_get_manifest_identifier_route(self):
        """GET /api/launcher/v1/Manifest/identifier/<id> must filter by identifier."""
        result = self._api_v1_get_manifest_for_identifier(self.app_inhouse.identifier)
        self.assertIsNotNone(result)
        applications = result.get("applications", [])
        self.assertEqual(len(applications), 1)
        self.assertFalse(applications[0].get("cornerImage"))
        self.assertEqual(applications[0].get("identifier"), 50001)
        self.assertFalse(applications[0].get("image"))
        self.assertFalse(applications[0].get("isFree"))
        self.assertFalse(applications[0].get("isSoon"))
        self.assertFalse(applications[0].get("isTool"))
        self.assertEqual(applications[0].get("name"), "Test Inhouse App")
        self.assertFalse(applications[0].get("needLicense"))
        self.assertFalse(applications[0].get("pictogramImage"))
        self.assertFalse(applications[0].get("productDescription"))
        self.assertFalse(applications[0].get("productName"))
        self.assertEqual(applications[0].get("releases"), [])
        self.assertEqual(applications[0].get("resources"), [])
        self.assertFalse(applications[0].get("shopLink"))
        self.assertEqual(applications[0].get("tags"), [])
        self.assertEqual(applications[0].get("tooltipImages"), [])

    def test_15_api_v1_get_manifest(self):
        manifest = self._api_v1_get_manifest()
        # check the structure of the manifest
        self.assertManifestStructure(manifest)
        # check version is 2
        self.assertEqual(manifest.get("version"), 2)
        # aggregate all applications names
        app_names = [app["name"] for app in manifest["applications"]]
        # check some known applications
        self.assertIn("New Age", app_names)
        self.assertIn("MyFitnessApp", app_names)
        self.assertIn("The Brick Game", app_names)
        self.assertIn("Calm", app_names)
        # check that private applications (ID < 1000) are not listed
        self.assertNotIn("Securia Privacy", app_names)
        # check that the launcher application is listed even if its ID is < 1000
        # because 998 is a special case
        self.assertIn("Space-Launcher", app_names)
        # check the manifest entry for Space-Launcher
        self._check_app_space_launcher_manifest_entry(
            self._get_app_by_name(manifest, "Space-Launcher")
        )
        # check that resources attached to space-launcher are also listed
        resource_names = [res["name"] for res in manifest["resources"]]
        self.assertIn("Space-Launcher's Quickstart", resource_names)
        self.assertIn("Space-Launcher's Userguide", resource_names)

    def test_20_api_v2_get_manifest_route(self):
        """GET /api/launcher/v2/identifier/<id>/Manifest must return a manifest
        structure."""
        result = self._api_v2_get_manifest(998)
        self.assertIsNotNone(result)
        self.assertIn("applications", result)
        self.assertIn("resources", result)

    def test_21_api_v2_get_manifest_images_route(self):
        """GET /api/launcher/v2/identifier/<id>/Manifest/Images must return a manifest
        with tooltips."""
        result = self._api_v2_get_manifest_with_images(998)
        self.assertIsNotNone(result)

    def test_22_api_v2_get_manifest_identifier_route(self):
        """GET /api/launcher/v2/identifier/<id>/Manifest/asset/<id> must filter
        by identifier."""
        spacelauncher = self.env.ref("software_application_launcher.sa_spacelauncher")
        # link the inhouse app to the launcher to ensure it is included in the manifest
        spacelauncher.application_ids |= self.app_inhouse
        result = self._api_v2_get_manifest_for_identifier(
            998, self.app_inhouse.identifier
        )
        self.assertIsNotNone(result)
        applications = result.get("applications", [])
        self.assertEqual(len(applications), 1)
        self.assertFalse(applications[0].get("cornerImage"))
        self.assertEqual(applications[0].get("identifier"), 50001)
        self.assertFalse(applications[0].get("image"))
        self.assertFalse(applications[0].get("isFree"))
        self.assertFalse(applications[0].get("isSoon"))
        self.assertFalse(applications[0].get("isTool"))
        self.assertEqual(applications[0].get("name"), "Test Inhouse App")
        self.assertFalse(applications[0].get("needLicense"))
        self.assertFalse(applications[0].get("pictogramImage"))
        self.assertFalse(applications[0].get("productDescription"))
        self.assertFalse(applications[0].get("productName"))
        self.assertEqual(applications[0].get("releases"), [])
        self.assertEqual(applications[0].get("resources"), [])
        self.assertFalse(applications[0].get("shopLink"))
        self.assertEqual(applications[0].get("tags"), [])
        self.assertEqual(applications[0].get("tooltipImages"), [])

    def test_25_api_v2_get_manifest(self):
        spacelauncher = self.env.ref("software_application_launcher.sa_spacelauncher")
        manifest = self._api_v2_get_manifest(spacelauncher.identifier)
        # check the structure of the manifest
        self.assertManifestStructure(manifest)
        # check their is no version attribute
        self.assertFalse("version" in manifest)
        # aggregate all applications names
        app_names = [app["name"] for app in manifest["applications"]]
        # check that only specific applications are listed
        self.assertCountEqual(
            app_names,
            [
                "Space-Launcher",
                "MyFitnessApp",
                "Calm",
            ],
        )
        # check the manifest entry for Space-Launcher
        self._check_app_space_launcher_manifest_entry(
            self._get_app_by_name(manifest, "Space-Launcher")
        )
        # also check that only resources attached to one of these apps are listed
        resource_names = [res["name"] for res in manifest["resources"]]
        self.assertCountEqual(
            resource_names,
            [
                "Space-Launcher's Quickstart",
                "Space-Launcher's Userguide",
                "MyFitnessApp's Userguide",
            ],
        )

    def test_26_api_v2_get_manifest_invalid_identifier(self):
        manifest = self._api_v2_get_manifest(10)
        # check the structure of the manifest
        self.assertManifestStructure(manifest)
        # check their is no version attribute
        self.assertFalse("version" in manifest)
        # ensure empty lists
        self.assertEqual(manifest["applications"], [])
        self.assertEqual(manifest["resources"], [])
