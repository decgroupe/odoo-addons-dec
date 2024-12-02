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

TOMATO_TEMPLATE = """<?xml version="1.0"?>
<t t-name="mail_qweb.view_email_template_test">
    <style>.tomato {background-color: Tomato;}</style>
    <div class="tomato"><t t-esc="subject"/></div>
    <div><t t-raw="ctx.get('email_message')"/></div>
</t>"""


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
        # mail qweb template and its view
        self.mail_view_id = self.env["ir.ui.view"].create(
            {
                "name": "mail_qweb.view_email_template_test",
                "type": "qweb",
                "arch_base": '<?xml version="1.0"?>'
                '<t t-name="mail_qweb.view_email_template_test">'
                "</t>",
            }
        )
        self.mail_template_id = self.env["mail.template"].create(
            {
                "name": "Custom template",
                "model_id": self.env.ref("base.model_res_users").id,
                "email_from": "${object.user_id.email_formatted |safe}",
                "email_to": "${object.user_id.email}",
                "auto_delete": True,
                "subject": "Template Test",
                "body_type": "qweb",
                "body_view_id": self.mail_view_id.id,
                "lang": "${object.user_id.lang}",
            }
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

    def test_05_send_qweb_mail_template_with_inline_css(self):
        ctx = {"email_message": "This is the message"}
        try:
            self.mail_unlink_disabled()
            self.mail_view_id.arch_base = TOMATO_TEMPLATE
            mail_id = self.mail_template_id.with_context(**ctx).send_mail(
                self.user.id,
                force_send=True,
                email_values={"email_to": self.user.email},
            )
            mail_id = self.env["mail.mail"].browse(mail_id)
            clean_body = " ".join(mail_id.body_html.split())
            self.assertEqual(
                clean_body,
                "<html> <head></head> <body> "
                '<div class="tomato" style="background-color:Tomato" bgcolor="Tomato">'
                "Template Test</div> "
                "<div>This is the message</div> "
                "</body> </html>",
            )
        finally:
            self.mail_unlink_enabled()

    def test_06_send_qweb_mail_template_without_inline_css(self):

        def mail_it():
            mail_id = self.mail_template_id.with_context(**ctx).send_mail(
                self.user.id,
                force_send=True,
                email_values={"email_to": self.user.email},
            )
            mail_id = self.env["mail.mail"].browse(mail_id)
            # remove extra spaces and new line characters
            clean_body = " ".join(mail_id.body_html.split())
            self.assertEqual(
                clean_body,
                "<style>.tomato {background-color: Tomato;}</style> "
                '<div class="tomato">Template Test</div> '
                "<div>This is the message</div>",
            )

        ctx = {"email_message": "This is the message"}
        try:
            self.mail_unlink_disabled()
            self.mail_view_id.arch_base = TOMATO_TEMPLATE
            self.mail_template_id.no_inline_css = True
            mail_it()
            # re-enable inline css but user context to disable it
            self.mail_template_id.no_inline_css = False
            ctx["no_inline_css"] = True
            mail_it()
        finally:
            self.mail_unlink_enabled()

    def test_07_send_qweb_mail_template_with_local_links(self):
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        self.assertTrue(base_url.startswith("http"))
        ctx = {
            "email_message": '<a href="/downloads/package.zip">Click me to download this archive</a>'
        }
        try:
            self.mail_unlink_disabled()
            self.mail_view_id.arch_base = TOMATO_TEMPLATE
            mail_id = self.mail_template_id.with_context(**ctx).send_mail(
                self.user.id,
                force_send=True,
                email_values={"email_to": self.user.email},
            )
            mail_id = self.env["mail.mail"].browse(mail_id)
            clean_body = " ".join(mail_id.body_html.split())
            self.assertEqual(
                clean_body,
                "<html> <head></head> <body> "
                '<div class="tomato" style="background-color:Tomato" bgcolor="Tomato">'
                "Template Test</div> "
                '<div><a href="%s/downloads/package.zip">'
                "Click me to download this archive</a></div> "
                "</body> </html>" % (base_url),
            )
        finally:
            self.mail_unlink_enabled()
