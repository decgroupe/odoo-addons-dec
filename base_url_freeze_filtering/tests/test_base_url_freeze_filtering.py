# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jan 2025

from unittest.mock import patch

from odoo.tests.common import TransactionCase
from odoo.tools.config import config as odoo_config
from odoo.tools.misc import str2bool


class TestBaseUrlFreezeFiltering(TransactionCase):
    def setUp(self):
        super().setUp()

    def test_01_url_freeze(self):
        ICP = self.env["ir.config_parameter"].sudo()
        # disable url freeze for this database
        ICP.set_param("web.base.url.freeze", False)
        # allow this database to be frozen
        with patch.dict(
            odoo_config.options, {"db_url_freeze_allowedlist": [self.env.cr.dbname]}
        ):
            ICP.clear_caches()
            web_base_url_freeze = str2bool(ICP.get_param("web.base.url.freeze"))
            self.assertFalse(web_base_url_freeze)
        # disallow this database to be frozen
        with patch.dict(odoo_config.options, {"db_url_freeze_allowedlist": []}):
            ICP.clear_caches()
            web_base_url_freeze = str2bool(ICP.get_param("web.base.url.freeze"))
            self.assertFalse(web_base_url_freeze)
        # enable url freeze for this database
        ICP.set_param("web.base.url.freeze", True)
        # allow this database to be frozen
        with patch.dict(
            odoo_config.options, {"db_url_freeze_allowedlist": [self.env.cr.dbname]}
        ):
            ICP.clear_caches()
            web_base_url_freeze = str2bool(ICP.get_param("web.base.url.freeze"))
            self.assertTrue(web_base_url_freeze)
        # disallow this database to be frozen
        with patch.dict(odoo_config.options, {"db_url_freeze_allowedlist": []}):
            ICP.clear_caches()
            web_base_url_freeze = str2bool(ICP.get_param("web.base.url.freeze"))
            self.assertFalse(web_base_url_freeze)
