# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Mar 2021

from odoo import http
from odoo.http import request
from odoo.tools.translate import _

[
    # html GET
    '/software_license_api/v1/identifier/<int:identifier>/serial/<string:serial>',
    # json POST
    '/software_license_api/v1/identifier/<int:identifier>/serial/<string:serial>/hardware_id/<string:hardware_id>/activate',
    '/software_license_api/v1/identifier/<int:identifier>/serial/<string:serial>/hardware_id/<string:hardware_id>/deactivate',
    '/software_license_api/v1/identifier/<int:identifier>/serial/<string:serial>',
    '/software_license_api/v1/identifier/<int:identifier>/serial/<string:serial>',
]


class SoftwareLicenseController(http.Controller):
    # http://odessa.decindustrie.com:8008/software_license_api/identifier/1035/serial/DN7SW-HNKFU-SEIR8-82AA6
    @http.route(
        '/software_license_api/v1/identifier/<int:identifier>/serial/<string:serial>',
        type='json',
        methods=['POST', 'GET'],
        auth="public",
        csrf=False,
    )
    def test(self, identifier, serial, **kwargs):
        license_id = False
        if identifier > 0:
            license_id = request.env['software.license'].sudo().search(
                [
                    ('application_id.application_id', '=', identifier),
                    ('serial', '=', serial),
                ]
            )
        if not license_id:
            return False
        return {
            'datetime': license_id.datetime,
        }

    # @http.route('/rating/<string:token>/<int:rate>', type='http', auth="public")
    # def open_rating(self, token, rate, **kwargs):
    #     assert rate in (1, 5, 10), "Incorrect rating"
    #     rating = request.env['rating.rating'].sudo().search([('access_token', '=', token)])
    #     if not rating:
    #         return request.not_found()
    #     rate_names={
    #         5: _("not satisfied"),
    #         1: _("highly dissatisfied"),
    #         10: _("satisfied")
    #     }
    #     rating.write({'rating': rate, 'consumed': True})
    #     lang = rating.partner_id.lang or 'en_US'
    #     return request.env['ir.ui.view'].with_context(lang=lang).render_template('rating.rating_external_page_submit', {
    #         'rating': rating, 'token': token,
    #         'rate_name': rate_names[rate], 'rate': rate
    #     })

    # @http.route(['/rating/<string:token>/<int:rate>/submit_feedback'], type="http", auth="public", methods=['post'])
    # def submit_rating(self, token, rate, **kwargs):
    #     rating = request.env['rating.rating'].sudo().search([('access_token', '=', token)])
    #     if not rating:
    #         return request.not_found()
    #     record_sudo = request.env[rating.res_model].sudo().browse(rating.res_id)
    #     record_sudo.rating_apply(rate, token=token, feedback=kwargs.get('feedback'))
    #     lang = rating.partner_id.lang or 'en_US'
    #     return request.env['ir.ui.view'].with_context(lang=lang).render_template('rating.rating_external_page_view', {
    #         'web_base_url': request.env['ir.config_parameter'].sudo().get_param('web.base.url'),
    #         'rating': rating,
    #     })
