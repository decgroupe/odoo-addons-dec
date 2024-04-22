# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2024

from odoo.addons.mail.tests.common import MailCase
from odoo.addons.mail_above_line.tests.common import MSG_REPLY
from odoo.tests import tagged
from odoo.tests.common import SavepointCase
from odoo.tools import mute_logger


@tagged("mail_thread", "mail_gateway")
class TestMailAboveLine(SavepointCase, MailCase):
    def setUp(self):
        super().setUp()
        self.env["ir.config_parameter"].sudo().set_param(
            "mail.catchall.domain", "yourcompany.com"
        )
        self.user1 = self.env.ref("base.user_demo")
        # Azure Interior, Brandon Freeman
        self.partner_id = self.env.ref("base.res_partner_address_15")
        # assign an activity to this partner
        _activity_id, msg_id = self._assign_activity(self.partner_id, self.user1)
        self.msg_activity_notification_id = msg_id

    def _assign_activity_to_user(self, partner_id, user_id):
        # we cannot rely on `message_ids` since message with
        # `type == user_notification` are excluded by the field domain
        prev_msg_ids = self.env["mail.message"].search(
            [
                ("model", "=", partner_id._name),
                ("res_id", "=", partner_id.id),
            ]
        )
        activity_id = partner_id.activity_schedule(
            act_type_xmlid="mail.mail_activity_data_todo",
            summary="Contact again",
            note="Please go on site ASAP to fix Brandon's issue",
            user_id=user_id.id,
        )
        new_msg_ids = self.env["mail.message"].search(
            [
                ("model", "=", partner_id._name),
                ("res_id", "=", partner_id.id),
            ]
        )
        msg_id = new_msg_ids - prev_msg_ids
        self.assertEqual(1, len(msg_id))
        return activity_id, msg_id

    @mute_logger("odoo.addons.mail.models.mail_thread")
    def test_01_incoming_reply(self):
        # replace Message-Id to ensure that odoo will route our incoming e-mail as a
        # reply to the acitivty assigned notification
        incoming_message = MSG_REPLY.replace(
            "<673696096375914.1713787777.469944715499878-openerp-message-notify@myhostname>",
            self.msg_activity_notification_id.message_id,
        )
        prev_msg_ids = self.partner_id.message_ids
        record_id = self.env["mail.thread"].message_process(None, incoming_message)
        msg_id = self.partner_id.message_ids - prev_msg_ids
        self.assertEqual(1, len(msg_id))
        self.assertEqual(self.partner_id.id, record_id)
        self.assertNotIn("##- Please type your reply above this line -##", msg_id.body)
        self.assertIn("##- Content Removed -##", msg_id.body)
