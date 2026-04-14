# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2021


from odoo import http
from odoo.http import request

URL_V2_BASE = "/api/launcher/v2"
URL_V2_LAUNCHER_IDENTIFIER = URL_V2_BASE + "/identifier/<int:launcher_identifier>"
URL_V2_LAUNCHER_MANIFEST = URL_V2_LAUNCHER_IDENTIFIER + "/Manifest"
URL_V2_LAUNCHER_MANIFEST_IMAGES = URL_V2_LAUNCHER_MANIFEST + "/Images"
URL_V2_LAUNCHER_MANIFEST_ASSET_IDENTIFIER = (
    URL_V2_LAUNCHER_MANIFEST + "/asset/<int:asset_identifier>"
)

API_AUTH = "api_key"

# Changes compared to V1:
# - remove "version" key from the manifest (not needed anymore, we should only rely
#   on the API version)
# - default domain now excludes the "launcher" type


class SoftwareApplicationLauncherControllerV2(http.Controller):
    """Http Controller for Software Application Launcher"""

    #######################################################################
    # API V2
    #######################################################################

    def _sal_api_v2_get_manifest(
        self, launcher_identifier, asset_identifier=False, with_tooltips=False
    ):
        """Build and return the launcher manifest data structure."""
        res = {
            "applications": [],
            "resources": [],
        }
        SoftwareApplication = request.env["software.application"].sudo()
        launcher_id = SoftwareApplication.search(
            [
                ("identifier", "=", launcher_identifier),
                ("type", "=", "launcher"),
            ]
        )
        application_ids = launcher_id.application_ids | launcher_id
        resource_ids = SoftwareApplication
        if asset_identifier:
            application_ids = application_ids.filtered(
                lambda application: application.identifier == asset_identifier
            )
        for application_id in application_ids:
            entry = application_id._get_launcher_manifest_entry(
                with_tooltips=with_tooltips
            )
            res["applications"].append(entry)
            resource_ids |= application_id.resource_ids
        for resource_id in resource_ids:
            entry = resource_id._get_launcher_manifest_entry(
                with_tooltips=with_tooltips
            )
            res["resources"].append(entry)
        return res

    @http.route(
        URL_V2_LAUNCHER_MANIFEST,
        type="json",
        methods=["POST"],
        auth=API_AUTH,
        csrf=False,
    )
    def sal_api_v2_get_manifest(self, launcher_identifier, **kwargs):
        """Return the launcher manifest without tooltip images."""
        return self._sal_api_v2_get_manifest(launcher_identifier)

    @http.route(
        URL_V2_LAUNCHER_MANIFEST_IMAGES,
        type="json",
        methods=["POST"],
        auth=API_AUTH,
        csrf=False,
    )
    def sal_api_v2_get_manifest_with_images(self, launcher_identifier, **kwargs):
        """Return the launcher manifest including tooltip images."""
        return self._sal_api_v2_get_manifest(launcher_identifier, with_tooltips=True)

    @http.route(
        URL_V2_LAUNCHER_MANIFEST_ASSET_IDENTIFIER,
        type="json",
        methods=["POST"],
        auth=API_AUTH,
        csrf=False,
    )
    def sal_api_v2_get_manifest_from_identifier(
        self, launcher_identifier, asset_identifier, **kwargs
    ):
        """Return the launcher manifest filtered by application identifier."""
        return self._sal_api_v2_get_manifest(
            launcher_identifier,
            asset_identifier=asset_identifier,
            with_tooltips=True,
        )
