# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Nov 2021

from odoo import api, models


class AccountAccountTag(models.Model):
    _inherit = 'account.account.tag'

    @api.depends('name')
    def name_get(self):
        """
        """
        super_res = super().name_get()
        res = []
        if self.user_has_groups('base.group_no_one'):
            ModelData = self.env["ir.model.data"]
            for item in super_res:
                rec = self.browse(item[0])[0]
                xml_module, xml_name = ModelData.get_xmlid(rec)
                if xml_name:
                    name = "%s [%s]" % (item[1], xml_name)
                else:
                    name = item[1]
                res.append((rec.id, name))
        return res or super_res
