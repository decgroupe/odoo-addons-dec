# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2023


from odoo.tests import common


class TestTaggingCommon(common.TransactionCase):
    """ """

    def setUp(self):
        super().setUp()
        self.model = self.env["tagging.tags"]
        self.tag_1 = self.env.ref("tagging.tag_01")
        self.tag_2 = self.env.ref("tagging.tag_02")
        self.tag_3 = self.env.ref("tagging.tag_03")
        self.tag_4 = self.env.ref("tagging.tag_04")