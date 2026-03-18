# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2026

from unittest.mock import patch

from odoo.tests.common import TransactionCase

from odoo.addons.wizard_run.wizard import wizard_run as wizard_run_module


class _FakeThread:
    """fake thread used to inspect run behavior without starting real threads."""

    last_instance = None

    def __init__(self, target=None, *args, **kwargs):
        """store target and instantiation metadata for assertions."""
        self.target = target
        self.args = args
        self.kwargs = kwargs
        self.started = False
        _FakeThread.last_instance = self

    def start(self):
        """simulate thread start without executing asynchronous code."""
        self.started = True


class TestWizardRun(TransactionCase):
    """Tests for the `wizard_run` module."""

    def test_01_base_methods_must_be_overridden(self):
        """Base wizard methods should raise until specialized by inherited wizards."""
        wizard = self.env["wizard.run"].create({})
        with self.assertRaises(NotImplementedError):
            wizard.pre_execute()
        with self.assertRaises(NotImplementedError):
            wizard.execute()

    def test_02_run_returns_close_action_and_starts_thread(self):
        """Run should call pre_execute, start a thread, and close the wizard window."""
        wizard = self.env["wizard.generate_user_random_signature"].create({})
        _FakeThread.last_instance = None
        with patch.object(wizard_run_module.threading, "Thread", _FakeThread):
            action = wizard.run()
        thread = _FakeThread.last_instance
        self.assertIsNotNone(thread)
        self.assertTrue(thread.started)
        self.assertEqual(action["type"], "ir.actions.act_window_close")

    def test_03_execute_generates_signature_for_users(self):
        """Execute should generate html signatures for users."""
        user = self.env.ref("base.user_admin")
        user.signature = False
        wizard = self.env["wizard.generate_user_random_signature"].create({})
        wizard.execute()
        user.invalidate_recordset(["signature"])
        self.assertTrue(user.signature)
        self.assertIn("This signature was generated randomly by module", user.signature)
        self.assertIn("Generated on", user.signature)
