# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2025

from odoo.tests.common import TransactionCase


class TestMailGroupPrefix(TransactionCase):
    def setUp(self):
        super().setUp()
        self.group_general = self.env.ref("mail.channel_all_employees")

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
                self.env["mail.group"]._remove_subject_client_prefix(subject),
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
                self.env["mail.group"]._remove_subject_client_prefix(subject),
                subject,
                "Subject must not be altered: %s" % subject,
            )

    def test_03_post_message_no_prefix_no_subject(self):
        self.group_general.subject_prefix = False
        self.group_general.message_post(subject="", body="test")
        last_message_id = self.group_general.message_ids[0]
        self.assertFalse(last_message_id.subject)

    def test_04_post_message_no_prefix_spaceonly_subject(self):
        self.group_general.subject_prefix = False
        self.group_general.message_post(subject="   ", body="test")
        last_message_id = self.group_general.message_ids[0]
        self.assertFalse(last_message_id.subject)

    def test_05_post_message_no_prefix(self):
        self.group_general.subject_prefix = False
        self.group_general.message_post(subject="Re: test", body="test")
        last_message_id = self.group_general.message_ids[0]
        self.assertEqual(last_message_id.subject, "test")

    def test_06_post_message_prefix_no_subject(self):
        self.group_general.subject_prefix = "[GENERAL]"
        self.group_general.message_post(subject="", body="test")
        last_message_id = self.group_general.message_ids[0]
        self.assertEqual(last_message_id.subject, "[GENERAL]")

    def test_06_post_message_prefix_spaceonly_subject(self):
        self.group_general.subject_prefix = "[GENERAL]"
        self.group_general.message_post(subject="   ", body="test")
        last_message_id = self.group_general.message_ids[0]
        self.assertEqual(last_message_id.subject, "[GENERAL]")

    def test_08_post_message_prefix_subject(self):
        self.group_general.subject_prefix = "[GENERAL]"
        self.group_general.message_post(subject="Re: test", body="test")
        last_message_id = self.group_general.message_ids[0]
        self.assertEqual(last_message_id.subject, "[GENERAL] test")

    def test_09_post_message_prefix_subject_prefixed(self):
        self.group_general.subject_prefix = "[GENERAL]"
        self.group_general.message_post(subject="[GENERAL] Re: test", body="test")
        last_message_id = self.group_general.message_ids[0]
        self.assertEqual(last_message_id.subject, "[GENERAL] Re: test")
