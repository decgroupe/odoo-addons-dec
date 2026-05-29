# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2026

from lxml import etree

from .common import TestWebsiteRedirectionMgmtCommon


class TestWebsiteRedirectionMgmt(TestWebsiteRedirectionMgmtCommon):
    """Tests for website_redirection_mgmt module."""

    def test_01_rewrite_group_creation(self):
        """Check that a website.rewrite.group record can be created."""
        self.assertEqual(self.group.name, "Test Campaign")
        self.assertEqual(self.group.note, "A test campaign group")

    def test_02_rewrite_extra_fields(self):
        """Check that the new fields on website.rewrite are assignable."""
        # assign group and UTM source/target
        utm_source = self.env["utm.source"].create({"name": "Test Source"})
        self.rewrite.write(
            {
                "group_id": self.group.id,
                "content_source_ids": [(4, utm_source.id)],
                "content_target_id": utm_source.id,
                "look": "clickable_link",
                "note": "<p>Test note</p>",
            }
        )
        self.assertEqual(self.rewrite.group_id, self.group)
        self.assertIn(utm_source, self.rewrite.content_source_ids)
        self.assertEqual(self.rewrite.content_target_id, utm_source)
        self.assertEqual(self.rewrite.look, "clickable_link")
        self.assertIn("Test note", self.rewrite.note)

    def test_03_onchange_url_sets_name(self):
        """Check that onchange_url auto-generates the name from url_from/url_to."""
        rewrite = self.WebsiteRewrite.new(
            {
                "redirect_type": "302",
                "url_from": "/foo",
                "url_to": "/bar",
                "name": "",
            }
        )
        rewrite.onchange_url()
        self.assertEqual(rewrite.name, "/foo 🡢 /bar")

    def test_04_onchange_url_updates_arrow_name(self):
        """Check that onchange_url overwrites a name that already contains the arrow."""
        rewrite = self.WebsiteRewrite.new(
            {
                "redirect_type": "302",
                "url_from": "/new-from",
                "url_to": "/new-to",
                "name": "/old 🡢 /stuff",
            }
        )
        rewrite.onchange_url()
        self.assertEqual(rewrite.name, "/new-from 🡢 /new-to")

    def test_05_onchange_url_preserves_custom_name(self):
        """Check that onchange_url does not overwrite a custom name."""
        rewrite = self.WebsiteRewrite.new(
            {
                "redirect_type": "302",
                "url_from": "/foo",
                "url_to": "/bar",
                "name": "My custom name",
            }
        )
        rewrite.onchange_url()
        self.assertEqual(rewrite.name, "My custom name")

    def test_06_form_view_fields(self):
        """Check that new fields are present in the combined form view arch."""
        view_info = self.WebsiteRewrite.get_view(view_type="form")
        arch = etree.fromstring(view_info["arch"].encode())
        field_names = [el.get("name") for el in arch.iter("field")]
        self.assertIn("group_id", field_names)
        self.assertIn("content_source_ids", field_names)
        self.assertIn("content_target_id", field_names)
        self.assertIn("look", field_names)
        self.assertIn("tag_ids", field_names)
        self.assertIn("note", field_names)

    def test_07_list_view_fields(self):
        """Check that new fields are present in the combined list view arch."""
        view_info = self.WebsiteRewrite.get_view(view_type="list")
        arch = etree.fromstring(view_info["arch"].encode())
        field_names = [el.get("name") for el in arch.iter("field")]
        self.assertIn("content_source_ids", field_names)
        self.assertIn("content_target_id", field_names)
        self.assertIn("tag_ids", field_names)

    def test_08_search_view_fields(self):
        """Check that new fields are present in the combined search view arch."""
        view_info = self.WebsiteRewrite.get_view(view_type="search")
        arch = etree.fromstring(view_info["arch"].encode())
        field_names = [el.get("name") for el in arch.iter("field")]
        self.assertIn("group_id", field_names)
        self.assertIn("content_source_ids", field_names)
        self.assertIn("content_target_id", field_names)
        self.assertIn("tag_ids", field_names)
