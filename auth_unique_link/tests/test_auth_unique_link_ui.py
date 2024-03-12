# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2023


from lxml import html
from werkzeug.test import Client
from werkzeug.wrappers import BaseResponse


from odoo.service import wsgi_server
from odoo.tests import common, tagged
from .common import TestAuthUniqueLinkCommon


@tagged("post_install", "-at_install")
class TestAuthUniqueLinkUI(common.HttpCase, TestAuthUniqueLinkCommon):
    """ """

    def get_request(self, url, data=None):
        return self.test_client.get(url, query_string=data, follow_redirects=True)

    def post_request(self, url, data=None):
        return self.test_client.post(
            url, data=data, follow_redirects=True, environ_base=self.werkzeug_environ
        )

    def html_doc(self, response):
        """Get an HTML LXML document."""
        return html.fromstring(response.data)

    def csrf_token(self, response):
        """Get a valid CSRF token."""
        doc = self.html_doc(response)
        return doc.xpath("//input[@name='csrf_token']")[0].get("value")

    def setUp(self):
        super().setUp()

        with self.registry.cursor() as test_cursor:
            env = self.env(test_cursor)
            # brandon.freeman55@example.com
            partner_xml_id = "base.res_partner_address_15"
            partner_id = self.env.ref(partner_xml_id)
            self._get_user_with_portal_access(partner_xml_id)
            self.user_email_with_portal_access = partner_id.email
            # colleen.diaz83@example.com
            partner_xml_id = "base.res_partner_address_28"
            partner_id = self.env.ref(partner_xml_id)
            self.user_email_without_portal_access = partner_id.email
            # database
            self.dbname = env.cr.dbname

        self.werkzeug_environ = {"REMOTE_ADDR": "127.0.0.1"}
        self.test_client = Client(wsgi_server.application, BaseResponse)
        self.test_client.get("/web/session/logout")

    def _test_login_link(self, email):
        response = self.get_request("/web/login")
        content = response.data.decode("utf-8")
        self.assertIn("Email Me a Link", content)

        data = {
            "email": email,
            "csrf_token": self.csrf_token(response),
            "db": self.dbname,
        }
        response = self.post_request("/web/login_link/", data=data)
        doc = self.html_doc(response)
        return doc


    def test_01_login_link_success(self):
        doc = self._test_login_link(self.user_email_with_portal_access)
        self.assertIn(
            "We've sent you an email with login instructions. Please check your inbox!",
            doc.xpath("//p[@name='link-success']")[0].text,
        )

    def test_02_login_link_error(self):
        doc = self._test_login_link(self.user_email_without_portal_access)
        self.assertIn(
            "Unknown email address",
            doc.xpath("//p[@name='link-error']")[0].text,
        )
