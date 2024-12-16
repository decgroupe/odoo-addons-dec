# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Dec 2024

import os

from datetime import datetime
from freezegun import freeze_time

import odoo.tests
from odoo import http

from .common import TestBasePermanentSessionCommon


@odoo.tests.tagged("post_install", "-at_install")
class TestBasePermanentSession(TestBasePermanentSessionCommon):

    def _create_multiple_sessions(self):
        non_permanent_headers = {"X-Odoo-Session-Permanent": "0"}
        permanent_headers = {"X-Odoo-Session-Permanent": "1"}
        res = []
        with freeze_time("2020-10-02"):
            # authenticate with user #A
            res.append(self._authenticate(0, permanent_headers).sid)
            # authenticate with user #B
            res.append(self._authenticate(1, non_permanent_headers).sid)
        with freeze_time("2021-01-30"):
            # authenticate with user #C
            res.append(self._authenticate(2, permanent_headers).sid)
            # authenticate with user #D
            res.append(self._authenticate(3, non_permanent_headers).sid)
        with freeze_time("2021-02-28"):
            # authenticate with user #E
            res.append(self._authenticate(4, permanent_headers).sid)
            # authenticate with user #F
            res.append(self._authenticate(5, non_permanent_headers).sid)
        with freeze_time("2021-03-02"):
            # authenticate with user #G
            res.append(self._authenticate(6, permanent_headers).sid)
            # authenticate with user #H
            res.append(self._authenticate(7, non_permanent_headers).sid)
        return res

    def setUp(self):
        super().setUp()

    def test_01_authenticate_standard_session(self):
        session = self._authenticate()
        self.assertFalse(session.permanent)
        for value in ["False", "false", "0", "off"]:
            session = self._authenticate(0, {"X-Odoo-Session-Permanent": value})
            self.assertFalse(session.permanent)
            # cleanup session folder
            http.root.session_store.delete(session)

    def test_02_authenticate_permanent_session(self):
        for value in ["True", "true", "1", "on"]:
            session = self._authenticate(0, {"X-Odoo-Session-Permanent": value})
            self.assertTrue(session.permanent)
            # cleanup session folder
            http.root.session_store.delete(session)

    def test_03_maintain_permanent_session(self):
        # set session expiry to 6 months
        session_expiry_delay = 86400 * 30 * 6
        # run session garbage collector
        self.env["ir.autovacuum"].gc_sessions(session_expiry_delay)
        # list existing sessions
        cur_sids = http.root.session_store.list()
        # create 8 sessions (4 permanents) for our 8 users at different dates
        new_sids = dict.fromkeys(self._create_multiple_sessions(), {})
        for sid, data in new_sids.items():
            fn = http.root.session_store.get_session_filename(sid)
            data["timestamp"] = os.path.getmtime(fn)
            data["timestamp_dt"] = datetime.fromtimestamp(data["timestamp"])
            data["human_timestamp"] = data["timestamp_dt"].strftime("%Y-%m-%d %H:%M:%S")
            print(sid, data)

        # run maintains and vaccum
        with freeze_time("2021-03-02"):
            self.env["ir.autovacuum"].maintain_permanent_sessions()
            self.env["ir.autovacuum"].gc_sessions(session_expiry_delay)

        # check sessions
        logins = []
        for sid, data in new_sids.items():
            fn = http.root.session_store.get_session_filename(sid)
            session = http.root.session_store.get(sid)
            logins.append(session.login)
            timestamp = os.path.getmtime(fn)
            timestamp_dt = datetime.fromtimestamp(timestamp)
            if session.login in ("userA", "userC", "userE", "userG"):
                self.assertTrue(session.permanent)
                self.assertEqual(timestamp_dt.year, 2021)
                self.assertEqual(timestamp_dt.month, 3)
                self.assertEqual(timestamp_dt.day, 2)
            else:
                self.assertFalse(session.permanent)
                if session.login == "userB":
                    self.assertEqual(timestamp_dt.year, 2020)
                    self.assertEqual(timestamp_dt.month, 10)
                    self.assertEqual(timestamp_dt.day, 2)
                elif session.login == "userD":
                    self.assertEqual(timestamp_dt.year, 2021)
                    self.assertEqual(timestamp_dt.month, 1)
                    self.assertEqual(timestamp_dt.day, 30)
                elif session.login == "userF":
                    self.assertEqual(timestamp_dt.year, 2021)
                    self.assertEqual(timestamp_dt.month, 2)
                    self.assertEqual(timestamp_dt.day, 28)
                elif session.login == "userH":
                    self.assertEqual(timestamp_dt.year, 2021)
                    self.assertEqual(timestamp_dt.month, 3)
                    self.assertEqual(timestamp_dt.day, 2)
                else:
                    raise Exception("Missing case ?")

        self.assertIn("userA", logins)
        self.assertIn("userB", logins)
        self.assertIn("userC", logins)
        self.assertIn("userD", logins)
        self.assertIn("userE", logins)
        self.assertIn("userF", logins)
        self.assertIn("userG", logins)
        self.assertIn("userH", logins)

        # run maintains and vaccum
        with freeze_time("2021-04-05"):
            self.env["ir.autovacuum"].maintain_permanent_sessions()
            self.env["ir.autovacuum"].gc_sessions(session_expiry_delay)

        # check sessions
        logins = []
        for sid, data in new_sids.items():
            fn = http.root.session_store.get_session_filename(sid)
            if not os.path.exists(fn):
                # expired sessions have been garbage collected
                continue
            session = http.root.session_store.get(sid)
            logins.append(session.login)
            timestamp = os.path.getmtime(fn)
            timestamp_dt = datetime.fromtimestamp(timestamp)
            if session.login in ("userA", "userC", "userE", "userG"):
                self.assertTrue(session.permanent)
                self.assertEqual(timestamp_dt.year, 2021)
                self.assertEqual(timestamp_dt.month, 4)
                self.assertEqual(timestamp_dt.day, 5)
            else:
                self.assertFalse(session.permanent)
                if session.login == "userD":
                    self.assertEqual(timestamp_dt.year, 2021)
                    self.assertEqual(timestamp_dt.month, 1)
                    self.assertEqual(timestamp_dt.day, 30)
                elif session.login == "userF":
                    self.assertEqual(timestamp_dt.year, 2021)
                    self.assertEqual(timestamp_dt.month, 2)
                    self.assertEqual(timestamp_dt.day, 28)
                elif session.login == "userH":
                    self.assertEqual(timestamp_dt.year, 2021)
                    self.assertEqual(timestamp_dt.month, 3)
                    self.assertEqual(timestamp_dt.day, 2)
                else:
                    raise Exception("Missing case ?")

        # ensure oldest non-permanent session have been removed
        self.assertIn("userA", logins)
        self.assertNotIn("userB", logins)
        self.assertIn("userC", logins)
        self.assertIn("userD", logins)
        self.assertIn("userE", logins)
        self.assertIn("userF", logins)
        self.assertIn("userG", logins)
        self.assertIn("userH", logins)

        # run maintains and vaccum
        with freeze_time("2021-09-03"):
            self.env["ir.autovacuum"].maintain_permanent_sessions()
            self.env["ir.autovacuum"].gc_sessions(session_expiry_delay)

        # check sessions
        logins = []
        for sid, data in new_sids.items():
            fn = http.root.session_store.get_session_filename(sid)
            if not os.path.exists(fn):
                # expired sessions have been garbage collected
                continue
            session = http.root.session_store.get(sid)
            logins.append(session.login)
            timestamp = os.path.getmtime(fn)
            timestamp_dt = datetime.fromtimestamp(timestamp)
            if session.login in ("userA", "userC", "userE", "userG"):
                self.assertTrue(session.permanent)
                self.assertEqual(timestamp_dt.year, 2021)
                self.assertEqual(timestamp_dt.month, 9)
                self.assertEqual(timestamp_dt.day, 3)
            else:
                raise Exception("Missing case ?")

        # ensure all non-permanent sessions have been removed
        self.assertIn("userA", logins)
        self.assertNotIn("userB", logins)
        self.assertIn("userC", logins)
        self.assertNotIn("userD", logins)
        self.assertIn("userE", logins)
        self.assertNotIn("userF", logins)
        self.assertIn("userG", logins)
        self.assertNotIn("userH", logins)

        # cleanup session folder
        for sid in new_sids:
            session = http.root.session_store.get(sid)
            http.root.session_store.delete(session)
