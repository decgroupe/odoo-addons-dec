# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2024

from datetime import datetime
import re

from dateutil.relativedelta import relativedelta

from odoo.exceptions import UserError
from odoo.tests import Form, new_test_user
from odoo.tests.common import TransactionCase

from contextlib import contextmanager


class TestSaleLockable(TransactionCase):

    def setUp(self):
        super().setUp()
        self.sale_order = self.env["sale.order"]
        self.sale_order_line = self.env["sale.order.line"]
        # create users
        ctx = {
            "mail_create_nolog": True,
            "mail_create_nosubscribe": True,
            "mail_notrack": True,
            "no_reset_password": True,
        }
        self.so_user1 = new_test_user(
            self.env,
            login="so_user1",
            groups="sales_team.group_sale_manager",
            context=ctx,
        )
        self.so_user2 = new_test_user(
            self.env,
            login="so_user2",
            groups="sales_team.group_sale_manager",
            context=ctx,
        )
        # create a sale order
        self.order_id = self.env["sale.order"].create(
            {
                "partner_id": self.env.ref("base.res_partner_10").id,
                "user_id": self.so_user1.id,
                "date_order": (datetime.now() - relativedelta(days=65)).strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
            }
        )

    def test_01_unset_order_user(self):
        self.order_id.user_id = False
        with self.assertRaisesRegex(
            UserError,
            r"A salesperson must be set before locking a sale order",
        ), self.cr.savepoint():
            self.order_id.with_user(self.so_user1).action_draft_lock()
        # unlock when not locked should not raise anything
        self.order_id.with_user(self.so_user1).action_draft_unlock()

    def test_02_lock_unlock(self):
        self.order_id.with_user(self.so_user1).action_draft_lock()
        self.order_id.with_user(self.so_user1).action_draft_unlock()

    def test_03_lock_another_user(self):
        self.assertFalse(self.order_id.locked_draft)
        # try lock with another user
        with self.assertRaisesRegex(
            UserError,
            rf"Only {re.escape(self.so_user1.name)} or an Administrator can "
            "lock/unlock this quotation",
        ), self.cr.savepoint():
            self.order_id.with_user(self.so_user2).action_draft_lock()

    def test_04_unlock_another_user(self):
        # unlock when not locked should not raise anything
        self.order_id.with_user(self.so_user2).action_draft_unlock()
        self.assertFalse(self.order_id.locked_draft)
        # lock with correct user
        self.order_id.invalidate_cache()
        self.order_id.with_user(self.so_user1).action_draft_lock()
        # try unlock with another user
        with self.assertRaisesRegex(
            UserError,
            rf"Only {re.escape(self.so_user1.name)} or an Administrator can "
            "lock/unlock this quotation",
        ), self.cr.savepoint():
            self.order_id.invalidate_cache()
            self.order_id.with_user(self.so_user2).action_draft_unlock()

    def test_05_edit_when_locked(self):
        self.order_id.with_user(self.so_user1).action_draft_lock()
        self.order_id.with_user(self.so_user1).date_order = datetime.now()
        self.assertIn("date_order", self.order_id._get_lockable_fields())
        with self.assertRaisesRegex(
            UserError,
            rf"is currently locked, you are not allowed to make changes to .*",
        ), self.cr.savepoint():
            self.order_id.invalidate_cache()
            self.order_id.with_user(self.so_user2).date_order = datetime.now()

    def test_06_unlock_on_confirm(self):
        self.order_id.with_user(self.so_user1).action_draft_lock()
        self.assertTrue(self.order_id.locked_draft)
        self.order_id.with_user(self.so_user1).action_confirm()
        self.assertFalse(self.order_id.locked_draft)
        # try edit with another user
        self.order_id.invalidate_cache()
        self.order_id.with_user(self.so_user2).date_order = datetime.now()
