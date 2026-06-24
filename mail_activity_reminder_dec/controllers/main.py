# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jul 2024

from odoo import http
from odoo.http import Controller as HttpController
from odoo.http import request
from odoo.tools.misc import format_date

# from odoo.addons.base_controller_user.controllers.main import HttpController

SUCCESS = 0
ERROR = 1

URL_BASE_V1 = "/api/reminder/v1"
URL_VAR_ACTIVITY = "/activity/<int:activity_id>"
URL_VAR_SNOOZE = "/snooze/<int:value>/<string:unit>"


class MailActivityReminderController(HttpController):
    """Http Controller for Mail Activity Reminder"""

    #######################################################################

    def _get_user_id(self, token):
        """Look up a user by their activity reminder access token."""
        domain = [
            ("activity_reminder_access_token", "=", token),
        ]
        user_id = request.env["res.users"].sudo().search(domain, limit=1)
        # fix translation issues using "base_controller_user" module
        if user_id and hasattr(self, "_update_user_with_context"):
            user_id = self._update_user_with_context(
                user_id, override_request_user=True
            )
        return user_id

    def _get_activity_id(self, activity_id):
        """Browse a mail.activity record by id."""
        return request.env["mail.activity"].browse(activity_id)

    def _render_activity_reminder_message(
        self, message=False, subject=False, warning=False, user=False
    ):
        """Render the activity reminder notification email template."""
        return request.env["ir.qweb"]._render(
            "mail_qweb.view_email_template_notification",
            {
                "env": request.env,
                "do_not_reply": True,
                "notified_user": user,
                "content_subject": subject,
                "content_message": message,
                "content_warning": warning,
            },
        )

    def _render_activity_reminder_message_activity_update(
        self, message=False, user=False, activity=False
    ):
        """Render the activity update reminder message with the activity subject."""
        return self._render_activity_reminder_message(
            message=message,
            user=user,
            subject=f"{activity.res_model_id_name}: {activity.res_name}",
        )

    def _render_activity_reminder_not_found_message(self, user=False):
        """Render the activity not found reminder message."""
        return self._render_activity_reminder_message(
            user=user,
            message=request.env._(
                "This activity has probably been closed by you or someone in your "
                "team since this reminder was sent."
            ),
            warning=request.env._("Activity not found"),
        )

    def _render_activity_reminder_invalid_token_message(self):
        """Render the invalid token reminder message."""
        return self._render_activity_reminder_message(
            message=request.env._(
                "You have probably received a new reminder since this one."
            ),
            warning=request.env._("Invalid token"),
        )

    @http.route(
        URL_BASE_V1 + URL_VAR_ACTIVITY + "/close",
        type="http",
        methods=["GET"],
        auth="public",
        csrf=False,
    )
    def activity_close(self, activity_id, token=None, **kwargs):
        """Handle close action from an activity reminder email link."""
        user_id = self._get_user_id(token)
        if user_id:
            activity_id = self._get_activity_id(activity_id)
            if activity_id.exists():
                message = request.env._("Activity closed")
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
        """Handle cancel action from an activity reminder email link."""
        user_id = self._get_user_id(token)
        if user_id:
            activity_id = self._get_activity_id(activity_id)
            if activity_id.exists():
                message = request.env._("Activity cancelled")
                render = self._render_activity_reminder_message_activity_update(
                    message,
                    user=user_id,
                    activity=activity_id,
                )
                activity_id.with_user(user_id).unlink()
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
    def activity_snooze(
        self, activity_id, value, unit, token=None, date=None, **kwargs
    ):
        """Handle snooze action from an activity reminder email link."""
        user_id = self._get_user_id(token)
        if user_id:
            activity_id = self._get_activity_id(activity_id).with_user(user_id)
            if activity_id.exists():
                previous_deadline = activity_id.date_deadline
                activity_id.action_snooze_custom(unit, value)
                message = request.env._(
                    "New deadline is %(new)s (was %(old)s)",
                    new=format_date(user_id.env, activity_id.date_deadline),
                    old=format_date(user_id.env, previous_deadline),
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
        """Extract the client IP address from the request, handling proxies."""
        ip_addr = req.httprequest.environ.get("HTTP_X_FORWARDED_FOR")
        if ip_addr:
            ip_addr = ip_addr.split(",")[0]
        else:
            ip_addr = req.httprequest.remote_addr
        return ip_addr
