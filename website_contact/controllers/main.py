# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2021

import logging
import werkzeug
import base64

import odoo.http as http
from odoo.http import request
from odoo import _, tools

_logger = logging.getLogger(__name__)

URL_BASE = "/contact"


class WebsiteContactController(http.Controller):
    """ Http Controller for Contact Forms
    """

    #######################################################################

    @http.route(
        URL_BASE + '/ticket/new', type="http", auth="public", website=True
    )
    def create_new_ticket_from_contactform(self, **kw):
        categories = http.request.env['helpdesk.ticket.category']. \
            search([('active', '=', True), ('public_ok', '=', True)])
        origin = {
            'radio_1': _("A private person"),
            'radio_2': _("A school"),
            'radio_3': _("A company "),
        }
        description = _("Company Name") + ':\n-\n'
        description += _("Full Address (street, zipcode, city)") + ':\n-\n'
        description += _("Your Request") + ':\n-\n'

        return http.request.render(
            'website_contact.create_contact_message', {
                'origin': origin,
                'categories': categories,
                'description': description,
                'form_action': URL_BASE + '/ticket/submit',
            }
        )

    @http.route(
        URL_BASE + '/ticket/submit',
        type="http",
        auth="public",
        website=True,
        csrf=True
    )
    def submit_ticket_from_contactform(self, **kw):
        channel_id = request.env['helpdesk.ticket.channel'].sudo().search(
            [('name', '=', 'Web')]
        )
        partner_id = request.env['res.partner'].sudo().search(
            [('email', 'ilike', kw.get('email'))], limit=1
        )
        team_id = request.env['helpdesk.ticket.team'].sudo()
        category = kw.get('category')
        if category:
            team_ids = team_id.search([('category_ids', 'in', [category])])
            if len(team_ids) == 1:
                # Assign `team_id` if there is one and only one match
                team_id = team_ids[0]
        vals = {
            'partner_name': kw.get('name'),
            'company_id': request.env.user.company_id.id,
            'category_id': category,
            'team_id': team_id.id,
            'user_id': False,
            'partner_email': kw.get('email'),
            'description': tools.plaintext2html(kw.get('description')),
            'name': kw.get('subject'),
            'attachment_ids': False,
            'channel_id': channel_id.id,
            'partner_id': partner_id.id,
        }
        # Create the ticket
        ticket_id = request.env['helpdesk.ticket'].sudo().with_context(
            contact_ticket=True
        ).create(vals)
        # And subscribe the partner if retrieved from email
        if partner_id:
            ticket_id.message_subscribe(
                partner_ids=request.env.user.partner_id.ids
            )
        if kw.get('attachment'):
            for c_file in request.httprequest.files.getlist('attachment'):
                data = c_file.read()
                if c_file.filename:
                    request.env['ir.attachment'].sudo().create(
                        {
                            'name': c_file.filename,
                            'datas': base64.b64encode(data),
                            'datas_fname': c_file.filename,
                            'res_model': 'helpdesk.ticket',
                            'res_id': ticket_id.id
                        }
                    )
        # return werkzeug.utils.redirect("/")
