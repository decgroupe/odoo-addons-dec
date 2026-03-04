# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Dec 2024


from odoo import http
from odoo.http import request
from odoo.tools.misc import str2bool

from odoo.addons.web.controllers.session import Session


class PermanentSession(Session):
    @http.route()
    def authenticate(self, db, login, password, base_location=None):
        """Inherits `/web/session/authenticate` to set permanent attribute to
        werkzeug session"""
        request.session.permanent = str2bool(
            request.httprequest.headers.get("X-Odoo-Session-Permanent", "False")
        )
        return super().authenticate(db, login, password, base_location)
