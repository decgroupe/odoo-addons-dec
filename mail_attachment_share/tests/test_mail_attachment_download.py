# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2024

import base64

import odoo.tests
from .common import TestMailAttachmentCommon
from ..controllers.main import SHARING_URL


@odoo.tests.tagged("post_install", "-at_install")
class TestMailAttachmentDownload(TestMailAttachmentCommon, odoo.tests.HttpCase):

    def setUp(self):
        super().setUp()

    def test_01_download_using_token(self):
        self.assertFalse(self.attachment_id.sharing_link)
        self.attachment_id.action_generate_sharing_token_from_wizard()
        self.assertTrue(self.attachment_id.sharing_link)
        # remove base url to ensure ip address will be loopback
        url = self.attachment_id.sharing_link.replace(self.base_url, "")
        resp = self.url_open(url)
        self.assertEqual(resp.status_code, 200)
        datas = base64.b64decode(self.attachment_id.with_context(bin_size=False).datas)
        self.assertEqual(resp.content, datas)

    def test_02_get_with_invalid_token(self):
        url = SHARING_URL + "/aaaa-bbbb-cccc-dddd"
        resp = self.url_open(url)
        self.assertEqual(resp.status_code, 404)
        output = resp.content.decode('utf-8')
        self.assertIn("Attachment(s) not found", output)

