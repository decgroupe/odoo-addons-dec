# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2025

from odoo.tests.common import TransactionCase


class TestMailChannelPrefix(TransactionCase):

    def setUp(self):
        super().setUp()
        self.channel_general = self.env.ref("mail.channel_all_employees")

    def test_01_prefix_removal(self):
        subjects = [
            "Re: test",
            "RE: test",
            "Fw: test",
            "FW: test",
            "Fwd: test",
            "FWD: test",
            "Re:test",
            "RE:test",
            "Fw:test",
            "FW:test",
            "Fwd:test",
            "FWD:test",
            "Re :test",
            "RE :test",
            "Fw :test",
            "FW :test",
            "Fwd :test",
            "FWD :test",
            "Re : test",
            "RE : test",
            "Fw : test",
            "FW : test",
            "Fwd : test",
            "FWD : test",
            "test",
        ]
        for subject in subjects:
            self.assertEqual(
                self.env["mail.channel"]._remove_subject_client_prefix(subject),
                "test",
                "Prefix not removed from subject: %s" % subject,
            )

    def test_02_not_a_prefix(self):
        subjects = [
            "Renault Megane",
            "RENAULT CLIO",
            "Re Tour",
        ]
        for subject in subjects:
            self.assertEqual(
                self.env["mail.channel"]._remove_subject_client_prefix(subject),
                subject,
                "Subject must not be altered: %s" % subject,
            )

    def test_03_post_message(self):
        self.channel_general.subject_prefix = "[GENERAL]"
        self.channel_general.message_post(subject="Re: test", body="test")
        last_message_id = self.channel_general.message_ids[0]
        self.assertEqual(
            last_message_id.subject,
            "[GENERAL] test",
            "Subject not prefixed: %s" % last_message_id.subject,
        )
        print(1)
