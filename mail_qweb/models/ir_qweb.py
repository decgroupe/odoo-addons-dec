# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2024

import logging
import pprint

from odoo import api, models

_logger = logging.getLogger(__name__)


class IrQWeb(models.AbstractModel):
    _inherit = "ir.qweb"

    def _get_view_name(self, id_or_xml_id):
        view_name = id_or_xml_id
        if type(view_name) is int:
            view_xmlid = (
                self.env["ir.model.data"]
                .sudo()
                .search(
                    [
                        ("res_id", "=", id_or_xml_id),
                        ("model", "=", "ir.ui.view"),
                    ]
                )
            )
            view_name = f"{view_xmlid.module}.{view_xmlid.name} ({id_or_xml_id})"
        return view_name

    @api.model
    def _render(self, id_or_xml_id, values=None, **options):
        view_name = self._get_view_name(id_or_xml_id)
        if values and "env" not in values:
            values["env"] = self.env
        _logger.debug("Rendering QWeb %s with: %s", view_name, pprint.pformat(values))
        res = super()._render(id_or_xml_id, values=values, **options)
        return res
