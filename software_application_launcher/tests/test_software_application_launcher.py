# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2025

from pprint import pprint

from odoo.addons.software_application_launcher.tests.common import (
    TestSoftwareApplicationLauncherBase,
)


class TestSoftwareApplicationLauncher(TestSoftwareApplicationLauncherBase):

    def setUp(self):
        super().setUp()

    def _get_app_by_name(self, manifest, name):
        for app in manifest["applications"]:
            if app["name"] == name:
                return app
        return None

    def _check_app_space_launcher_manifest_entry(self, entry):
        self.maxDiff = None
        ENTRY_ROOT = {
            "cornerImage": False,
            "identifier": 998,
            "image": False,
            "isFree": False,
            "isSoon": False,
            "isTool": False,
            "name": "Space-Launcher",
            "needLicense": False,
            "pictogramImage": False,
            "productDescription": False,
            "productName": False,
            "tooltipImages": [],
        }
        ENTRY_RELEASES = [
            {
                "date": "YYYY-MM-DD",
                "url": "https://cdn.mydomain.com/launchpad/spacelauncher/setup_3.1.1.exe",
                "version": {
                    "build": False,
                    "major": 3,
                    "minor": 1,
                    "patch": 1,
                    "prerelease": False,
                    "string": "3.1.1",
                },
            },
            {
                "date": "YYYY-MM-DD",
                "url": "https://cdn.mydomain.com/launchpad/spacelauncher/setup_3.1.0.exe",
                "version": {
                    "build": False,
                    "major": 3,
                    "minor": 1,
                    "patch": 0,
                    "prerelease": False,
                    "string": "3.1.0",
                },
            },
            {
                "date": "YYYY-MM-DD",
                "url": "https://cdn.mydomain.com/launchpad/spacelauncher/setup_2.0.1.exe",
                "version": {
                    "build": False,
                    "major": 2,
                    "minor": 0,
                    "patch": 1,
                    "prerelease": False,
                    "string": "2.0.1",
                },
            },
            {
                "date": "YYYY-MM-DD",
                "url": "https://cdn.mydomain.com/launchpad/spacelauncher/setup_2.0.0.exe",
                "version": {
                    "build": False,
                    "major": 2,
                    "minor": 0,
                    "patch": 0,
                    "prerelease": False,
                    "string": "2.0.0",
                },
            },
            {
                "date": "YYYY-MM-DD",
                "url": "https://cdn.mydomain.com/launchpad/spacelauncher/setup_1.0.0.exe",
                "version": {
                    "build": False,
                    "major": 1,
                    "minor": 0,
                    "patch": 0,
                    "prerelease": False,
                    "string": "1.0.0",
                },
            },
        ]
        ENTRY_RESOURCES = [
            {"identifier": 0, "name": "Space-Launcher's Quickstart"},
            {"identifier": 0, "name": "Space-Launcher's Userguide"},
        ]
        ENTRY_TAGS = [
            {"isSecondary": True, "tag": "Pegi 7"},
            {"isSecondary": True, "tag": "launcher"},
        ]

        _tags = entry.pop("tags", [])
        self.assertCountEqual(_tags, ENTRY_TAGS)
        _resources = entry.pop("resources", [])
        self.assertCountEqual(_resources, ENTRY_RESOURCES)
        _releases = entry.pop("releases", [])
        # small pre-process to ignore the date of the releases
        for release in _releases:
            release["date"] = "YYYY-MM-DD"
        # compare each release entry matches (ignoring order)
        self.assertCountEqual(_releases, ENTRY_RELEASES)
        for release in ENTRY_RELEASES:
            self.assertIn(release, _releases)

    def test_01_api_v1_get_manifest(self):
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

    def test_10_api_v2_get_manifest(self):
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

    def test_11_api_v2_get_manifest_invalid_identifier(self):
        manifest = self._api_v2_get_manifest(10)
        # check the structure of the manifest
        self.assertManifestStructure(manifest)
        # check their is no version attribute
        self.assertFalse("version" in manifest)
        # ensure empty lists
        self.assertEqual(manifest["applications"], [])
        self.assertEqual(manifest["resources"], [])
