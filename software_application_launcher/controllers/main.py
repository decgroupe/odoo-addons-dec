# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2021

import pprint

from odoo import http, fields
from odoo.http import request
from odoo.tools.translate import _
import odoo.tools.convert as odoo_convert

URL_BASE_V1 = "/api/launcher/v1"
URL_MANIFEST = URL_BASE_V1 + "/Manifest"
URL_MANIFEST_IMAGES = URL_MANIFEST + "/Images"
URL_MANIFEST_IDENTIFIER = URL_MANIFEST + "/identifier/<int:identifier>"


class SoftwareApplicationLauncherController(http.Controller):
    """ Http Controller for Software Application Launcher
    """

    #######################################################################

    def _get_manifest(self, with_tooltips=False, extra_domain=False):
        res = {
            'version': 2,
            'applications': [],
            'resources': [],
        }
        SoftwareApplication = request.env['software.application']
        domain = SoftwareApplication._get_launcher_manifest_domain()
        if extra_domain:
            domain += extra_domain
        asset_ids = SoftwareApplication.search(domain)
        for asset_id in asset_ids:
            entry = asset_id._get_launcher_manifest_entry(
                with_tooltips=with_tooltips
            )
            if asset_id.type == 'inhouse':
                res['applications'].append(entry)
            elif asset_id.type == 'resource':
                res['resources'].append(entry)
        return res

    @http.route(
        URL_MANIFEST,
        type='json',
        methods=['POST'],
        auth="api_key",
        csrf=False,
    )
    def get_manifest(self, **kwargs):
        domain = []
        return self._get_manifest(extra_domain=domain)

    @http.route(
        URL_MANIFEST_IMAGES,
        type='json',
        methods=['POST'],
        auth="api_key",
        csrf=False,
    )
    def get_manifest_with_images(self, **kwargs):
        return self._get_manifest(with_tooltips=True)

    @http.route(
        URL_MANIFEST_IDENTIFIER,
        type='json',
        methods=['POST'],
        auth="api_key",
        csrf=False,
    )
    def get_manifest_from_identifier(self, identifier, **kwargs):
        domain = [('identifier', '=', identifier)]
        return self._get_manifest(with_tooltips=True, extra_domain=domain)
