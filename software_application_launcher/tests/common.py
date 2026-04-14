# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2025

import json
import logging

import odoo.tests
from odoo.tests import new_test_user

_logger = logging.getLogger(__name__)


API_KEY = "d5b27d10-3db6-47b4-ab7e-412cd4418f6b"

# minimal valid 4x4 white PNG in base64
_PIXEL_PNG = b"iVBORw0KGgoAAAANSUhEUgAAAAQAAAAECAIAAAAmkwkpAAAAFElEQVR4nGP8//8/AwwwMSAB3BwAlm4DBfIlvvkAAAAASUVORK5CYII="  # noqa: E501


class TestSoftwareApplicationLauncherBase(odoo.tests.HttpCase):
    """Base class with shared test fixtures for software_application_launcher."""

    def assertManifestStructure(self, manifest):
        self.assertIsInstance(manifest, dict)
        self.assertIn("applications", manifest)
        self.assertIsInstance(manifest["applications"], list)
        self.assertIn("resources", manifest)
        self.assertIsInstance(manifest["resources"], list)

    @classmethod
    def setUpClass(cls):
        """Set up shared test data."""
        super().setUpClass()
        cls.SoftwareApplication = cls.env["software.application"]
        cls.SoftwareTag = cls.env["software.tag"]
        cls.SoftwareApplicationImage = cls.env["software.application.image"]
        # create a basic inhouse application for use across tests
        cls.app_inhouse = cls.SoftwareApplication.create(
            {
                "name": "Test Inhouse App",
                "type": "inhouse",
                "identifier": 50001,
            }
        )
        # create a resource application
        cls.app_resource = cls.SoftwareApplication.create(
            {
                "name": "Test Resource App",
                "type": "resource",
                "identifier": 50002,
            }
        )
        # create an other-type application
        cls.app_other = cls.SoftwareApplication.create(
            {
                "name": "Test Other App",
                "type": "other",
                "identifier": 50003,
            }
        )

    def setUp(self):
        super().setUp()
        ctx = {
            "mail_create_nolog": True,
            "mail_create_nosubscribe": True,
            "mail_notrack": True,
            "no_reset_password": True,
        }
        self.company = self.env.ref("base.main_company")
        self.api_user = new_test_user(
            self.env,
            login="api-user",
            password="api-user",
            groups="software.group_software_user",
            context=ctx,
        )
        self.api_key = self.env["auth.api.key"].create(
            {
                "name": "MyRemoteTool",
                "user_id": self.api_user.id,
                "key": API_KEY,
            }
        )

        self.api_user.parent_id = self.company.partner_id

    def _get_app_by_name(self, manifest, name):
        for app in manifest["applications"]:
            if app["name"] == name:
                return app
        return None

    def _check_app_space_launcher_manifest_entry(self, entry):
        self.maxDiff = None
        _ENTRY_ROOT = {
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

    def _get_common_payload(self, params):
        return {
            "jsonrpc": "2.0",
            "params": params,
        }

    def _api_v1_launcher(self, url, payload=None, headers=False):
        """Post a JSON-RPC call authenticated with the API key."""
        if not payload:
            payload = self._get_common_payload(params={})
        if not headers:
            headers = {}
        headers.update(
            {
                "Content-Type": "application/json",
                "Api-Key": API_KEY,
            }
        )
        resp = self.url_open(
            f"/api/launcher/v1/{url}",
            data=json.dumps(payload),
            headers=headers,
        )
        self.assertEqual(resp.status_code, 200)
        resp_payload = json.loads(resp.text)
        self.assertEqual(resp_payload.get("jsonrpc"), "2.0")
        if "error" in resp_payload:
            message = resp_payload["error"]["data"].get("message")
            debug = resp_payload["error"]["data"].get("debug")
            _logger.error("API %s Error:\n%s\n%s", url, message, debug)
        res = resp_payload.get("result")
        return res

    def _api_v1_get_manifest(self, payload=None, headers=False):
        return self._api_v1_launcher(
            "Manifest",
            payload=payload,
            headers=headers,
        )

    def _api_v1_get_manifest_with_images(self, payload=None, headers=False):
        return self._api_v1_launcher(
            "Manifest/Images",
            payload=payload,
            headers=headers,
        )

    def _api_v1_get_manifest_for_identifier(
        self, identifier, payload=None, headers=False
    ):
        return self._api_v1_launcher(
            f"Manifest/identifier/{identifier}",
            payload=payload,
            headers=headers,
        )

    def _api_v2_launcher(self, launcher_identifier, url, payload=None, headers=False):
        """Post a JSON-RPC call authenticated with the API key."""
        if not payload:
            payload = self._get_common_payload(params={})
        if not headers:
            headers = {}
        headers.update(
            {
                "Content-Type": "application/json",
                "Api-Key": API_KEY,
            }
        )
        resp = self.url_open(
            f"/api/launcher/v2/identifier/{launcher_identifier}/{url}",
            data=json.dumps(payload),
            headers=headers,
        )
        self.assertEqual(resp.status_code, 200)
        resp_payload = json.loads(resp.text)
        self.assertEqual(resp_payload.get("jsonrpc"), "2.0")
        if "error" in resp_payload:
            message = resp_payload["error"]["data"].get("message")
            debug = resp_payload["error"]["data"].get("debug")
            _logger.error("API %s Error:\n%s\n%s", url, message, debug)
        res = resp_payload.get("result")
        return res

    def _api_v2_get_manifest(self, launcher_identifier, payload=None, headers=False):
        return self._api_v2_launcher(
            launcher_identifier,
            "Manifest",
            payload=payload,
            headers=headers,
        )

    def _api_v2_get_manifest_with_images(
        self, launcher_identifier, payload=None, headers=False
    ):
        return self._api_v2_launcher(
            launcher_identifier,
            "Manifest/Images",
            payload=payload,
            headers=headers,
        )

    def _api_v2_get_manifest_for_identifier(
        self, launcher_identifier, identifier, payload=None, headers=False
    ):
        return self._api_v2_launcher(
            launcher_identifier,
            f"Manifest/asset/{identifier}",
            payload=payload,
            headers=headers,
        )
