# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2021

import logging

import odoo.http as http
from odoo.http import request

_logger = logging.getLogger(__name__)

URL_BASE = "/api/crm/v1"
URL_PARTNER = URL_BASE + "/Partner"


class CRM3CXController(http.Controller):
    """ Http Public Controller for Helpdesk
    """

    #######################################################################

    @http.route(
        URL_PARTNER + '/Get',
        type='json',
        methods=['POST'],
        auth="api_key",
        csrf=False,
    )
    def SearchPartner(self, **kw):
        session_ani = kw.get('session_ani')
        number = session_ani.lstrip("0").replace(" ", "%")
        domain = [
            '|',
            ('phone', 'ilike', number),
            ('mobile', 'ilike', number),
        ]
        partner_id = request.env['res.partner'].sudo().search(domain, limit=1)
        if partner_id:
            # Get firstname and lastname from name
            name = partner_id.name.split(" ", 1)
            if len(name) > 1:
                name = [" ".join(name[1:]), name[0]]
            else:
                while len(name) < 2:
                    name.append('')
            firstname = name[1]
            lastname = name[0]

            res = {
                # Firstname
                'firstname': firstname or '',
                # Lastname
                'lastname': lastname or '',
                # Mobile
                'phonenumber': partner_id.mobile or '',
                'company': partner_id.commercial_partner_id.name or '',
                # Odoo partner ID to sync data
                'tag': str(partner_id.id),
                # Mobile 2
                'pv_an0': '',
                # Domicile
                'pv_an1': '',
                # Domicile 2
                'pv_an2': '',
                # Entreprise
                'pv_an3': partner_id.phone or '',
                # Entreprise 2
                'pv_an4': '',
                # E-mail
                'pv_an5': partner_id.email or '',
                # Autre
                'pv_an6': '',
                # Fax entreprise
                'pv_an7': partner_id.fax or '',
                # Fax domicile
                'pv_an8': '',
                # ---
                'pv_an9': '',
            }
        else:
            res = {}
        _logger.info("{} match for {}".format(session_ani, res))
        return res
