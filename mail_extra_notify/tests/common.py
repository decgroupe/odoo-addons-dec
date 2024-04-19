# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2024

import logging

from odoo.tests.common import TransactionCase, tagged

_test_logger = logging.getLogger("odoo.tests")


@tagged("post_install", "-at_install")
class TestMailExtraNotifyCommon(TransactionCase):

    def setUp(self):
        super().setUp()
        self.Mail = self.env["mail.mail"]
        self.user1 = self.env.ref("base.user_demo")

    def mail_unlink_disabled(self):
        # disable automatic mail-deletion
        def unlink(self):
            _test_logger.warning("Unlink disabled for `mail.mail`")

        self.Mail._patch_method("unlink", unlink)

    def mail_unlink_enabled(self):
        # restore original method
        self.Mail._revert_method("unlink")
