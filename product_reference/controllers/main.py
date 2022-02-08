# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Feb 2022

import json

from odoo import http
from odoo.http import request

URL_BASE_V1 = "/api/ref/v1"

URL_USERS = URL_BASE_V1 + "/Users"


class ProductReferenceController(http.Controller):
    """ Http Controller for Product Reference Application
    """

    #######################################################################

    @http.route(
        URL_USERS, type='json', methods=['POST'], auth="api_key", csrf=False
    )
    def get_ref_users(self, **kwargs):
        res = {}
        group_id = request.env.ref(
            "product_reference_management.group_ref_user"
        )
        for user_id in group_id.users:
            res[user_id.id] = {
                'name': user_id.name,
                'login': user_id.login,
                'email': user_id.email,
            }
        return res
