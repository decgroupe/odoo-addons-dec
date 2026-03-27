# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2026

from odoo.tests.common import TransactionCase

# minimal 1x1 transparent GIF image encoded as base64
_GIF_B64 = "R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"


class TestDocumentPageImageToAttachment(TransactionCase):
    """Test DocumentPageImageToAttachment module."""

    def setUp(self):
        """Create a test document page."""
        super().setUp()
        self.page = self.env["document.page"].create(
            {
                "name": "Test Page",
                "content": "<p>Initial content</p>",
            }
        )

    def _attachment_count(self):
        """Return number of attachments linked to the test page."""
        return self.env["ir.attachment"].search_count(
            [
                ("res_model", "=", "document.page"),
                ("res_id", "=", self.page.id),
            ]
        )

    def _get_attachments(self):
        """Return attachments linked to the test page."""
        return self.env["ir.attachment"].search(
            [
                ("res_model", "=", "document.page"),
                ("res_id", "=", self.page.id),
            ]
        )

    def test_01_no_images(self):
        """Test that content without inline images is not modified."""
        content = "<p>No images here</p>"
        self.page.content = content
        count_before = self._attachment_count()
        self.page.action_convert_content_images_to_attachments()
        self.assertEqual(self._attachment_count(), count_before)
        self.assertNotIn("data:image", self.page.content)

    def test_02_convert_single_image(self):
        """Test that a single base64 inline image is converted to an attachment."""
        content = f'<p><img src="data:image/gif;base64,{_GIF_B64}"/></p>'
        self.page.content = content
        count_before = self._attachment_count()
        self.page.action_convert_content_images_to_attachments()
        # one new attachment must have been created
        self.assertEqual(self._attachment_count(), count_before + 1)
        # content must no longer contain base64 data
        self.assertNotIn("data:image", self.page.content)
        # content must contain a web image URL with access token
        self.assertIn("/web/image/", self.page.content)
        self.assertIn("access_token=", self.page.content)

    def test_03_named_image(self):
        """Test that data-filename attribute is used as the attachment name."""
        filename = "logo.gif"
        content = (
            f'<p><img src="data:image/gif;base64,{_GIF_B64}"'
            f' data-filename="{filename}"/></p>'
        )
        self.page.content = content
        self.page.action_convert_content_images_to_attachments()
        attachments = self._get_attachments()
        self.assertEqual(len(attachments), 1)
        self.assertEqual(attachments.name, filename)
        # converted content must use the filename as alt text
        self.assertIn(f'alt="{filename}"', self.page.content)

    def test_04_duplicate_image(self):
        """Test that duplicate base64 images yield only one attachment."""
        img_tag = f'<img src="data:image/gif;base64,{_GIF_B64}"/>'
        content = f"<p>{img_tag}{img_tag}</p>"
        self.page.content = content
        self.page.action_convert_content_images_to_attachments()
        # only one attachment despite two identical images
        self.assertEqual(self._attachment_count(), 1)
        # both occurrences must be replaced
        self.assertNotIn("data:image", self.page.content)

    def test_05_invalid_base64_image(self):
        """Test that a badly formatted base64 image triggers binascii_error.

        A base64 string whose length % 4 == 1 (here 5 chars) cannot be decoded
        even with lenient settings and raises binascii.Error inside
        ir.attachment.create().  The code must catch it, log a warning, remove
        the invalid image from the content, and create no attachment.
        """
        # 5-char string: valid regex match but length % 4 == 1 → undecodable
        invalid_b64 = "aaaaa"
        content = f'<p><img src="data:image/gif;base64,{invalid_b64}"/></p>'
        self.page.content = content
        count_before = self._attachment_count()
        self.page.action_convert_content_images_to_attachments()
        # no attachment must have been created
        self.assertEqual(self._attachment_count(), count_before)
        # the invalid image tag must have been removed from the content
        self.assertNotIn("data:image", self.page.content)
