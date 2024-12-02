# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2024

import logging

from freezegun import freeze_time
from odoo_test_helper import FakeModelLoader

from odoo import fields
from odoo.tests import new_test_user
from odoo.tests.common import SavepointCase

from ..models.mail_template import remaining_days

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
        from .models import FakeModel, FakeModelWithoutName

        cls.loader.update_registry(
            (
                FakeModel,
                FakeModelWithoutName,
            )
        )
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
            obj_id.message_post(body="Hello world", record_name="Custom Name")
            # get latest email
            mail_id = self.Mail.search([]) - existing_mail_ids
            self.assertEqual(len(mail_id), 1)
            self.assertEqual(
                mail_id.subject,
                "Custom Name",
            )
        finally:
            self.mail_unlink_enabled()

    def _message_post(self, record_id, body):
        """Help to post a new message and get the corresponding email in return"""
        # keep a trace of existing mail
        existing_mail_ids = self.Mail.search([])
        # post basic message
        record_id.message_post(body=body)
        # get latest email
        mail_id = self.Mail.search([]) - existing_mail_ids
        self.assertEqual(len(mail_id), 1)
        return mail_id

    def test_02_content_alignment(self):
        try:
            self.mail_unlink_disabled()
            # create record and subscribe our user to all possible subtypes
            obj_id = self.env["fake.model"].create({"name": "myrecord"})
            all_subtype_ids = self.env["mail.message.subtype"].search([])
            obj_id.message_subscribe(
                [self.user.partner_id.id], subtype_ids=all_subtype_ids.ids
            )
            # basic message
            mail_id = self._message_post(
                obj_id, body="Please take a look on this simple message"
            )
            # big message with more than 128 characters
            mail_id = self._message_post(
                obj_id,
                body="Please take a look on this big message with a lot of characters."
                "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vivamus in "
                "metus nec erat auctor volutpat eget id nibh. Etiam sodales justo nec "
                "orci euismod, eu rutrum mauris vulputate. Curabitur iaculis purus "
                "lectus, ut tincidunt odio euismod sed. Vestibulum vel nulla eget odio "
                "aliquet congue. Vestibulum pharetra a nisl a varius.",
            )
            # basic message with basic text format
            mail_id = self._message_post(
                obj_id,
                body="Please take a <b>look</b> on this <i>simple message</i>"
                "<br /> Some text is in bold",
            )
            # basic message with advanced html text formatting
            mail_id = self._message_post(
                obj_id,
                body="Please take a <b>look</b> on this <i>simple message</i>"
                "<br /> Some text can be in: <br />"
                "<ul>"
                "<li>bold</li>"
                "<li>italic</li>"
                "</ul>",
            )

        finally:
            self.mail_unlink_enabled()

    def test_03_empty_message(self):
        try:
            self.mail_unlink_disabled()
            # create record and subscribe our user to all possible subtypes
            obj_id = self.env["fake.model"].create({"name": "myrecord"})
            all_subtype_ids = self.env["mail.message.subtype"].search([])
            obj_id.message_subscribe(
                [self.user.partner_id.id], subtype_ids=all_subtype_ids.ids
            )
            # empty messages should not raised any exceptions
            self._message_post(obj_id, body=False)
            self._message_post(obj_id, body="")
            self._message_post(obj_id, body=" ")
            self._message_post(obj_id, body=" \n\n ")
        finally:
            self.mail_unlink_enabled()

    @freeze_time("2024-12-02 11:00:00")
    def test_04_remaining_days(self):
        """Use Odoo standard for date formatting: '%Y-%m-%d'"""
        obj_id = self.env["fake.model"].create({"name": "myrecord"})
        self.assertEqual(
            remaining_days(obj_id, fields.Date.to_date("2024-08-24")), "08/24/2024"
        )
        self.assertEqual(
            remaining_days(obj_id, fields.Date.to_date("2024-08-25")), "99 days ago"
        )
        self.assertEqual(
            remaining_days(obj_id, fields.Date.to_date("2024-09-01")), "92 days ago"
        )
        self.assertEqual(
            remaining_days(obj_id, fields.Date.to_date("2024-12-01")), "Yesterday"
        )
        self.assertEqual(
            remaining_days(obj_id, fields.Date.to_date("2024-12-02")), "Today"
        )
        self.assertEqual(
            remaining_days(obj_id, fields.Date.to_date("2024-12-03")), "Tomorrow"
        )
        self.assertEqual(
            remaining_days(obj_id, fields.Date.to_date("2024-12-04")), "In 2 days"
        )
        self.assertEqual(
            remaining_days(obj_id, fields.Date.to_date("2025-02-28")), "In 88 days"
        )
        self.assertEqual(
            remaining_days(obj_id, fields.Date.to_date("2025-02-28")), "In 88 days"
        )
        self.assertEqual(
            remaining_days(obj_id, fields.Date.to_date("2025-03-11")), "In 99 days"
        )
        self.assertEqual(
            remaining_days(obj_id, fields.Date.to_date("2025-03-12")), "03/12/2025"
        )
