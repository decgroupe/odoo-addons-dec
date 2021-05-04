# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Mar 2021

import pprint

from odoo import http, fields
from odoo.http import request
from odoo.tools.translate import _

SUCCESS = 0
ERROR = 1

LICENSE_NOT_FOUND = {
    "result": ERROR,
    "message_id": "LICENSE_NOT_FOUND",
    "message":
        "unable to find an existing license for this "
        "identifier and this serial key.",
}

SERIAL_ALREADY_ACTIVATED_ON_HARDWARE = {
    "result": ERROR,
    "message_id": "SERIAL_ALREADY_ACTIVATED_ON_HARDWARE",
    "message":
        "the serial key is already activated with this hardware identifier, "
        "use Validate endpoint to update a license.",
}

SERIAL_EXPIRED = {
    "result": ERROR,
    "message_id": "SERIAL_EXPIRED",
    "message":
        "the expiration date for this serial key is reached, "
        "no activation or validation will be able to proceed.",
}

SERIAL_TOO_MANY_ACTIVATION = {
    "result": ERROR,
    "message_id": "SERIAL_TOO_MANY_ACTIVATION",
    "message":
        "the serial key is already activated on all available hardware "
        "identifier slots. Deactivate from the application or "
        "from your account to free some slots.",
}

SERIAL_NOT_ACTIVATED_ON_HARDWARE = {
    "result": ERROR,
    "message_id": "SERIAL_NOT_ACTIVATED_ON_HARDWARE",
    "message":
        "the serial key is not activated on a machine with the given "
        "hardware identifier and therefore cannot be updated or deactivated.",
}

SERIAL_ACTIVATED_ON_HARDWARE = {
    "result": SUCCESS,
    "message_id": "SERIAL_ACTIVATED_ON_HARDWARE",
    "message":
        "the serial key has been successfully activated on the machine with "
        "the given hardware identifier.",
}

SERIAL_DEACTIVATED_ON_HARDWARE = {
    "result": SUCCESS,
    "message_id": "SERIAL_DEACTIVATED_ON_HARDWARE",
    "message":
        "the serial key has been successfully deactivated on the machine with "
        "the given hardware identifier.",
}

SERIAL_UPDATED_ON_HARDWARE = {
    "result": SUCCESS,
    "message_id": "SERIAL_UPDATED_ON_HARDWARE",
    "message":
        "the serial key activation has been successfully updated on the "
        "machine with the given hardware identifier.",
}

URL_BASE = "/api/license/v1"
URL_IDENTIFIER = URL_BASE + "/identifier/<int:identifier>"
URL_IDENTIFIER_SERIAL_HARDWARE = URL_IDENTIFIER + "/serial/<string:serial>/hardware/<string:hardware>"
URL_IDENTIFIER_HARDWARE = URL_IDENTIFIER + "/hardware/<string:hardware>"


