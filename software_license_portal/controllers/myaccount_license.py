# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2021

from odoo import _, http
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.addons.portal.controllers.portal import pager as portal_pager
from odoo.exceptions import AccessError
from odoo.http import request
from odoo.osv.expression import OR


class LicenseCustomerPortal(CustomerPortal):
    #########################################################################

    def _prepare_portal_layout_values(self):
        values = super(LicenseCustomerPortal, self)._prepare_portal_layout_values()
        SoftwareLicense = request.env["software.license"]
        domain = SoftwareLicense._get_license_default_portal_domain(
            request_partner_id=request.env.user.partner_id,
            include_pass_licenses=False,
        )
        license_count = SoftwareLicense.search_count(domain)
        values["license_count"] = license_count
        return values

    def _software_license_check_access(self, lic_id):
        license_id = request.env["software.license"].browse([lic_id])
        # license_id = license_id.sudo()
        try:
            license_id.check_access_rights("read")
            license_id.check_access_rule("read")
        except AccessError:
            raise
        return license_id

    def _get_searchbar_sortings(self):
        return {
            "date": {"label": _("Newest"), "order": "create_date desc"},
            "serial": {"label": _("Serial"), "order": "serial"},
            "application": {"label": _("Application"), "order": "application_id"},
        }

    def _get_searchbar_inputs(self):
        # search input (text)
        return {
            "serial": {"input": "serial", "label": _("Search in Serials")},
            "application_id": {
                "input": "application",
                "label": _("Search in Applications"),
            },
            "hardware_ids": {
                "input": "hardware",
                "label": _("Search in Hardware identifiers"),
            },
        }

    def _get_searchbar_meta_inputs(self):
        return {
            "all": {"input": "all", "label": _("Search in All")},
        }

    def _get_searchbar_filters(self):
        return {"all": {"label": _("All"), "domain": []}}

    @http.route(
        ["/my/licenses", "/my/licenses/page/<int:page>"],
        type="http",
        auth="user",
        website=True,
    )
    def portal_my_licenses(
        self,
        page=1,
        date_begin=None,
        date_end=None,
        sortby=None,
        filterby=None,
        search=None,
        search_in="all",
        **kw
    ):
        values = self._prepare_portal_layout_values()
        SoftwareLicense = request.env["software.license"]
        domain = SoftwareLicense._get_license_default_portal_domain(
            request_partner_id=request.env.user.partner_id,
            include_pass_licenses=False,
        )

        searchbar_sortings = self._get_searchbar_sortings()
        searchbar_inputs = self._get_searchbar_inputs()
        searchbar_meta_inputs = self._get_searchbar_meta_inputs()

        if search and search_in:
            search_domain = []
            for search_property in [
                k
                for (k, v) in searchbar_inputs.items()
                if search_in in (v["input"], "all")
            ]:
                search_domain = OR(
                    [search_domain, [(search_property, "ilike", search)]]
                )
            domain += search_domain
        searchbar_inputs.update(searchbar_meta_inputs)

        searchbar_filters = self._get_searchbar_filters()
        # search filters (by application)
        # for app in request.env['software.application'].search(
        #     [('portal_published', '=', True)]
        # ):
        #     searchbar_filters.update(
        #         {
        #             str(app.id):
        #                 {
        #                     'label': app.name,
        #                     'domain': [('application_id', '=', app.id)]
        #                 }
        #         }
        #     )

        # default sort by order
        if not sortby:
            sortby = "date"
        order = searchbar_sortings[sortby]["order"]

        # default filter by value
        if not filterby:
            filterby = "all"
        domain += searchbar_filters[filterby]["domain"]

        # count for pager
        license_count = SoftwareLicense.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/licenses",
            url_args={},
            total=license_count,
            page=page,
            step=self._items_per_page,
        )
        # content according to pager and archive selected
        licenses = SoftwareLicense.search(
            domain, order=order, limit=self._items_per_page, offset=pager["offset"]
        )
        values.update(
            {
                "date": date_begin,
                "licenses": licenses,
                "page_name": "license",
                "pager": pager,
                "default_url": "/my/licenses",
                "searchbar_sortings": searchbar_sortings,
                "searchbar_inputs": searchbar_inputs,
                "search_in": search_in,
                "sortby": sortby,
                "searchbar_filters": searchbar_filters,
                "filterby": filterby,
            }
        )
        return request.render("software_license_portal.portal_my_licenses", values)

    @http.route(["/my/license/<int:license_id>"], type="http", website=True)
    def portal_my_license(self, license_id=None, **kw):
        try:
            license_sudo = self._software_license_check_access(license_id)
        except AccessError:
            return request.redirect("/my")
        values = self._license_get_page_view_values(license_sudo, **kw)
        return request.render(
            "software_license_portal.portal_software_license_page", values
        )

    def _license_get_page_view_values(self, license_sudo, **kwargs):
        files = request.env["ir.attachment"].search(
            [("res_model", "=", "software.license"), ("res_id", "=", license_sudo.id)]
        )
        values = {
            "page_name": "license",
            "license": license_sudo,
            "files": files,
        }

        if kwargs.get("error"):
            values["error"] = kwargs["error"]
        if kwargs.get("warning"):
            values["warning"] = kwargs["warning"]
        if kwargs.get("success"):
            values["success"] = kwargs["success"]

        return values

    @http.route(
        ["/my/license/deactivate"],
        type="http",
        auth="user",
        methods=["POST"],
        website=True,
    )
    def _license_deactivate_hardware(self, hardware_id, license_id, **kw):
        license_id = int(license_id)
        hardware_id = int(hardware_id)
        SoftwareLicense = request.env["software.license"].sudo()
        SoftwareLicense.browse(license_id).deactivate(hardware_id)
        return request.redirect("/my/license/%d" % (license_id))
