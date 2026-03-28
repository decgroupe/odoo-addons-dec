# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2026

from odoo.tests.common import TransactionCase


class TestFetchmailFiltering(TransactionCase):
    """Tests for fetchmail_filtering module."""

    @classmethod
    def setUpClass(cls):
        """Set up shared test data."""
        super().setUpClass()
        cls.Server = cls.env["fetchmail.server"]
        cls.server_wildcard = cls.Server.create(
            {
                "name": "Test Server - Wildcard",
                "server_type": "local",
                "allowed_databases": "*",
            }
        )
        cls.server_this_db = cls.Server.create(
            {
                "name": "Test Server - This DB",
                "server_type": "local",
                "allowed_databases": cls.env.cr.dbname,
            }
        )
        cls.server_other_db = cls.Server.create(
            {
                "name": "Test Server - Other DB",
                "server_type": "local",
                "allowed_databases": "some_other_database",
            }
        )
        cls.server_multi_db = cls.Server.create(
            {
                "name": "Test Server - Multi DB",
                "server_type": "local",
                "allowed_databases": "other1," + cls.env.cr.dbname + ",other2",
            }
        )
        cls.server_no_filter = cls.Server.create(
            {
                "name": "Test Server - No Filter",
                "server_type": "local",
                "allowed_databases": False,
            }
        )

    def _reload(self, server):
        """Invalidate server recordset cache and return the server."""
        server.invalidate_recordset()
        return server

    def test_01_allowed_databases_field_default(self):
        """New fetchmail servers default to allowed_databases='*'."""
        new_server = self.Server.create(
            {
                "name": "Default Server",
                "server_type": "local",
            }
        )
        self.assertEqual(new_server.allowed_databases, "*")

    def test_02_wildcard_allows_any_database(self):
        """Servers with allowed_databases='*' are passed to the base fetch."""
        self.assertFalse(self._reload(self.server_wildcard).date)
        self.server_wildcard.fetch_mail(raise_exception=False)
        self.assertTrue(self._reload(self.server_wildcard).date)

    def test_03_specific_db_allows_current_database(self):
        """Servers with allowed_databases matching the current DB are allowed."""
        self.assertFalse(self._reload(self.server_this_db).date)
        self.server_this_db.fetch_mail(raise_exception=False)
        self.assertTrue(self._reload(self.server_this_db).date)

    def test_04_other_db_blocks_current_database(self):
        """Servers with allowed_databases not matching the current DB are skipped."""
        self.assertFalse(self._reload(self.server_other_db).date)
        self.server_other_db.fetch_mail(raise_exception=False)
        self.assertFalse(self._reload(self.server_other_db).date)

    def test_05_no_filter_blocks_without_global_config(self):
        """Servers with no allowed_databases are skipped when config list is empty."""
        self.assertFalse(self._reload(self.server_no_filter).date)
        self.server_no_filter.fetch_mail(raise_exception=False)
        self.assertFalse(self._reload(self.server_no_filter).date)

    def test_06_comma_separated_includes_current_database(self):
        """Servers with comma-separated list including current DB are allowed."""
        self.assertFalse(self._reload(self.server_multi_db).date)
        self.server_multi_db.fetch_mail(raise_exception=False)
        self.assertTrue(self._reload(self.server_multi_db).date)

    def test_07_multiple_servers_filtering(self):
        """Only servers with matching allowed_databases are passed to base fetch."""
        all_servers = (
            self.server_wildcard
            | self.server_this_db
            | self.server_other_db
            | self.server_no_filter
        )
        all_servers.fetch_mail(raise_exception=False)
        self.assertTrue(self._reload(self.server_wildcard).date)
        self.assertTrue(self._reload(self.server_this_db).date)
        self.assertFalse(self._reload(self.server_other_db).date)
        self.assertFalse(self._reload(self.server_no_filter).date)
