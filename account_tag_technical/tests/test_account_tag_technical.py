# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2023

import contextlib
from unittest.mock import Mock, patch

import odoo
from odoo.tests import new_test_user
from odoo.tests.common import TransactionCase
from odoo.tools.misc import DotDict


@contextlib.contextmanager
def MockDebugRequest(env):
    request = Mock(
        db=None,
        env=env,
        session=DotDict(
            debug=True,
        ),
    )
    with contextlib.ExitStack() as s:
        odoo.http._request_stack.push(request)
        s.callback(odoo.http._request_stack.pop)
        yield request


class TestAccountTagTechnical(TransactionCase):
    def setUp(self):
        super().setUp()
        ctx = {
            "mail_create_nolog": True,
            "mail_create_nosubscribe": True,
            "mail_notrack": True,
            "no_reset_password": True,
        }
        self.user = new_test_user(
            self.env,
            login="action_view-user",
            groups="account.group_account_invoice",
            context=ctx,
        )

    def test_01_technical_name(self):
        tag_financing = self.env.ref("account.account_tag_financing")
        tech_name = tag_financing.with_user(self.user).name_get()[0][1]
        self.assertEqual(tech_name, "Financing Activities")
        # enable technical group (not needed since base_user depends on it)
        self.env.ref("base.group_no_one").write({"users": [(4, self.user.id)]})
        self.assertTrue(self.user.has_group("base.group_no_one"))
        # retry with debug mode enabled in mocked http request
        with MockDebugRequest(self.env):
            tech_name = tag_financing.with_user(self.user).name_get()[0][1]
        self.assertEqual(tech_name, "Financing Activities [account_tag_financing]")
