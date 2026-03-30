# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2026

from unittest.mock import patch

from odoo.tests.common import TransactionCase
from odoo.tools.config import config


class TestWebEnvironmentRibbonFiltering(TransactionCase):
    """Tests for web_environment_ribbon_filtering module."""

    @classmethod
    def setUpClass(cls):
        """Set up shared test data."""
        super().setUpClass()
        cls.backend = cls.env["web.environment.ribbon.backend"]
        cls.env["ir.config_parameter"].sudo().set_param("ribbon.name", "TEST {db_name}")

    def _set_ignorelist(self, databases):
        """Patch the cached ignorelist with the given list of database names."""
        return patch.object(
            type(self.backend),
            "_get_db_ribbon_ignorelist",
            return_value=databases,
        )

    def test_01_ribbon_shown_when_db_not_in_ignorelist(self):
        """Ribbon name is returned normally when the current db is not ignored."""
        with self._set_ignorelist(["other_db"]):
            result = self.backend.get_environment_ribbon()
        self.assertNotEqual(result.get("name"), "")

    def test_02_ribbon_hidden_when_db_in_ignorelist(self):
        """Ribbon name is cleared when the current db is in the ignorelist."""
        dbname = self.env.cr.dbname
        with self._set_ignorelist([dbname]):
            result = self.backend.get_environment_ribbon()
        self.assertEqual(result.get("name"), "")

    def test_03_ignorelist_empty_by_default(self):
        """_get_db_ribbon_ignorelist returns an empty list when config key is absent."""
        original = config.get("db_ribbon_ignorelist")
        try:
            config["db_ribbon_ignorelist"] = None
            # clear ormcache so the real method runs
            self.env.registry.clear_cache()
            result = self.backend._get_db_ribbon_ignorelist()
            self.assertEqual(result, [])
        finally:
            config["db_ribbon_ignorelist"] = original
            self.env.registry.clear_cache()

    def test_04_ignorelist_parsed_from_config(self):
        """_get_db_ribbon_ignorelist parses a comma-separated config value correctly."""
        original = config.get("db_ribbon_ignorelist")
        try:
            config["db_ribbon_ignorelist"] = "db1,db2,db3"
            self.env.registry.clear_cache()
            result = self.backend._get_db_ribbon_ignorelist()
            self.assertIn("db1", result)
            self.assertIn("db2", result)
            self.assertIn("db3", result)
        finally:
            config["db_ribbon_ignorelist"] = original
            self.env.registry.clear_cache()
