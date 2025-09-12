# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2021

from odoo import http
from odoo.http import request
from odoo.tools.translate import _

URL_V1_BASE = "/api/launcher/v1"
URL_V1_MANIFEST = URL_V1_BASE + "/Manifest"
URL_V1_MANIFEST_IMAGES = URL_V1_MANIFEST + "/Images"
URL_V1_MANIFEST_IDENTIFIER = URL_V1_MANIFEST + "/identifier/<int:identifier>"


class SoftwareApplicationLauncherController(http.Controller):
    """Http Controller for Software Application Launcher"""

    #######################################################################

    def _sal_api_v1_get_manifest(self, with_tooltips=False, extra_domain=False):
        res = {
            "version": 2,
            "applications": [],
            "resources": [],
        }
        SoftwareApplication = request.env["software.application"]
        domain = SoftwareApplication._get_launcher_manifest_domain()
        if extra_domain:
            domain += extra_domain
        asset_ids = SoftwareApplication.search(domain)
        for asset_id in asset_ids:
            entry = asset_id._get_launcher_manifest_entry(with_tooltips=with_tooltips)
            if asset_id.type == "inhouse":
                res["applications"].append(entry)
            elif asset_id.type == "resource":
                res["resources"].append(entry)
        return res

    @http.route(
        URL_V1_MANIFEST,
        type="json",
        methods=["POST"],
        auth="api_key",
        csrf=False,
    )
    def sal_api_v1_get_manifest(self, **kwargs):
        domain = []
        return self._sal_api_v1_get_manifest(extra_domain=domain)

    @http.route(
        URL_V1_MANIFEST_IMAGES,
        type="json",
        methods=["POST"],
        auth="api_key",
        csrf=False,
    )
    def sal_api_v1_get_manifest_with_images(self, **kwargs):
        return self._sal_api_v1_get_manifest(with_tooltips=True)

    @http.route(
        URL_V1_MANIFEST_IDENTIFIER,
        type="json",
        methods=["POST"],
        auth="api_key",
        csrf=False,
    )
    def sal_api_v1_get_manifest_from_identifier(self, identifier, **kwargs):
        domain = [("identifier", "=", identifier)]
        return self._sal_api_v1_get_manifest(with_tooltips=True, extra_domain=domain)
