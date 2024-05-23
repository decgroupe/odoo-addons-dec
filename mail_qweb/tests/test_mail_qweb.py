# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2024

import logging

from odoo_test_helper import FakeModelLoader

from odoo.tests import new_test_user
from odoo.tests.common import SavepointCase

_test_logger = logging.getLogger("odoo.tests")


class TestMailQweb(SavepointCase):

    def mail_unlink_disabled(self):
        # disable automatic mail-deletion
        def unlink(self):
            _test_logger.warning("Unlink disabled for `mail.mail`")

        self.Mail._patch_method("unlink", unlink)

    def mail_unlink_enabled(self):
        # restore original method
        self.Mail._revert_method("unlink")

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.loader = FakeModelLoader(cls.env, cls.__module__)
        cls.loader.backup_registry()

        # The fake class is imported here !! After the backup_registry
        from .models import FakeModelWithoutName

        cls.loader.update_registry((FakeModelWithoutName,))
        cls.Mail = cls.env["mail.mail"]

    @classmethod
    def tearDownClass(cls):
        cls.loader.restore_registry()
        super().tearDownClass()

    def setUp(self):
        super().setUp()
        ctx = {
            "mail_create_nolog": True,
            "mail_create_nosubscribe": True,
            "mail_notrack": True,
            "no_reset_password": True,
        }
        self.user = new_test_user(
            self.env,
            login="myuser@mycompany.com",
            groups="base.group_user",
            context=ctx,
        )

    def test_01_model_without_name(self):
        try:
            self.mail_unlink_disabled()
            # create record and subscribe our user to all possible subtypes
            obj_id = self.env["fake.model.without.name"].create({"serial": "123456"})
            all_subtype_ids = self.env["mail.message.subtype"].search([])
            obj_id.message_subscribe(
                [self.user.partner_id.id], subtype_ids=all_subtype_ids.ids
            )
            # keep a trace of existing mail
            existing_mail_ids = self.Mail.search([])
            # post message
            obj_id.message_post(body="Hello world")
            # get latest email
            mail_id = self.Mail.search([]) - existing_mail_ids
            self.assertEqual(len(mail_id), 1)
            self.assertEqual(
                mail_id.subject,
                "123456",
            )
            # udpate trace of existing mail
            existing_mail_ids = self.Mail.search([])
            # post another message
            obj_id.message_post(body="Hello world",record_name="Custom Name")
            # get latest email
            mail_id = self.Mail.search([]) - existing_mail_ids
            self.assertEqual(len(mail_id), 1)
            self.assertEqual(
                mail_id.subject,
                "Custom Name",
            )
        finally:
            self.mail_unlink_enabled()
