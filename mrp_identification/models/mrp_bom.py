# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jul 2021

from odoo import api, models


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    @api.depends("name", "product_tmpl_id")
    def name_get(self):
        """Custom naming to remove bom name / product name duplication"""
        super_res = super().name_get()
        res = []
        for item in super_res:
            rec = self.browse(item[0])[0]
            if rec.code:
                if rec.product_tmpl_id.default_code in rec.code:
                    name = "[%s] %s" % (rec.code, rec.product_tmpl_id.name)
                else:
                    name = "[%s] %s" % (rec.code, rec.product_tmpl_id.display_name)
            else:
                name = item[1]
            res.append((rec.id, name))
        return res or super_res
