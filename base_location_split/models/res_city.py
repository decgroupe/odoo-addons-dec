# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2021

from odoo import fields, models, api
from odoo.tools.progressbar import progressbar as pb


class ResCity(models.Model):
    _inherit = "res.city"

    def action_split_by_zip(self):
        for rec in pb(self):
            if len(rec.zip_ids) <= 1:
                continue
            common_prefix = False
            to_split = {}
            for zip_id in rec.zip_ids:
                if len(zip_id.name) >= 2:
                    other_prefix = zip_id.name[:2]
                    if not common_prefix:
                        common_prefix = other_prefix
                    elif other_prefix != common_prefix:
                        if not other_prefix in to_split:
                            to_split[other_prefix] = []
                        to_split[other_prefix].append(zip_id)
            if not to_split:
                continue
            for prefix, zip_ids in to_split.items():
                new_city_id = rec.copy(default={'zip_ids': False})
                for zip_id in zip_ids:
                    zip_id.city_id = new_city_id
