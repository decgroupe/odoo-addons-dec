# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2021

import logging
import werkzeug
import base64

import odoo.http as http
from odoo.http import request

_logger = logging.getLogger(__name__)

URL_BASE = "/api/helpdesk/v1"
URL_TICKET = URL_BASE + "/Ticket"


class HelpdeskTicketPublicController(http.Controller):
    """ Http Public Controller for Helpdesk
    """

    #######################################################################

    def _get_project(self, vals):
        res = False
        if vals.get('project'):
            res = request.env['project.project'].sudo().search(
                [('name', '=', vals.get('project'))]
            ).id
        return res

    def _get_team(self, vals):
        res = False
        if vals.get('team'):
            res = request.env['helpdesk.ticket.team'].sudo().search(
                [('name', '=', vals.get('team'))]
            ).id
        return res

    def _get_category(self, vals):
        res = False
        if vals.get('category'):
            res = request.env['helpdesk.ticket.category'].sudo().search(
                [('name', '=', vals.get('category'))]
            ).id
        return res

    def _get_channel(self, vals):
        res = False
        if vals.get('channel'):
            res = request.env['helpdesk.ticket.channel'].sudo().search(
                [('name', '=', vals.get('channel'))]
            ).id
        return res

    @http.route(
        URL_TICKET + '/New',
        type='json',
        methods=['POST'],
        auth="public",
        csrf=False,
    )
    def create_new_ticket(self, **kw):
        vals = {
            'partner_name': kw.get('name'),
            'partner_email': kw.get('email'),
            'project_id': self._get_project(kw),
            'team_id': self._get_team(kw),
            'category_id': self._get_category(kw),
            'channel_id': self._get_channel(kw),
            'name': kw.get('subject'),
            'description': kw.get('description'),
        }
        new_ticket = request.env['helpdesk.ticket'].sudo().with_context(
            public_ticket=True
        ).create(vals)
        return {'ticket': new_ticket.number}
