# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jul 2024

from odoo import http
from odoo.exceptions import UserError
from odoo.http import request
from odoo.tools.translate import _

SUCCESS = 0
ERROR = 1

URL_BASE_V1 = "/api/mrp/v1"
URL_VAR_CODE = "/code/<string:code>"

GENERIC_ERROR = {
    "result": ERROR,
    "message_id": "GENERIC_ERROR",
    "message": "",
}

MRP_ORDER_NOT_FOUND = {
    "result": ERROR,
    "message_id": "MRP_ORDER_NOT_FOUND",
    "message": "no existing production order found.",
}

MRP_ORDER_NOT_READY = {
    "result": ERROR,
    "message_id": "MRP_ORDER_NOT_READY",
    "message": "production order not ready.",
}

MRP_ORDER_QUANTITY_UPDATED = {
    "result": SUCCESS,
    "message_id": "MRP_ORDER_QUANTITY_UPDATED",
    "message": "quantity has been updated.",
}

MRP_NOTIFICATION_CREATED = {
    "result": SUCCESS,
    "message_id": "MRP_NOTIFICATION_CREATED",
    "message": "a notification has been created.",
}


class MrpController(http.Controller):
    """Http Controller for MRP"""

    #######################################################################

    def _get_ip_from_request(self, req):
        ip_addr = req.httprequest.environ.get("HTTP_X_FORWARDED_FOR")
        if ip_addr:
            ip_addr = ip_addr.split(",")[0]
        else:
            ip_addr = req.httprequest.remote_addr
        return ip_addr

    def _get_production_id(self, code):
        domain = [
            ("name", "=", code),
        ]
        production_id = request.env["mrp.production"].sudo().search(domain, limit=1)
        return production_id

    def _get_production_not_ready_states(self):
        return ["draft", "done", "cancel"]

    @http.route(
        URL_BASE_V1 + URL_VAR_CODE + "/UpdateQuantity",
        type="json",
        methods=["POST"],
        auth="api_key",
        csrf=False,
    )
    def update_production_quantity(self, code, **kwargs):
        ip_addr = self._get_ip_from_request(request)
        try:
            production_id = self._get_production_id(code)
            if production_id:
                if production_id.state in self._get_production_not_ready_states():
                    msg = MRP_ORDER_NOT_READY.copy()
                else:
                    quantity = request.params.get("value")
                    production_id._remote_update_producing_quantity(quantity, ip_addr)
                    msg = MRP_ORDER_QUANTITY_UPDATED.copy()
                msg.update(
                    {
                        "state": production_id.state,
                        "production_id": production_id.id,
                    }
                )
            else:
                msg = MRP_ORDER_NOT_FOUND.copy()
        except UserError as e:
            msg = GENERIC_ERROR.copy()
            msg["message"] = str(e)
        return msg

    @http.route(
        URL_BASE_V1 + URL_VAR_CODE + "/NotifyDone",
        type="json",
        methods=["POST"],
        auth="api_key",
        csrf=False,
    )
    def notify_done_production_order(self, code, **kwargs):
        ip_addr = self._get_ip_from_request(request)
        production_id = self._get_production_id(code)
        if production_id:
            if production_id.state in self._get_production_not_ready_states():
                msg = MRP_ORDER_NOT_READY.copy()
            else:
                production_id._remote_notify_done(ip_addr)
                msg = MRP_NOTIFICATION_CREATED.copy()
            msg.update(
                {
                    "state": production_id.state,
                    "production_id": production_id.id,
                }
            )
        else:
            msg = MRP_ORDER_NOT_FOUND.copy()
        return msg

    @http.route(
        URL_BASE_V1 + URL_VAR_CODE + "/NotifyCancel",
        type="json",
        methods=["POST"],
        auth="api_key",
        csrf=False,
    )
    def notify_cancel_production_order(self, code, **kwargs):
        ip_addr = self._get_ip_from_request(request)
        production_id = self._get_production_id(code)
        if production_id:
            if production_id.state in self._get_production_not_ready_states():
                msg = MRP_ORDER_NOT_READY.copy()
            else:
                production_id._remote_notify_cancel(ip_addr)
                msg = MRP_NOTIFICATION_CREATED.copy()
            msg.update(
                {
                    "state": production_id.state,
                    "production_id": production_id.id,
                }
            )
        else:
            msg = MRP_ORDER_NOT_FOUND.copy()
        return msg
