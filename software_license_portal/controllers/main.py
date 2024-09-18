# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2021

import pprint
import json

import odoo.tools.convert as odoo_convert
from odoo import fields, http
from odoo.http import request
from odoo.tools.translate import _

SUCCESS = 0
ERROR = 1

LICENSE_NOT_FOUND = {
    "result": ERROR,
    "message_id": "LICENSE_NOT_FOUND",
    "message": "unable to find an existing license for this "
    "identifier and this serial key.",
}

HARDWARE_NOT_FOUND = {
    "result": ERROR,
    "message_id": "HARDWARE_NOT_FOUND",
    "message": "this hardware identifier is not used to activate/validate any "
    "serial key on our system.",
}

SERIAL_ALREADY_ACTIVATED_ON_HARDWARE = {
    "result": ERROR,
    "message_id": "SERIAL_ALREADY_ACTIVATED_ON_HARDWARE",
    "message": "the serial key is already activated with this hardware identifier, "
    "use Validate endpoint to update a license.",
}

SERIAL_EXPIRED = {
    "result": ERROR,
    "message_id": "SERIAL_EXPIRED",
    "message": "the expiration date for this serial key is reached, "
    "no activation or validation will be able to proceed.",
}

SERIAL_TOO_MANY_ACTIVATION = {
    "result": ERROR,
    "message_id": "SERIAL_TOO_MANY_ACTIVATION",
    "message": "the serial key is already activated on all available hardware "
    "identifier slots. Deactivate from the application or "
    "from your account to free some slots.",
}

SERIAL_NOT_ACTIVATED_ON_HARDWARE = {
    "result": ERROR,
    "message_id": "SERIAL_NOT_ACTIVATED_ON_HARDWARE",
    "message": "the serial key is not activated on a machine with the given "
    "hardware identifier and therefore cannot be updated or deactivated.",
}

ALL_SERIALS_DEACTIVATED_ON_HARDWARE = {
    "result": SUCCESS,
    "message_id": "ALL_SERIALS_DEACTIVATED_ON_HARDWARE",
    "message": "all serial keys have been successfully deactivated on the machine "
    "with the given hardware identifier.",
}

SERIAL_ACTIVATED_ON_HARDWARE = {
    "result": SUCCESS,
    "message_id": "SERIAL_ACTIVATED_ON_HARDWARE",
    "message": "the serial key has been successfully activated on the machine with "
    "the given hardware identifier.",
}

SERIAL_DEACTIVATED_ON_HARDWARE = {
    "result": SUCCESS,
    "message_id": "SERIAL_DEACTIVATED_ON_HARDWARE",
    "message": "the serial key has been successfully deactivated on the machine with "
    "the given hardware identifier.",
}

SERIAL_UPDATED_ON_HARDWARE = {
    "result": SUCCESS,
    "message_id": "SERIAL_UPDATED_ON_HARDWARE",
    "message": "the serial key activation has been successfully updated on the "
    "machine with the given hardware identifier.",
}

URL_BASE_V1 = "/api/license/v1"
URL_BASE_V2 = "/api/license/v2"

URL_VAR_IDENTIFIER = "/identifier/<int:identifier>"
URL_VAR_SERIAL = "/serial/<string:serial>"
URL_VAR_HARDWARE = "/hardware/<string:hardware>"


