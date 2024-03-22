# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2024

import logging
import pprint

from odoo import api, models

_logger = logging.getLogger(__name__)


class IrQWeb(models.AbstractModel):
    _inherit = "ir.qweb"

    @api.model
    def _render(self, id_or_xml_id, values=None, **options):
        _logger.info(
            "Rendering QWeb %s with: %s", id_or_xml_id, pprint.pformat(values)
        )
        res = super(IrQWeb, self)._render(id_or_xml_id, values=values, **options)
        return res

    def default_values(self):
        """attributes add to the values for each computed template"""
        default = super(IrQWeb, self).default_values()
        # default.update(request=request, cache_assets=round(time()/180), true=True, false=False) # true and false added for backward compatibility to remove after v10
        return default
