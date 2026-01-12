# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2024

from odoo.tests import tagged
from odoo.tests.common import TransactionCase
from odoo.tools import mute_logger

from odoo.addons.crm_lead_new_email.tests.common import MAIL_TEMPLATE, MSG_CONTACT
from odoo.addons.mail.tests.common import MailCase


@tagged("mail_thread", "mail_gateway", "post_install", "-at_install")
class TestCrmLeadNewEmail(TransactionCase, MailCase):
    """Test CRM Lead New Email functionalities"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Create company default alias domain (replacing `mail.catchall.domain` param)
        cls.env["mail.alias.domain"].create(
            {
                "name": "yourcompany.com",
                "bounce_alias": "bounce",
                "catchall_alias": "catchall",
            }
        )
        cls.env["mail.alias"].create(
            {
                "alias_name": "contact",
                "alias_model_id": cls.env["ir.model"]._get("crm.lead").id,
                "alias_parent_model_id": cls.env["ir.model"]._get("crm.team").id,
                "alias_defaults": "{'type': 'lead', 'company_id':1}",
            }
        )

    def setUp(self):
        super().setUp()

    @mute_logger("odoo.addons.mail.models.mail_thread")
    def test_01_incoming_reply_from_unknown_contact(self):
        incoming_message = MSG_CONTACT
        prev_mail_ids = self.env["mail.mail"].search([])
        _record_id = self.env["mail.thread"].message_process(None, incoming_message)
        mail_id = self.env["mail.mail"].search([]) - prev_mail_ids
        self.assertEqual(
            "✨ New Lead: Need information about your products", mail_id.subject
        )
        self.assertIn('No match found for "Xan Yin Zu (myhostname)"', mail_id.body)
        self.assertIn("Can you contact me at xyz@widget.com ?", mail_id.body)
        self.assertIn("Open Lead", mail_id.body)

    @mute_logger("odoo.addons.mail.models.mail_thread")
    def test_02_incoming_reply_from_known_contact(self):
        _partner_id = self.env["res.partner"].create(
            {
                "name": "Xan Yin Zu",
                "email": "xyz@widget.com",
            }
        )
        incoming_message = MSG_CONTACT
        prev_mail_ids = self.env["mail.mail"].search([])
        _record_id = self.env["mail.thread"].message_process(None, incoming_message)
        mail_id = self.env["mail.mail"].search([]) - prev_mail_ids
        self.assertEqual(
            "✨ New Lead: Need information about your products", mail_id.subject
        )
        self.assertNotIn('No match found for "Xan Yin Zu (myhostname)"', mail_id.body)

    @mute_logger("odoo.addons.mail.models.mail_thread")
    def test_03_incoming_html_body(self):
        subject = "Need information about your products"
        incoming_message = MAIL_TEMPLATE.format(
            subject=subject,
            email_from="xyz@widget.com",
            to="contact@yourcompany.com",
            cc="",
            msg_id="<58976bdf-e97b-4c3a-a103-2888d10615fd@widget.com>",
            extra="",
        )
        record_id = self.env["mail.thread"].message_process(None, incoming_message)
        lead_id = self.env["crm.lead"].browse(record_id)
        self.assertEqual(lead_id.name, subject)
        # ensure html is converted to plaintext
        self.assertNotIn("</body>", lead_id.description)
