# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2023

from collections import defaultdict

from odoo import fields, models


class IrModelData(models.Model):
    _inherit = "ir.model.data"

    def res_id_to_xmlid(self, model, res_ids):
        xml_ids = defaultdict(list)
        model_datas = defaultdict(list)
        domain = [("model", "=", model), ("res_id", "in", res_ids)]
        for data in self.search_read(domain, ["module", "name", "res_id"]):
            xml_ids[data["res_id"]].append("%s.%s" % (data["module"], data["name"]))
            model_datas[data["res_id"]].append(data["id"])
        return xml_ids, model_datas
