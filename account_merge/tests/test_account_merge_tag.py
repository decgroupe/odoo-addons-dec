# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2023

from odoo.tests.common import TransactionCase


class TestAccountMergeTag(TransactionCase):
    def setUp(self):
        super().setUp()
        self.tag_model = self.env["account.account.tag"]
        self.merge_account_tag_wizard_model = self.env[
            "merge.account.account.tag.wizard"
        ]
        self.group_do_merge = self.env.ref("account_merge.res_group_do_merge")

    def test_01_merge(self):
        # get a first tag reference
        at1 = self.env.ref("account.account_tag_financing")
        # keep current data for future comparison
        at1_data = at1.read()[0]
        # get another tag reference that will be merged in to the first one
        at2 = self.env.ref("account.account_tag_investing")
        # edit some values
        at2.write({})
        # keep current data for future comparison
        at2_data = at2.read()[0]
        # execute merge
        wizard_id = self.merge_account_tag_wizard_model.create(
            {
                "object_ids": (at1 + at2).ids,
                "dst_object_id": at1.id,
            }
        )
        wizard_id.action_merge()
        self.assertTrue(at1.exists())
        self.assertFalse(at2.exists())
        at1_new_data = at1.read()[0]
        self.assertEqual(
            set(at1_data["account_ids"] + at2_data["account_ids"]),
            set(at1_new_data["account_ids"]),
        )