class SoftwareLicenseController(http.Controller):
    """Http Controller for Software Licensing System"""

    #######################################################################

    @http.route(
        URL_BASE_V1 + "/ResetUnitTesting",
        type="json",
        methods=["POST"],
        auth="public",
        csrf=False,
    )
    def reset_unit_testing(self, **kwargs):  # pragma: no cover
        # Keep a reference on the previous function
        previous_safe_eval = odoo_convert.safe_eval
        # Define a local context and override default `safe_eval`
        local_ctx = {
            "same_hardware_identifier": "SAME",
            "other_hardware_identifier": "OTHER",
        }
        # Let the testing user update local context with data from json
        local_ctx.update(request.params.copy())
        odoo_convert.safe_eval = lambda expr, ctx={}: odoo_convert.s_eval(
            expr, ctx, local_ctx, nocopy=True
        )
        try:
            for file in [
                "data/unit_testing_software_application.xml",
                "data/unit_testing_software_license.xml",
            ]:
                odoo_convert.convert_file(
                    request.env.cr,
                    "software_license_portal",
                    file,
                    {},
                    mode="init",
                    kind="data",
                )
        finally:
            # Restore previous function
            odoo_convert.safe_eval = previous_safe_eval

    #######################################################################

    def _get_hardware_id(self, hardware, identifier, serial=False):
        hardware_id = (
            request.env["software.license.hardware"]
            .sudo()
            .get_hardware_ids(hardware, identifier, serial, limit=1)
        )
        return hardware_id

    @http.route(
        URL_BASE_V1 + URL_VAR_IDENTIFIER + URL_VAR_HARDWARE + "/Serial",
        type="json",
        methods=["POST"],
        auth="public",
        csrf=False,
    )
    def get_serial(self, identifier, hardware, **kwargs):
        hardware_id = self._get_hardware_id(hardware, identifier)
        return {"serial": hardware_id.license_id.serial}

    def _get_license_id(self, identifier, serial):
        license_id = (
            request.env["software.license"]
            .sudo()
            .get_license_ids(identifier, serial, limit=1)
        )
        return license_id

    @http.route(
        URL_BASE_V1
        + URL_VAR_IDENTIFIER
        + URL_VAR_SERIAL
        + URL_VAR_HARDWARE
        + "/Activate",
        type="json",
        methods=["POST"],
        auth="public",
        csrf=False,
    )
    def activate(self, identifier, serial, hardware, **kwargs):
        license_id = self._get_license_id(identifier, serial)
        if not license_id:
            return LICENSE_NOT_FOUND
        elif license_id.check_expired():
            return SERIAL_EXPIRED
        hardware_id = self._get_hardware_id(hardware, identifier, serial)
        if hardware_id:
            return SERIAL_ALREADY_ACTIVATED_ON_HARDWARE
        elif license_id.check_max_activation_reached(hardware_name=hardware):
            return SERIAL_TOO_MANY_ACTIVATION
        else:
            info = self._get_request_info(request)
            hardware_id = license_id.activate(hardware, info)
            msg = SERIAL_ACTIVATED_ON_HARDWARE.copy()
            # common data will contain the validated license string
            self._append_common_data(license_id, hardware_id, msg)
            return msg

    @http.route(
        URL_BASE_V1
        + URL_VAR_IDENTIFIER
        + URL_VAR_SERIAL
        + URL_VAR_HARDWARE
        + "/Deactivate",
        type="json",
        methods=["POST"],
        auth="public",
        csrf=False,
    )
    def deactivate(self, identifier, serial, hardware, **kwargs):
        license_id = self._get_license_id(identifier, serial)
        if not license_id:
            return LICENSE_NOT_FOUND
        hardware_id = self._get_hardware_id(hardware, identifier, serial)
        if not hardware_id:
            return SERIAL_NOT_ACTIVATED_ON_HARDWARE
        else:
            hardware_id.unlink()
            return SERIAL_DEACTIVATED_ON_HARDWARE

    @http.route(
        URL_BASE_V1
        + URL_VAR_IDENTIFIER
        + URL_VAR_SERIAL
        + URL_VAR_HARDWARE
        + "/Validate",
        type="json",
        methods=["POST"],
        auth="public",
        csrf=False,
    )
    def validate(self, identifier, serial, hardware, **kwargs):
        license_id = self._get_license_id(identifier, serial)
        if not license_id:
            return LICENSE_NOT_FOUND
        elif license_id.check_expired():
            return SERIAL_EXPIRED
        hardware_id = self._get_hardware_id(hardware, identifier, serial)
        if not hardware_id:
            return SERIAL_NOT_ACTIVATED_ON_HARDWARE
        else:
            hardware_id.info = self._get_request_info(request)
            msg = SERIAL_UPDATED_ON_HARDWARE.copy()
            # common data will contain the validated license string
            self._append_common_data(license_id, hardware_id, msg)
            return msg

    def _get_request_info(self, req):
        res = {}
        ip_addr = req.httprequest.environ.get("HTTP_X_FORWARDED_FOR")
        if ip_addr:
            ip_addr = ip_addr.split(",")[0]
        else:
            ip_addr = req.httprequest.remote_addr
        res["httprequest"] = {"remote_addr": ip_addr}
        if "telemetry" in req.params:
            res["telemetry"] = req.params["telemetry"].copy()
        else:
            # Fallback to pre 2023 implementation where telemetry
            # (aka sysinfos) data were directly put into the main params
            # json object
            res["telemetry"] = req.params.copy()
        return json.dumps(res, indent=4)

    def _append_common_data(self, license_id, hardware_id, msg):
        msg["server_date"] = fields.Date.to_string(fields.Date.today())
        msg["server_datetime"] = fields.Datetime.to_string(fields.Datetime.now())
        self._append_license_string(hardware_id, msg)
        self._append_remaining_activation(license_id, msg)
        self._append_expiration_dates(license_id, hardware_id, msg)

    def _append_license_string(self, hardware_id, msg):
        msg["license_string"] = hardware_id.get_license_string()

    def _append_remaining_activation(self, license_id, msg):
        msg["remaining_activation"] = license_id.get_remaining_activation()
        pass_remaining_activation = 0
        if license_id.pass_id:
            pass_remaining_activation = license_id.pass_id.get_remaining_activation()
        msg["pass_remaining_activation"] = pass_remaining_activation

    def _append_expiration_dates(self, license_id, hardware_id, msg):
        license_exp_date = license_id.expiration_date
        validation_exp_date = hardware_id._get_validation_expiration_date()
        min_date = validation_exp_date
        if license_exp_date and license_exp_date < min_date:
            min_date = license_exp_date
        msg["expiration_date"] = {
            "license": fields.Datetime.to_string(license_exp_date),
            "validation": fields.Datetime.to_string(validation_exp_date),
            "min": fields.Datetime.to_string(min_date),
        }

    #######################################################################

    def _get_licenses(self, identifier, hardware, **kwargs):
        # use sudo to bypass access rules, only rely on the domain
        SoftwareLicense = request.env["software.license"].sudo()
        domain = SoftwareLicense._get_license_default_portal_domain(
            request_partner_id=request.env.user.partner_id,
            include_pass_licenses=True,
        )
        if identifier:
            domain += [("application_id.identifier", "=", identifier)]
        license_ids = SoftwareLicense.search(domain)
        res = {}
        for license_id in license_ids:
            license_data = license_id._prepare_export_vals(
                include_activation_identifier=True
            )
            if hardware:
                if hardware == "*":
                    # if a wildcard character is used, then include all
                    # hardwares
                    hw_names = False
                else:
                    # allow multiple hardware identifiers separated with
                    # a `||` sequence
                    hw_names = hardware.split("||")
                license_data["hardwares"] = license_id.get_hardwares_dict(
                    filter_names=hw_names
                )
                if not license_data["hardwares"]:
                    # if no hardwares match our query, then ignore this license
                    continue
            self._append_remaining_activation(license_id, license_data)
            # Warning, the key used there is `serial`, not the
            # `activation_identifier`, don't rely on it
            res[license_id.serial] = license_data
        return res

    @http.route(
        URL_BASE_V1 + URL_VAR_HARDWARE + "/Licenses",
        type="json",
        methods=["POST"],
        auth="user",
        csrf=False,
    )
    def get_all_licenses_per_hardware(self, hardware, **kwargs):
        return self._get_licenses(identifier=False, hardware=hardware)

    @http.route(
        URL_BASE_V1 + URL_VAR_IDENTIFIER + "/Licenses",
        type="json",
        methods=["POST"],
        auth="user",
        csrf=False,
    )
    def get_all_licenses_per_identifier(self, identifier, **kwargs):
        return self._get_licenses(identifier=identifier, hardware=False)

    @http.route(
        URL_BASE_V1 + "/Licenses",
        type="json",
        methods=["POST"],
        auth="user",
        csrf=False,
    )
    def get_all_licenses(self, **kwargs):
        return self._get_licenses(identifier=False, hardware=False)

    @http.route(
        URL_BASE_V1 + "/Infos",
        methods=["GET"],
        auth="none",
        csrf=False,
    )
    def get_request_info(self, **kwargs):
        return self._get_request_info(request)

    @http.route(
        URL_BASE_V1 + URL_VAR_HARDWARE + "/Activate",
        type="json",
        methods=["POST"],
        auth="public",
        csrf=False,
    )
    def activate_multiple(self, hardware, **kwargs):
        res = {}
        if "data" in request.params:
            for identifier, serial in request.params["data"].items():
                msg = self.activate(int(identifier), serial, hardware)
                if serial not in res:
                    res[serial] = {}
                res[serial][identifier] = msg
        return res

    @http.route(
        URL_BASE_V1 + URL_VAR_HARDWARE + "/Validate",
        type="json",
        methods=["POST"],
        auth="public",
        csrf=False,
    )
    def validate_multiple(self, hardware, **kwargs):
        res = {}
        if "data" in request.params:
            for identifier, serial in request.params["data"].items():
                msg = self.validate(int(identifier), serial, hardware)
                if serial not in res:
                    res[serial] = {}
                res[serial][identifier] = msg
        return res

    def _get_hardware_ids(self, hardware, identifier=False, serial=False):
        hardware_ids = (
            request.env["software.license.hardware"]
            .sudo()
            .get_hardware_ids(hardware, identifier, serial)
        )
        return hardware_ids

    @http.route(
        URL_BASE_V1 + URL_VAR_HARDWARE + "/Deactivate",
        type="json",
        methods=["POST"],
        auth="user",
        csrf=False,
    )
    def deactivate_all(self, hardware, **kwargs):
        hardware_ids = self._get_hardware_ids(hardware)
        if not hardware_ids:
            return HARDWARE_NOT_FOUND
        else:
            hardware_ids.unlink()
            res = ALL_SERIALS_DEACTIVATED_ON_HARDWARE
            return res
