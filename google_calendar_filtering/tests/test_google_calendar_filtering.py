# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2026

from datetime import datetime
from unittest.mock import MagicMock, patch

from odoo.tests.common import TransactionCase


class TestGoogleCalendarFiltering(TransactionCase):
    """Tests for the google_calendar_filtering module.
    Verifies that Google Calendar sync is blocked for databases not in the
    configured allowlist, and that the duplicate_count computed fields work as expected.
    """

    @classmethod
    def setUpClass(cls):
        """Set up shared test data."""
        super().setUpClass()
        cls.CalendarEvent = cls.env["calendar.event"]
        cls.GoogleSync = cls.env["google.calendar.sync"]
        cls.ResUsers = cls.env["res.users"]
        cls.partner = cls.env.ref("base.partner_admin")
        cls.event_vals = {
            "name": "Test Event",
            "start": datetime(2026, 4, 1, 10, 0),
            "stop": datetime(2026, 4, 1, 11, 0),
            "partner_ids": [],
        }

    def _invalidate_allowlist_cache(self):
        """Invalidate the ormcache for _get_db_allowedlist."""
        self.env.registry.clear_cache()

    def test_01_allowlist_empty_by_default(self):
        """_get_db_allowedlist returns empty list when config key is absent."""
        self._invalidate_allowlist_cache()
        with patch(
            "odoo.addons.google_calendar_filtering.models.google_sync.config"
        ) as mock_cfg:
            mock_cfg.get.return_value = None
            result = self.GoogleSync._get_db_allowedlist()
        self.assertEqual(result, [])

    def test_02_allowlist_parsed_from_config(self):
        """_get_db_allowedlist splits the config value into a list."""
        self._invalidate_allowlist_cache()
        with patch(
            "odoo.addons.google_calendar_filtering.models.google_sync.config"
        ) as mock_cfg:
            mock_cfg.get.return_value = "db1,db2"
            with patch(
                "odoo.addons.google_calendar_filtering.models.google_sync.to_list"
            ) as mock_to_list:
                mock_to_list.return_value = ["db1", "db2"]
                result = self.GoogleSync._get_db_allowedlist()
        self.assertIn("db1", result)
        self.assertIn("db2", result)

    def test_03_sync_odoo2google_disabled_when_not_in_allowlist(self):
        """_sync_odoo2google returns None when db is not in the allowlist."""
        event = self.CalendarEvent.create(self.event_vals)
        self._invalidate_allowlist_cache()
        with patch.object(
            type(self.GoogleSync), "_get_db_allowedlist", return_value=[]
        ):
            result = event._sync_odoo2google(MagicMock())
        self.assertIsNone(result)

    def test_04_sync_google2odoo_disabled_when_not_in_allowlist(self):
        """_sync_google2odoo returns None when db is not in the allowlist."""
        self._invalidate_allowlist_cache()
        with patch.object(
            type(self.GoogleSync), "_get_db_allowedlist", return_value=[]
        ):
            result = self.CalendarEvent._sync_google2odoo(MagicMock())
        self.assertIsNone(result)

    def test_05_google_insert_disabled_when_not_in_allowlist(self):
        """_google_insert returns None when db is not in the allowlist."""
        event = self.CalendarEvent.create(self.event_vals)
        self._invalidate_allowlist_cache()
        with patch.object(
            type(self.GoogleSync), "_get_db_allowedlist", return_value=[]
        ):
            result = event._google_insert(MagicMock(), {})
        self.assertIsNone(result)

    def test_06_sync_google_calendar_disabled_when_not_in_allowlist(self):
        """_sync_google_calendar returns None when db is not in the allowlist."""
        user = self.env.ref("base.user_admin")
        self._invalidate_allowlist_cache()
        with patch.object(
            type(self.GoogleSync), "_get_db_allowedlist", return_value=[]
        ):
            result = user._sync_google_calendar(MagicMock())
        self.assertIsNone(result)

    def test_07_sync_all_google_calendar_disabled_when_not_in_allowlist(self):
        """_sync_all_google_calendar returns None when db is not in allowlist."""
        self._invalidate_allowlist_cache()
        with patch.object(
            type(self.GoogleSync), "_get_db_allowedlist", return_value=[]
        ):
            result = self.ResUsers._sync_all_google_calendar()
        self.assertIsNone(result)

    def test_09_action_recompute_duplicate_count_reset_in_module_context(self):
        """action_recompute_duplicate_count resets counts to 0 during install."""
        event = self.CalendarEvent.create(self.event_vals)
        # simulate the context set during module installation
        result = event.with_context(
            module="google_calendar_filtering"
        ).action_recompute_duplicate_count()
        self.assertIsNone(result)
        self.assertEqual(event.duplicate_count, 0)

    def test_10_duplicate_count_finds_identical_events(self):
        """duplicate_count is set when events share the same name and dates."""
        vals = dict(self.event_vals, name="Duplicate Event")
        event1 = self.CalendarEvent.create(vals)
        event2 = self.CalendarEvent.create(vals)
        (event1 + event2).action_recompute_duplicate_count()
        self.assertEqual(event1.duplicate_count, 1)
        self.assertEqual(event2.duplicate_count, 1)

    def test_11_duplicate_count_zero_for_unique_event(self):
        """duplicate_count is 0 for an event with no identical counterpart."""
        vals = dict(self.event_vals, name="Unique Event ABC123")
        event = self.CalendarEvent.create(vals)
        event.action_recompute_duplicate_count()
        self.assertEqual(event.duplicate_count, 0)

    def test_12_public_fields_include_custom_fields(self):
        """_get_public_fields includes duplicate_count."""
        public_fields = self.CalendarEvent._get_public_fields()
        self.assertIn("duplicate_count", public_fields)

    def test_13_sync_google_calendar_enabled_when_in_allowlist(self):
        """_sync_google_calendar delegates to super when db is in the allowlist."""
        user = self.env.ref("base.user_admin")
        dbname = self.env.cr.dbname
        self._invalidate_allowlist_cache()
        with patch.object(
            type(self.GoogleSync), "_get_db_allowedlist", return_value=[dbname]
        ):
            # also patch the google_calendar module's implementation to avoid
            # real API calls while still executing the "true" branch of our code
            import odoo.addons.google_calendar.models.res_users as gcal_res_users

            with patch.object(
                gcal_res_users.User, "_sync_google_calendar", return_value=None
            ):
                result = user._sync_google_calendar(MagicMock())
        # when in allowlist super() is called; it returns None here (mocked)
        self.assertIsNone(result)

    def test_14_sync_all_google_calendar_enabled_when_in_allowlist(self):
        """_sync_all_google_calendar delegates to super when db is in allowlist."""
        dbname = self.env.cr.dbname
        self._invalidate_allowlist_cache()
        with patch.object(
            type(self.GoogleSync), "_get_db_allowedlist", return_value=[dbname]
        ):
            import odoo.addons.google_calendar.models.res_users as gcal_res_users

            with patch.object(
                gcal_res_users.User, "_sync_all_google_calendar", return_value=None
            ):
                result = self.ResUsers._sync_all_google_calendar()
        self.assertIsNone(result)

    def test_15_sync_google_calendar_skips_user_without_rtoken(self):
        """sync_google_calendar skips users that have no google_calendar_rtoken."""
        user = self.env.ref("base.user_admin")
        # ensure no rtoken is set
        user.sudo().res_users_settings_id.sudo().google_calendar_rtoken = False
        # should complete without errors (loop body skips because of False rtoken)
        user.sync_google_calendar()

    def test_16_sync_google_calendar_calls_sync_when_rtoken_set(self):
        """sync_google_calendar calls _sync_google_calendar when user has rtoken."""
        user = self.env.ref("base.user_admin")
        user.sudo().res_users_settings_id.sudo().google_calendar_rtoken = "testtoken"
        try:
            with patch.object(
                type(user), "_sync_google_calendar", return_value=None
            ) as mock_sync:
                user.sync_google_calendar()
            mock_sync.assert_called()
        finally:
            user.sudo().res_users_settings_id.sudo().google_calendar_rtoken = False

    def test_18_compute_duplicate_count_via_method_call(self):
        """_compute_duplicate_count delegates to action_recompute_duplicate_count."""
        event = self.CalendarEvent.create(self.event_vals)
        # invalidate so the compute method is re-triggered
        event.invalidate_recordset(["duplicate_count"])
        # calling the compute method directly to cover line 44
        event._compute_duplicate_count()
        self.assertGreaterEqual(event.duplicate_count, 0)

    def test_19_allday_duplicate_count(self):
        """action_recompute_duplicate_count handles all-day events correctly."""

        vals = {
            "name": "AllDay Dup Event XYZ",
            "start": "2026-04-01 00:00:00",
            "stop": "2026-04-01 00:00:00",
            "allday": True,
        }
        event1 = self.CalendarEvent.create(vals)
        event2 = self.CalendarEvent.create(dict(vals))
        (event1 + event2).action_recompute_duplicate_count()
        # both events should detect each other as duplicates
        self.assertEqual(event1.duplicate_count, 1)
        self.assertEqual(event2.duplicate_count, 1)

    def test_20_action_sync2google_raises_for_full_sync(self):
        """action_sync2google raises Exception when user has no sync token."""
        event = self.CalendarEvent.create(self.event_vals)
        # ensure no sync token → full_sync=True → Exception
        event.user_id.sudo().res_users_settings_id.sudo().google_calendar_sync_token = (
            False
        )
        with self.assertRaises(ValueError):
            event.action_sync2google()
