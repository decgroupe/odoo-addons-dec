# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2026

from lxml import etree

from odoo import Command
from odoo.exceptions import UserError

from .common import _PIXEL_PNG, TestSoftwareApplicationLauncherBase


class TestSoftwareApplicationLauncher(TestSoftwareApplicationLauncherBase):
    """Tests for software_application_launcher module."""

    def test_01_write_clears_launcher_fields_on_type_other(self):
        """Changing type to 'other' must clear corner/pictogram images and image_ids."""
        # setup: assign launcher-specific data to an inhouse app
        app = self.SoftwareApplication.create(
            {
                "name": "App Before Other",
                "type": "inhouse",
                "corner_image": _PIXEL_PNG,
                "pictogram_image": _PIXEL_PNG,
            }
        )
        image = self.SoftwareApplicationImage.create(
            {
                "name": "tooltip_01",
                "application_id": app.id,
                "image": _PIXEL_PNG,
            }
        )
        app.write({"image_ids": [Command.link(image.id)]})
        self.assertTrue(app.corner_image)
        self.assertTrue(app.pictogram_image)
        self.assertTrue(app.image_ids)
        # act: change type to "other"
        app.write({"type": "other"})
        # assert: launcher fields must be cleared
        self.assertFalse(app.corner_image)
        self.assertFalse(app.pictogram_image)
        self.assertFalse(app.image_ids)

    def test_02_write_no_clear_when_not_other(self):
        """Changing type between inhouse/resource must not clear launcher fields."""
        app = self.SoftwareApplication.create(
            {
                "name": "App Not Other",
                "type": "inhouse",
                "corner_image": _PIXEL_PNG,
            }
        )
        # act: change type to "resource" (not "other")
        app.write({"type": "resource"})
        # assert: corner_image is preserved
        self.assertTrue(app.corner_image)

    def test_03_get_launcher_manifest_domain(self):
        """_get_launcher_manifest_domain must return inhouse and resource types."""
        domain = self.SoftwareApplication._get_launcher_manifest_domain()
        # check domain is non-empty and includes expected types
        self.assertTrue(domain)
        # only inhouse and resource apps are returned, not "other"
        apps = self.SoftwareApplication.search(domain)
        types = set(apps.mapped("type"))
        self.assertNotIn("other", types)
        self.assertIn(self.app_inhouse.id, apps.ids)
        self.assertIn(self.app_resource.id, apps.ids)
        self.assertNotIn(self.app_other.id, apps.ids)

    def test_04_get_launcher_manifest_entry_structure(self):
        """_get_launcher_manifest_entry must return the expected dict keys."""
        entry = self.app_inhouse._get_launcher_manifest_entry()
        expected_keys = {
            "name",
            "productName",
            "productDescription",
            "identifier",
            "image",
            "isSoon",
            "isFree",
            "isTool",
            "shopLink",
            "needLicense",
            "resources",
            "releases",
            "tags",
            "cornerImage",
            "pictogramImage",
            "tooltipImages",
        }
        self.assertEqual(set(entry.keys()), expected_keys)
        # tooltipImages must be empty when with_tooltips=False
        self.assertEqual(entry["tooltipImages"], [])

    def test_05_get_launcher_manifest_entry_with_tooltips(self):
        """_get_launcher_manifest_entry must include tooltip images when requested."""
        app = self.SoftwareApplication.create(
            {
                "name": "App With Tooltips",
                "type": "inhouse",
            }
        )
        self.SoftwareApplicationImage.create(
            {
                "name": "tooltip_01",
                "application_id": app.id,
                "image": _PIXEL_PNG,
            }
        )
        entry = app._get_launcher_manifest_entry(with_tooltips=True)
        self.assertEqual(len(entry["tooltipImages"]), 1)
        self.assertEqual(entry["tooltipImages"][0]["name"], "tooltip_01")

    def test_06_get_launcher_manifest_entry_is_tool(self):
        """_get_launcher_manifest_entry must set isTool=True for apps tagged 'tool'."""
        tag_tool = self.env.ref("software_application_launcher.tag_tool")
        self.app_inhouse.write({"tag_ids": [Command.link(tag_tool.id)]})
        entry = self.app_inhouse._get_launcher_manifest_entry()
        self.assertTrue(entry["isTool"])
        # cleanup
        self.app_inhouse.write({"tag_ids": [Command.unlink(tag_tool.id)]})

    def test_07_tag_unlink_protected(self):
        """Deleting the protected 'tool' tag must raise a UserError."""
        tag_tool = self.env.ref("software_application_launcher.tag_tool")
        with self.assertRaises(UserError):
            tag_tool.unlink()

    def test_08_tag_unlink_allowed(self):
        """Deleting a non-protected tag must succeed."""
        tag = self.SoftwareTag.create({"name": "Deletable Tag"})
        # must not raise
        tag.unlink()
        self.assertFalse(self.SoftwareTag.search([("name", "=", "Deletable Tag")]))

    def test_09_image_default_name(self):
        """_default_name must generate tooltip_01 for the first image."""
        image = self.SoftwareApplicationImage.with_context(image_ids=[]).create(
            {
                "application_id": self.app_inhouse.id,
                "image": _PIXEL_PNG,
            }
        )
        self.assertTrue(image.name.startswith("tooltip_"))

    def test_10_form_view_launcher_fields(self):
        """Launcher fields must be present in the combined application form view."""
        view_info = self.SoftwareApplication.get_view(view_type="form")
        arch = etree.fromstring(view_info["arch"])
        field_names = [el.get("name") for el in arch.iter("field")]
        self.assertIn("is_free", field_names)
        self.assertIn("is_soon", field_names)
        self.assertIn("need_license", field_names)
        self.assertIn("corner_image", field_names)
        self.assertIn("pictogram_image", field_names)
        self.assertIn("image_ids", field_names)

    def test_11_image_form_view_fields(self):
        """Expected fields must be present in the image form view."""
        view_info = self.SoftwareApplicationImage.get_view(view_type="form")
        arch = etree.fromstring(view_info["arch"])
        field_names = [el.get("name") for el in arch.iter("field")]
        self.assertIn("name", field_names)
        self.assertIn("resized_image", field_names)
        self.assertIn("resize_x", field_names)
        self.assertIn("resize_y", field_names)

    def test_12_manifest_entry_flags(self):
        """is_free, is_soon, need_license flags must be reflected in the manifest
        entry."""
        app = self.SoftwareApplication.create(
            {
                "name": "Free Soon App",
                "type": "inhouse",
                "is_free": True,
                "is_soon": True,
                "need_license": True,
            }
        )
        entry = app._get_launcher_manifest_entry()
        self.assertTrue(entry["isFree"])
        self.assertTrue(entry["isSoon"])
        self.assertTrue(entry["needLicense"])

    def test_13_manifest_entry_with_resource_and_release(self):
        """Resources and releases must appear in the manifest entry dict."""
        resource = self.SoftwareApplication.create(
            {
                "name": "Test Resource",
                "type": "resource",
                "identifier": 42,
            }
        )
        app = self.SoftwareApplication.create(
            {
                "name": "App With Resource",
                "type": "inhouse",
                "resource_ids": [Command.link(resource.id)],
            }
        )
        self.env["software.application.release"].create(
            {
                "application_id": app.id,
                "version": "2.0.0",
                "url": "https://example.com/dl",
            }
        )
        entry = app._get_launcher_manifest_entry()
        # resources list must contain the linked resource
        self.assertEqual(len(entry["resources"]), 1)
        self.assertEqual(entry["resources"][0]["identifier"], 42)
        # releases list must contain the created release
        self.assertEqual(len(entry["releases"]), 1)
        self.assertEqual(entry["releases"][0]["version"]["string"], "2.0.0")

    def test_14_image_default_name_with_existing_images(self):
        """_default_name must compute tooltip_03 when two images already exist."""
        # simulate the context that a form view sends when two images exist
        img1 = self.SoftwareApplicationImage.create(
            {
                "name": "tooltip_01",
                "application_id": self.app_inhouse.id,
                "image": _PIXEL_PNG,
            }
        )
        img2 = self.SoftwareApplicationImage.create(
            {
                "name": "tooltip_02",
                "application_id": self.app_inhouse.id,
                "image": _PIXEL_PNG,
            }
        )
        # simulate context with existing records referenced by int id
        ctx_image_ids = [
            (1, img1.id, {}),
            (1, img2.id, {}),
        ]
        name = self.SoftwareApplicationImage.with_context(
            image_ids=ctx_image_ids
        )._default_name()
        self.assertEqual(name, "tooltip_03")

    def test_15_image_default_name_with_new_record_vals(self):
        """_default_name must handle virtual (str, dict) entries in the context."""
        # simulate context with a virtual record (str key, dict vals)
        ctx_image_ids = [
            (0, "virtual_1", {"name": "tooltip_05"}),
        ]
        name = self.SoftwareApplicationImage.with_context(
            image_ids=ctx_image_ids
        )._default_name()
        self.assertEqual(name, "tooltip_06")

    def test_16_image_inverse_resized(self):
        """Setting resized_image must write back the processed image to image."""
        image = self.SoftwareApplicationImage.create(
            {
                "name": "tooltip_inv",
                "application_id": self.app_inhouse.id,
                "image": _PIXEL_PNG,
            }
        )
        # assigning to resized_image must trigger _inverse_image
        image.resized_image = _PIXEL_PNG
        # the image field must be updated after the inverse
        self.assertTrue(image.image)

    def test_17_image_default_get(self):
        """default_get must return a dict (pass-through to super)."""
        defaults = self.SoftwareApplicationImage.default_get(["name", "resize_x"])
        self.assertIsInstance(defaults, dict)
