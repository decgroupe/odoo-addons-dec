# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Dec 2021

import logging

import werkzeug

import odoo
from odoo import _, http
from odoo.addons.web.controllers.main import Home, ensure_db
from odoo.http import request

_logger = logging.getLogger(__name__)

URL_BASE = "/api/auth_unique_link/v1"


class AuthUniqueLink(Home):
    # #########################################################################

    @http.route()
    def web_login(self, *args, **kw):
        login_success = request.params.get("login_success", False)
        response = super(AuthUniqueLink, self).web_login(*args, **kw)
        request.params["login_success"] = login_success
        return response

    @http.route(
        "/web/login_link", type="http", auth="public", website=True, methods=["GET"]
    )
    def web_login_link_authenticate(self, **kw):
        """Try to mimic `super(AuthUniqueLink, self).web_login()` that is not
        properly callable from this context as most of its internal
        logic checks for `POST` to execute authenticate method.
        """
        ensure_db()
        login = request.params["login"]
        token = request.params["token"]
        redirect = request.params.get("redirect")

        old_uid = request.uid
        try:
            uid = request.session.authenticate(request.session.db, login, token)
            request.params["login_success"] = True
            self.web_login()
            request.env.user.signin_link_cancel()
            return http.redirect_with_hash(self._login_redirect(uid, redirect=redirect))
        except odoo.exceptions.AccessDenied as e:
            request.uid = old_uid
            if e.args == odoo.exceptions.AccessDenied().args:
                request.params["link_error"] = _(
                    "Invalid/expired token or invalid login"
                )
            else:
                request.params["link_error"] = e.args[0]

        return self.web_login()

    def _send_signin_link(self, email):
        domain = [("email", "=", email)]
        user_id = request.env["res.users"].sudo().search(domain, limit=1)
        if user_id:
            basic = request.params.get("basic", False)
            user_id._send_signin_link_email(basic=basic)
            # Create a context dictionary on a function level that will be
            # used by the translate function
            context = {"lang": user_id.lang}
            return {
                "link_success": _(
                    "We've sent you an email with login instructions. "
                    "Please check your inbox!"
                ),
            }
        else:
            return {
                "link_error": _("Unknown email address."),
                "show_create_account": True,
            }

    @http.route("/web/login_link", type="http", auth="public", methods=["POST"])
    def web_login_link_request(self, **kw):
        query = {
            "redirect": request.params.get("redirect"),
        }
        res = self._send_signin_link(request.params["email"])
        query.update(res)
        return http.local_redirect(
            path="/web/login",
            query=query,
            keep_hash=True,
        )

    @http.route(
        URL_BASE + "/SendLink",
        type="json",
        methods=["POST"],
        auth="api_key",
        csrf=False,
    )
    def api_auth_unique_link_send_link(self, email, **kwargs):
        res = self._send_signin_link(email)
        if "link_success" in res:
            return res["link_success"]
        elif "link_error" in res:
            return res["link_error"]
        else:
            return False
