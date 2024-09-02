# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jul 2024

from odoo import http
from odoo.exceptions import UserError
from odoo.http import request
from odoo.tools.translate import _

SUCCESS = 0
ERROR = 1

URL_BASE_V1 = "/api/reminder/v1"
URL_VAR_ACTIVITY = "/activity/<int:activity_id>"
URL_VAR_SNOOZE = "/snooze/<int:value>/<string:unit>"


# GENERIC_ERROR = {
#     "result": ERROR,
#     "message_id": "GENERIC_ERROR",
#     "message": "",
# }

# REQUEST_NOT_FOUND = {
#     "result": ERROR,
#     "message_id": "REQUEST_NOT_FOUND",
#     "message": "no existing active request found.",
# }

# REQUEST_CREATED = {
#     "result": SUCCESS,
#     "message_id": "REQUEST_CREATED",
#     "message": "a new request has been created.",
# }

# REQUEST_UPDATED = {
#     "result": SUCCESS,
#     "message_id": "REQUEST_UPDATED",
#     "message": "an existing request has been updated.",
# }

# REQUEST_CLOSED = {
#     "result": SUCCESS,
#     "message_id": "REQUEST_CLOSED",
#     "message": "an existing request has been closed.",
# }


class MailActivityReminderController(http.Controller):
    """Http Controller for Mail Activity Reminder"""

    #######################################################################

    def _get_user_id(self, token):
        domain = [
            ("activity_reminder_access_token", "=", token),
        ]
        user_id = request.env["res.users"].sudo().search(domain, limit=1)
        return user_id

    def _get_activity_id(self, activity_id):
        return request.env["mail.activity"].browse(activity_id)

    @http.route(
        URL_BASE_V1 + URL_VAR_ACTIVITY + "/close",
        type="http",
        methods=["GET"],
        auth="public",
        csrf=False,
    )
    def activity_close(self, activity_id, token=None, **kwargs):
        user_id = self._get_user_id(token)
        if user_id:
            activity_id = self._get_activity_id(activity_id)
            if activity_id.exists():
                activity_id.with_user(user_id).action_done()
                return "Activity closed"
            else:
                return "Activity not found"
        else:
            return "Invalid token"

    @http.route(
        URL_BASE_V1 + URL_VAR_ACTIVITY + "/cancel",
        type="http",
        methods=["GET"],
        auth="public",
        csrf=False,
    )
    def activity_cancel(self, activity_id, token=None, **kwargs):
        user_id = self._get_user_id(token)
        if user_id:
            activity_id = self._get_activity_id(activity_id)
            if activity_id.exists():
                activity_id.unlink()
                return "Activity cancelled"
            else:
                return "Activity not found"
        else:
            return "Invalid token"

    @http.route(
        URL_BASE_V1 + URL_VAR_ACTIVITY + URL_VAR_SNOOZE,
        type="http",
        methods=["GET"],
        auth="public",
        csrf=False,
    )
    def activity_snooze(self, activity_id, value, unit, token=None, **kwargs):
        user_id = self._get_user_id(token)
        if user_id:
            activity_id = self._get_activity_id(activity_id)
            if activity_id.exists():
                activity_id.action_snooze(unit, value)
                return f"Activity's new deadline is {activity_id.date_deadline}"
            else:
                return "Activity not found"
        else:
            return "Invalid token"

    def _get_ip_from_request(self, req):
        ip_addr = req.httprequest.environ.get("HTTP_X_FORWARDED_FOR")
        if ip_addr:
            ip_addr = ip_addr.split(",")[0]
        else:
            ip_addr = req.httprequest.remote_addr
        return ip_addr
