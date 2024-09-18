# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2024

import base64

from odoo.tests.common import TransactionCase


class TestMailAttachmentCommon(TransactionCase):

    def setUp(self):
        super().setUp()
        self.base_url = self.env["ir.config_parameter"].get_param("web.base.url")
        self.attachment = self.env["ir.attachment"]
        bin_data = base64.b64encode(b"\xff data")
        self.attachment_id = self.attachment.create(
            {
                "name": "MyAttachment",
                "datas": bin_data,
            }
        )
        # Azure Interior, Brandon Freeman
        self.partner_id = self.env.ref("base.res_partner_address_15")
