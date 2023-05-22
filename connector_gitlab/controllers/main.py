# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Dec 2021

import logging

import odoo.http as http
from odoo.http import request

_logger = logging.getLogger(__name__)

URL_BASE = "/api/connector_gitlab/v1"


class GitlabController(http.Controller):
    """Http Public Controller for Gitlab"""

    #######################################################################

    @http.route(
        URL_BASE + "/SignIn",
        type="json",
        methods=["POST"],
        auth="api_key",
        csrf=False,
    )
    def gitlab_sign_in(self, login, password, **kwargs):
        return request.env["gitlab.service"].sudo()._get_session(login, password)
