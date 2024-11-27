# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jul 2024

from odoo import http
from odoo.exceptions import UserError
from odoo.http import request
from odoo.tools.translate import _
from odoo.tools.misc import format_date

SUCCESS = 0
ERROR = 1

URL_BASE_V1 = "/api/reminder/v1"
URL_VAR_ACTIVITY = "/activity/<int:activity_id>"
URL_VAR_SNOOZE = "/snooze/<int:value>/<string:unit>"


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

    def _render_activity_reminder_message(
        self, message=False, subject=False, warning=False, user=False
    ):
        return request.env.ref("mail_qweb.view_email_template_notification")._render(
            {
                "env": request.env,
                "do_not_reply": True,
                "notified_user": user,
                "content_subject": subject,
                "content_message": message,
                "content_warning": warning,
            }
        )

    def _render_activity_reminder_message_activity_update(
        self, message=False, user=False, activity=False
    ):
        return self._render_activity_reminder_message(
            message=message,
            user=user,
            subject="%s: %s" % (activity.res_model_id_name, activity.res_name),
        )

    def _render_activity_reminder_not_found_message(self, user=False):
        return self._render_activity_reminder_message(
            user=user,
            message=_(
                "This activity has probably been closed by you or someone in your "
                "team since this reminder was sent."
            ),
            warning=_("Activity not found"),
        )

    def _render_activity_reminder_invalid_token_message(self):
        return self._render_activity_reminder_message(
            message=_("You have probably received a new reminder since this one."),
            warning=_("Invalid token"),
        )

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
                message = _("Activity closed")
                render = self._render_activity_reminder_message_activity_update(
                    message,
                    user=user_id,
                    activity=activity_id,
                )
                activity_id.with_user(user_id).action_done()
                return render
            else:
                return self._render_activity_reminder_not_found_message(user=user_id)
        else:
            return self._render_activity_reminder_invalid_token_message()

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
                message = _("Activity cancelled")
                render = self._render_activity_reminder_message_activity_update(
                    message,
                    user=user_id,
                    activity=activity_id,
                )
                activity_id.unlink()
                return render
            else:
                return self._render_activity_reminder_not_found_message(user=user_id)
        else:
            return self._render_activity_reminder_invalid_token_message()

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
                message = _("Activity's new deadline is %s") % format_date(
                    user_id.env, activity_id.date_deadline
                )
                return self._render_activity_reminder_message_activity_update(
                    message,
                    user=user_id,
                    activity=activity_id,
                )
            else:
                return self._render_activity_reminder_not_found_message(user=user_id)
        else:
            return self._render_activity_reminder_invalid_token_message()

    def _get_ip_from_request(self, req):
        ip_addr = req.httprequest.environ.get("HTTP_X_FORWARDED_FOR")
        if ip_addr:
            ip_addr = ip_addr.split(",")[0]
        else:
            ip_addr = req.httprequest.remote_addr
        return ip_addr
