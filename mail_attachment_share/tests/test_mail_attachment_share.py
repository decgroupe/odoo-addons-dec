# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2024

import base64

from .common import TestMailAttachmentCommon
from ..controllers.main import SHARING_URL


class TestMailAttachmentShare(TestMailAttachmentCommon):

    def setUp(self):
        super().setUp()

    def test_01_generate_sharing_token(self):
        self.assertFalse(self.attachment_id.sharing_token)
        self.assertFalse(self.attachment_id.sharing_link)
        action = self.attachment_id.action_generate_sharing_token_from_wizard()
        # no action returned because no wizard in context
        self.assertIsNone(action)
        # but token must be set
        self.assertTrue(self.attachment_id.sharing_token)
        url = self.base_url + SHARING_URL + "/" + self.attachment_id.sharing_token
        self.assertEqual(self.attachment_id.sharing_link, url)

    def test_02_generate_sharing_token_from_wizard(self):
        self.assertFalse(self.attachment_id.sharing_token)
        self.assertFalse(self.attachment_id.sharing_link)
        # link attachment to a record (partner)
        self.attachment_id.write(
            {
                "res_model": self.partner_id._name,
                "res_id": self.partner_id.id,
            }
        )
        # create a new wizard linked to this record
        wizard_id = (
            self.env["attachment.sharing"]
            .with_context(
                default_res_model=self.partner_id._name,
                default_res_id=self.partner_id.id,
            )
            .create({})
        )
        self.assertIn(self.attachment_id, wizard_id.attachment_ids)
        # execute share action
        action = self.attachment_id.with_context(
            wizard_id=wizard_id.id
        ).action_generate_sharing_token_from_wizard()
        # an action is returned because wizard in context
        self.assertIsNotNone(action)
        self.assertEqual(action["type"], "ir.actions.act_window")
        self.assertEqual(action["res_id"], wizard_id.id)
        self.assertEqual(action["res_model"], wizard_id._name)
        self.assertEqual(action["target"], "new")
        # and token must be set
        self.assertTrue(self.attachment_id.sharing_token)
        url = self.base_url + SHARING_URL + "/" + self.attachment_id.sharing_token
        self.assertEqual(self.attachment_id.sharing_link, url)

    def test_03_create_wizard_unrelated(self):
        # create a new wizard not linked to any record
        wizard_id = self.env["attachment.sharing"].with_context().create({})
        self.assertFalse(wizard_id.attachment_ids)
