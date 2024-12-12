# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Dec 2024

from odoo import http
from odoo.tests import new_test_user
from odoo.tests.common import TransactionCase


class TestBasePermanentSessionCommon(TransactionCase):

    def setUp(self):
        super().setUp()
        self.base_url = self.env["ir.config_parameter"].get_param("web.base.url")
        ctx = {
            "mail_create_nolog": True,
            "mail_create_nosubscribe": True,
            "mail_notrack": True,
            "no_reset_password": True,
        }
        self.user_login = "newuser@mycompany.com"
        self.user_password = "bi68NmKq8YME"
        self.user = new_test_user(
            self.env,
            login=self.user_login,
            groups="base.group_user",
            context=ctx,
        )
        self.user.password = self.user_password

    def _get_crsf_token(self):
        # Get csrf_token
        self.authenticate(None, None)
        csrf_token = http.WebRequest.csrf_token(self)
        return csrf_token
