# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2023

from odoo import http
from odoo.tests.common import HttpCase


class TestWebPublicImagesBase(HttpCase):
    """Base class for web_public_images tests"""

    def setUp(self):
        super().setUp()

    def _get_crsf_token(self):
        # Get csrf_token
        self.authenticate(None, None)
        csrf_token = http.Request.csrf_token(self)
        return csrf_token
