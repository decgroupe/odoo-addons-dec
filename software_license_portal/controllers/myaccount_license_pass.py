# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2021

from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.addons.portal.controllers.portal import pager as portal_pager
from odoo.exceptions import AccessError

from odoo.osv.expression import OR


class LicensePassCustomerPortal(CustomerPortal):

    #########################################################################

    def _prepare_portal_layout_values(self):
        values = super(LicensePassCustomerPortal, self)\
            ._prepare_portal_layout_values()
        SoftwarePass = request.env['software.license.pass']
        domain = SoftwarePass._get_default_portal_domain(
            request.env.user.partner_id
        )
        pass_count = SoftwarePass.search_count(domain)
        values['license_pass_count'] = pass_count
        return values

    def _software_pass_check_access(self, pass_id):
        pass_id = request.env['software.license.pass'].browse([pass_id])
        #pass_id = pass_id.sudo()
        try:
            pass_id.check_access_rights('read')
            pass_id.check_access_rule('read')
        except AccessError:
            raise
        return pass_id

    def _get_searchbar_sortings(self):
        return {
            'date': {
                'label': _('Newest'),
                'order': 'create_date desc'
            },
            'serial': {
                'label': _('Serial'),
                'order': 'serial'
            },
            'pack': {
                'label': _('Pack'),
                'order': 'pack_id'
            },
        }

    def _get_searchbar_inputs(self):
        # search input (text)
        return {
            'serial': {
                'input': 'serial',
                'label': _('Search in Serials')
            },
            'pack_id': {
                'input': 'pack',
                'label': _('Search in Packs')
            },
            'hardware_ids':
                {
                    'input': 'hardware',
                    'label': _('Search in Hardware identifiers')
                },
        }

    def _get_searchbar_meta_inputs(self):
        return {
            'all': {
                'input': 'all',
                'label': _('Search in All')
            },
        }

    def _get_searchbar_filters(self):
        return {'all': {'label': _('All'), 'domain': []}}

    @http.route(
        ['/my/passes', '/my/passes/page/<int:page>'],
        type='http',
        auth="user",
        website=True,
    )
    def portal_my_passes(
        self,
        page=1,
        date_begin=None,
        date_end=None,
        sortby=None,
        filterby=None,
        search=None,
        search_in='all',
        **kw
    ):
        values = self._prepare_portal_layout_values()
        SoftwarePass = request.env['software.license.pass']
        domain = SoftwarePass._get_default_portal_domain(
            request.env.user.partner_id
        )

        searchbar_sortings = self._get_searchbar_sortings()
        searchbar_inputs = self._get_searchbar_inputs()
        searchbar_meta_inputs = self._get_searchbar_meta_inputs()

        if search and search_in:
            search_domain = []
            for search_property in [
                k for (k, v) in searchbar_inputs.items()
                if search_in in (v['input'], 'all')
            ]:
                search_domain = OR(
                    [search_domain, [(search_property, 'ilike', search)]]
                )
            domain += search_domain
        searchbar_inputs.update(searchbar_meta_inputs)

        searchbar_filters = self._get_searchbar_filters()

        # default sort by order
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        # default filter by value
        if not filterby:
            filterby = 'all'
        domain += searchbar_filters[filterby]['domain']

        # count for pager
        pass_count = SoftwarePass.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/passes",
            url_args={},
            total=pass_count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        passes = SoftwarePass.search(
            domain,
            order=order,
            limit=self._items_per_page,
            offset=pager['offset']
        )
        values.update(
            {
                'date': date_begin,
                'passes': passes,
                'page_name': 'license_pass',
                'pager': pager,
                'default_url': '/my/passes',
                'searchbar_sortings': searchbar_sortings,
                'searchbar_inputs': searchbar_inputs,
                'search_in': search_in,
                'sortby': sortby,
                'searchbar_filters': searchbar_filters,
                'filterby': filterby,
            }
        )
        return request.render(
            "software_license_portal.portal_my_passes", values
        )

    @http.route(['/my/pass/<int:pass_id>'], type='http', website=True)
    def portal_my_pass(self, pass_id=None, **kw):
        try:
            pass_sudo = self._software_pass_check_access(pass_id)
        except AccessError:
            return request.redirect('/my')
        values = self._pass_get_page_view_values(pass_sudo, **kw)
        return request.render(
            "software_license_portal.portal_software_pass_page", values
        )

    def _pass_get_page_view_values(self, pass_sudo, **kwargs):
        files = request.env['ir.attachment'].search(
            [
                ('res_model', '=', 'software.license.pass'),
                ('res_id', '=', pass_sudo.id)
            ]
        )
        values = {
            'page_name': 'license_pass',
            'license_pass': pass_sudo,
            "files": files,
        }

        if kwargs.get('error'):
            values['error'] = kwargs['error']
        if kwargs.get('warning'):
            values['warning'] = kwargs['warning']
        if kwargs.get('success'):
            values['success'] = kwargs['success']

        return values

    @http.route(
        ["/my/pass/deactivate"],
        type="http",
        auth="user",
        methods=["POST"],
        website=True,
    )
    def _pass_deactivate_hardware(self, pass_id, hardware_name, **kw):
        pass_id = int(pass_id)
        SoftwareLicensePass = request.env['software.license.pass'].sudo()
        SoftwareLicensePass.browse(pass_id).deactivate(hardware_name)
        return request.redirect('/my/pass/%d' % (pass_id))
