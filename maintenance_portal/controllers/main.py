# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jul 2024

from odoo import http
from odoo.exceptions import UserError
from odoo.http import request
from odoo.tools.translate import _

SUCCESS = 0
ERROR = 1

URL_BASE_V1 = "/api/maintenance/v1"
URL_VAR_SERIAL = "/serial/<string:equipement_serial>"
URL_VAR_IDENTIFIER = "/id/<string:unique_identifier>"

GENERIC_ERROR = {
    "result": ERROR,
    "message_id": "GENERIC_ERROR",
    "message": "",
}

REQUEST_NOT_FOUND = {
    "result": ERROR,
    "message_id": "REQUEST_NOT_FOUND",
    "message": "no existing active request found.",
}

REQUEST_CREATED = {
    "result": SUCCESS,
    "message_id": "REQUEST_CREATED",
    "message": "a new request has been created.",
}

REQUEST_UPDATED = {
    "result": SUCCESS,
    "message_id": "REQUEST_UPDATED",
    "message": "an existing request has been updated.",
}

REQUEST_CLOSED = {
    "result": SUCCESS,
    "message_id": "REQUEST_CLOSED",
    "message": "an existing request has been closed.",
}


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
            msg = REQUEST_UPDATED.copy()
            msg["request_id"] = request_id.id
        else:
            try:
                request_id = (
                    request.env["maintenance.request"]
                    .sudo()
                    ._remote_create(
                        equipement_serial, unique_identifier, request.params, ip_addr
                    )
                )
                msg = REQUEST_CREATED.copy()
                msg["request_id"] = request_id.id
            except UserError as e:
                msg = GENERIC_ERROR.copy()
                msg["message"] = str(e)
                msg["request_id"] = False
        return msg


    @http.route(
        URL_BASE_V1 + URL_VAR_SERIAL + URL_VAR_IDENTIFIER + "/CloseRequest",
        type="json",
        methods=["POST"],
        auth="api_key",
        csrf=False,
    )
    def close_maintenance_request(
        self, equipement_serial, unique_identifier, **kwargs
    ):
        ip_addr = self._get_ip_from_request(request)
        request_id = self._get_maintenance_request_id(
            equipement_serial, unique_identifier
        )
        if request_id:
            request_id._remote_close(request.params, ip_addr)
            msg = REQUEST_CLOSED.copy()
            msg["request_id"] = request_id.id
        else:
            msg = REQUEST_NOT_FOUND.copy()
        return msg

    def _get_ip_from_request(self, req):
        ip_addr = req.httprequest.environ.get("HTTP_X_FORWARDED_FOR")
        if ip_addr:
            ip_addr = ip_addr.split(",")[0]
        else:
            ip_addr = req.httprequest.remote_addr
        return ip_addr
