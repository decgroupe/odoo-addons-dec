# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2024

import logging
from contextlib import contextmanager
from unittest.mock import patch

from odoo.tests.common import TransactionCase, tagged

_test_logger = logging.getLogger("odoo.tests")


@tagged("post_install", "-at_install")
class TestMailExtraNotifyCommon(TransactionCase):
    def setUp(self):
        super().setUp()
        self.Mail = self.env["mail.mail"]
        self.user1 = self.env.ref("base.user_demo")

    @contextmanager
    def patch_mail_unlink(self):
        """ """
        _origin = type(self.Mail).unlink

        def _disabled_unlink(self):
            _test_logger.warning("Unlink disabled for `mail.mail`")

        with patch.object(type(self.Mail), "unlink", _disabled_unlink):
            yield
