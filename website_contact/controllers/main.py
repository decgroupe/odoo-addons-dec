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

    def _get_origins(self):
        return {
            'radio_1': _("A private person"),
            'radio_2': _("A school"),
            'radio_3': _("A company "),
        }

    def _get_description(self):
        res = _("Company Name") + ':\n-\n'
        res += _("Full Address (street, zipcode, city)") + ':\n-\n'
        res += _("Your Request") + ':\n-\n'
        return res

    def _save_attachments(self, model, id):
        for c_file in request.httprequest.files.getlist('attachment'):
            data = c_file.read()
            if c_file.filename:
                request.env['ir.attachment'].sudo().create(
                    {
                        'name': c_file.filename,
                        'datas': base64.b64encode(data),
                        'datas_fname': c_file.filename,
                        'res_model': model,
                        'res_id': id
                    }
                )

    def _default_return(self):
        return werkzeug.utils.redirect("/")

    #######################################################################

    @http.route(
        URL_BASE + '/ticket/new', type="http", auth="public", website=True
    )
    def create_new_ticket_from_contactform(self, **kw):
        categories = http.request.env['helpdesk.ticket.category']. \
            search([('active', '=', True), ('public_ok', '=', True)])
        return http.request.render(
            'website_contact.create_contact_message', {
                'origin': self._get_origins(),
                'categories': categories,
                'description': self._get_description(),
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
        description = kw.get('origin') + '\n' + kw.get('description')
        vals = {
            'partner_name': kw.get('name'),
            'company_id': request.env.user.company_id.id,
            'category_id': category,
            'team_id': team_id.id,
            'user_id': False,
            'partner_email': kw.get('email'),
            'description': tools.plaintext2html(description),
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
            ticket_id.message_subscribe(partner_ids=partner_id.ids)
        if kw.get('attachment'):
            self._save_attachments('helpdesk.ticket', ticket_id.id)
        # return self._default_return()

    #######################################################################

    @http.route(
        URL_BASE + '/lead/new', type="http", auth="public", website=True
    )
    def create_new_lead_from_contactform(self, **kw):
        return http.request.render(
            'website_contact.create_contact_message', {
                'origin': self._get_origins(),
                'description': self._get_description(),
                'form_action': URL_BASE + '/lead/submit',
            }
        )

    @http.route(
        URL_BASE + '/lead/submit',
        type="http",
        auth="public",
        website=True,
        csrf=True
    )
    def submit_lead_from_contactform(self, **kw):
        partner_id = request.env['res.partner'].sudo().search(
            [('email', 'ilike', kw.get('email'))], limit=1
        )
        description = kw.get('origin') + '\n' + kw.get('description')
        utm_source_id = request.env.ref(
            'website_contact.utm_source_contact_form'
        )
        vals = {
            'partner_name': kw.get('name'),
            'company_id': request.env.user.company_id.id,
            'user_id': False,
            'partner_email': kw.get('email'),
            'description': description,
            'name': kw.get('subject'),
            'attachment_ids': False,
            'partner_id': partner_id.id,
            'source_id': utm_source_id.id,
        }
        # Create the lead
        lead_id = request.env['crm.lead'].sudo().with_context(
            contact_lead=True
        ).create(vals)
        # And subscribe the partner if retrieved from email
        if partner_id:
            lead_id.message_subscribe(partner_ids=partner_id.ids)
        if kw.get('attachment'):
            self._save_attachments('crm.lead', lead_id.id)

        # return self._default_return()
