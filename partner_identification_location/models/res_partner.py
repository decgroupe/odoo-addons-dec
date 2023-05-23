# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Nov 2021

from odoo import models


class ResPartner(models.Model):
    _inherit = "res.partner"

    def _get_name_location_identification(self):
        res = super()._get_name_location_identification()
        if self.zip_id:
            res = "🗺️ %s" % (self.zip_id.display_name)
        return res