class SoftwareLicenseController(http.Controller):
    """ Http Controller for Software Licensing System
    """

    #######################################################################
    # http://odessa.decindustrie.com:8008/api/license/v1/identifier/{identifier}/serial/{serial}/hardware/{hardware}

    def _get_hardware_id(self, identifier, hardware, serial=False):
        hardware_id = request.env['software.license.hardware']
        if hardware:
            domain = [
                ('name', '=', hardware),
                ('license_id.application_id.identifier', '=', identifier),
            ]
            if serial:
                domain += [
                    ('license_id.serial', '=', serial),
                ]

            hardware_id = hardware_id.sudo().search(domain, limit=1)
        return hardware_id

    @http.route(
        URL_IDENTIFIER_HARDWARE + '/Serial',
        type='json',
        methods=['POST'],
        auth="public",
        csrf=False,
    )
    def get_serial(self, identifier, hardware, **kwargs):
        hardware_id = self._get_hardware_id(identifier, hardware)
        return {'serial': hardware_id.license_id.serial}

    def _get_license_id(self, identifier, serial):
        license_id = request.env['software.license']
        if identifier > 0:
            domain = [
                ('application_id.identifier', '=', identifier),
                ('serial', '=', serial),
            ]
            license_id = license_id.sudo().search(domain, limit=1)
        return license_id

    @http.route(
        URL_IDENTIFIER_SERIAL_HARDWARE + '/Activate',
        type='json',
        methods=['POST'],
        auth="public",
        csrf=False,
    )
    def activate(self, identifier, serial, hardware, **kwargs):
        license_id = self._get_license_id(identifier, serial)
        if not license_id:
            return LICENSE_NOT_FOUND
        elif license_id.expiration_date and \
            fields.Datetime.now() > license_id.expiration_date:
            return SERIAL_EXPIRED
        hardware_id = self._get_hardware_id(identifier, hardware, serial)
        if hardware_id:
            return SERIAL_ALREADY_ACTIVATED_ON_HARDWARE
        elif license_id.max_allowed_hardware > 0 and \
            len(license_id.hardware_ids) >= license_id.max_allowed_hardware:
            return SERIAL_TOO_MANY_ACTIVATION
        else:
            hardware_id = license_id.activate(hardware)
            hardware_id.info = self._get_request_info(request)
            msg = SERIAL_ACTIVATED_ON_HARDWARE
            self._append_common_data(license_id, hardware_id, msg)
            return msg

    @http.route(
        URL_IDENTIFIER_SERIAL_HARDWARE + '/Deactivate',
        type='json',
        methods=['POST'],
        auth="public",
        csrf=False,
    )
    def deactivate(self, identifier, serial, hardware, **kwargs):
        license_id = self._get_license_id(identifier, serial)
        if not license_id:
            return LICENSE_NOT_FOUND
        hardware_id = self._get_hardware_id(identifier, hardware, serial)
        if not hardware_id:
            return SERIAL_NOT_ACTIVATED_ON_HARDWARE
        else:
            hardware_id.unlink()
            res = SERIAL_DEACTIVATED_ON_HARDWARE
            return res

    @http.route(
        URL_IDENTIFIER_SERIAL_HARDWARE + '/Validate',
        type='json',
        methods=['POST'],
        auth="public",
        csrf=False,
    )
    def validate(self, identifier, serial, hardware, **kwargs):
        license_id = self._get_license_id(identifier, serial)
        if not license_id:
            return LICENSE_NOT_FOUND
        elif license_id.expiration_date and \
            fields.Datetime.now() > license_id.expiration_date:
            return SERIAL_EXPIRED
        hardware_id = self._get_hardware_id(identifier, hardware, serial)
        if not hardware_id:
            return SERIAL_NOT_ACTIVATED_ON_HARDWARE
        else:
            hardware_id.info = self._get_request_info(request)
            msg = SERIAL_UPDATED_ON_HARDWARE
            self._append_common_data(license_id, hardware_id, msg)
            return msg

    def _get_request_info(self, request):
        res = {}
        res['httprequest'] = {'remote_addr': request.httprequest.remote_addr}
        res['jsonrequest'] = request.jsonrequest.copy()
        return pprint.pformat(res)

    def _append_common_data(self, license_id, hardware_id, msg):
        msg['server_date'] = fields.Date.to_string(fields.Date.today())
        msg['server_datetime'] = fields.Datetime.to_string(
            fields.Datetime.now()
        )
        self._append_license_string(hardware_id, msg)
        self._append_remaining_activation(license_id, msg)

    def _append_license_string(self, hardware_id, msg):
        msg['license_string'] = hardware_id.get_license_string()

    def _append_remaining_activation(self, license_id, msg):
        msg['remaining_activation'] = license_id.get_remaining_activation()

    #######################################################################

    def _get_default_domain(self):
        partner = request.env.user.partner_id
        return [
            # ('|'),
            # ('partner_id', 'parent_of', partner.id),
            ('partner_id', 'child_of', partner.id),
            ('portal_published', '=', True),
        ]

    @http.route(
        URL_IDENTIFIER + '/Licenses',
        type='json',
        methods=['POST'],
        auth="user",
        csrf=False,
    )
    def get_licenses(self, identifier, **kwargs):
        SoftwareLicense = request.env['software.license']
        domain = self._get_default_domain()
        if identifier:
            domain += [('application_id.identifier', '=', identifier)]
        license_ids = SoftwareLicense.search(domain)
        res = {}
        for license_id in license_ids:
            license_data = license_id.sudo()._prepare(include_serial=False)
            license_data['hardwares'] = license_id.sudo().get_hardwares_dict()
            self._append_remaining_activation(license_id, license_data)
            res[license_id.serial] = license_data
        return res

    @http.route(
        URL_BASE + '/Licenses',
        type='json',
        methods=['POST'],
        auth="user",
        csrf=False,
    )
    def get_all_licenses(self, **kwargs):
        return self.get_licenses(identifier=False)
