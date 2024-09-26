# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jul 2024

import logging

from odoo import http
from odoo.exceptions import UserError
from odoo.http import request
from odoo.tools.translate import _

from ..models.mrp_production import _checksum

SUCCESS = 0
ERROR = 1

URL_BASE_V1 = "/api/mrp/v1"
URL_VAR_IDENTIFIER = "/identifier/<string:identifier>"

GENERIC_ERROR = {
    "result": ERROR,
    "message_id": "GENERIC_ERROR",
    "message": "",
}

MRP_IDENTIFIER_CHECKSUM_INVALID = {
    "result": ERROR,
    "message_id": "MRP_IDENTIFIER_CHECKSUM_INVALID",
    "message": "invalid checksum.",
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

_logger = logging.getLogger(__name__)


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

    def _get_production_id(self, identifier, checksum=False, name=False):
        domain = [("identifier", "=", identifier)]
        if checksum:
            domain += [("identifier_checksum", "=", checksum)]
        if name:
            domain += [("name", "=", name)]
        production_id = request.env["mrp.production"].sudo().search(domain, limit=1)
        if not production_id:
            domain = [("name", "=", identifier)]
            production_id = request.env["mrp.production"].sudo().search(domain, limit=1)
            if production_id:
                _logger.warning(
                    "Use identifier `%s` instead of name `%s`",
                    production_id.identifier,
                    identifier,
                )
        return production_id

    def _get_production_not_ready_states(self):
        return ["draft", "done", "cancel"]

    def _validate_production_identifier_checksum(self, identifier, checksum):
        return _checksum(identifier) == checksum

    def _run_production_remote_action(self, identifier, action, **kwargs):
        ip_addr = self._get_ip_from_request(request)
        checksum = kwargs.get("checksum", False)
        name = kwargs.get("name", False)

        # ensure given checksum is valid
        if checksum:
            computed_checksum = _checksum(identifier)
            if computed_checksum != checksum:
                msg = MRP_IDENTIFIER_CHECKSUM_INVALID.copy()
                msg.update(
                    {
                        "computed_checksum": computed_checksum,
                    }
                )
                return msg

        production_id = self._get_production_id(identifier, checksum, name)
        if production_id:
            if production_id.state in self._get_production_not_ready_states():
                msg = MRP_ORDER_NOT_READY.copy()
            else:
                if action == "update_quantity":
                    quantity = request.params.get("value")
                    production_id._remote_update_producing_quantity(quantity, ip_addr)
                    msg = MRP_ORDER_QUANTITY_UPDATED.copy()
                elif action == "notify_done":
                    production_id._remote_notify_done(ip_addr)
                    msg = MRP_NOTIFICATION_CREATED.copy()
                elif action == "notify_cancel":
                    production_id._remote_notify_cancel(ip_addr)
                    msg = MRP_NOTIFICATION_CREATED.copy()
                else:
                    raise ValueError(f"Action `{action}` not supported")
            msg.update(
                {
                    "state": production_id.state,
                    "production_id": production_id.id,
                }
            )
        else:
            msg = MRP_ORDER_NOT_FOUND.copy()
            if name:
                msg.update({"name": name})

        return msg

    @http.route(
        URL_BASE_V1 + URL_VAR_IDENTIFIER + "/UpdateQuantity",
        type="json",
        methods=["POST"],
        auth="api_key",
        csrf=False,
    )
    def update_production_quantity(self, identifier, **kwargs):
        return self._run_production_remote_action(
            identifier,
            "update_quantity",
            **kwargs,
        )

    @http.route(
        URL_BASE_V1 + URL_VAR_IDENTIFIER + "/NotifyDone",
        type="json",
        methods=["POST"],
        auth="api_key",
        csrf=False,
    )
    def notify_done_production_order(self, identifier, **kwargs):
        return self._run_production_remote_action(
            identifier,
            "notify_done",
            **kwargs,
        )

    @http.route(
        URL_BASE_V1 + URL_VAR_IDENTIFIER + "/NotifyCancel",
        type="json",
        methods=["POST"],
        auth="api_key",
        csrf=False,
    )
    def notify_cancel_production_order(self, identifier, **kwargs):
        return self._run_production_remote_action(
            identifier,
            "notify_cancel",
            **kwargs,
        )
