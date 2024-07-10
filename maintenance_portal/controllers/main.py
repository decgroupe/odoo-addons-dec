# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jul 2024

import pprint
import json

from odoo import fields, http
from odoo.http import request
from odoo.tools.translate import _


URL_BASE_V1 = "/api/maintenance/v1"
URL_VAR_SERIAL = "/serial/<string:equipement_serial>"
URL_VAR_IDENTIFIER = "/id/<string:unique_identifier>"


class MaintenanceController(http.Controller):
    """Http Controller for Maintenance System"""

    #######################################################################

    def _get_maintenance_request_id(self, equipement_serial, unique_identifier):
        domain = [
            ("equipment_id.serial_no", "=", equipement_serial),
            ("unique_identifier", "=", unique_identifier),
            ("stage_id.done", "=", False),
        ]
        request_id = request.env["maintenance.request"].sudo().search(domain, limit=1)
        return request_id

    @http.route(
        URL_BASE_V1 + URL_VAR_SERIAL + URL_VAR_IDENTIFIER + "/Request",
        type="json",
        methods=["POST"],
        auth="api_key",
        csrf=False,
    )
    def create_or_update_maintenance_request(
        self, equipement_serial, unique_identifier, **kwargs
    ):
        ip_addr = self._get_ip_from_request(request)
        request_id = self._get_maintenance_request_id(
            equipement_serial, unique_identifier
        )
        if request_id:
            request_id._remote_update(request.params, ip_addr)
        else:
            request_id = (
                request.env["maintenance.request"]
                .sudo()
                ._remote_create(
                    equipement_serial, unique_identifier, request.params, ip_addr
                )
            )
        return {"request_id": request_id.id}

    def _get_ip_from_request(self, req):
        ip_addr = req.httprequest.environ.get("HTTP_X_FORWARDED_FOR")
        if ip_addr:
            ip_addr = ip_addr.split(",")[0]
        else:
            ip_addr = req.httprequest.remote_addr
        return ip_addr
