# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jan 2022


from odoo import fields, models, tools


class MailMessageSubtype(models.Model):
    _inherit = "mail.message.subtype"

    excluded_res_model_ids = fields.Many2many(
        comodel_name="ir.model",
        string="Excluded models",
        help="This subtype will not be included as default for models " "in this list.",
        domain="[('transient', '=', False)]",
    )

    def _filter_subtypes(self, model_name, pack_ids):
        res = pack_ids
        if model_name and not self.env.context.get("manual_message_subscribe"):
            domain = [("excluded_res_model_ids.model", "=", model_name)]
            excluded_ids = self.search(domain)
            if excluded_ids.ids:
                filtered_array_ids = []
                for ids in pack_ids:
                    ids = [x for x in ids if x not in excluded_ids.ids]
                    filtered_array_ids.append(ids)
                res = filtered_array_ids
        return res

    @tools.ormcache_context(
        "self.env.uid", "model_name", keys=("manual_message_subscribe",)
    )
    def _get_auto_subscription_subtypes(self, model_name):
        (
            child_ids,
            def_ids,
            all_int_ids,
            parent,
            relation,
        ) = super()._get_auto_subscription_subtypes(model_name)
        # Apply filtering and unpack values (KEEP THE COMMA !!!)
        def_ids,  = self._filter_subtypes(model_name, [def_ids])
        return child_ids, def_ids, all_int_ids, parent, relation

    @tools.ormcache("self.env.uid", "model_name")
    def _default_subtypes(self, model_name):
        subtype_ids, internal_ids, external_ids = super()._default_subtypes(model_name)
        # Apply filtering and unpack values
        subtype_ids, internal_ids, external_ids = self._filter_subtypes(
            model_name, [subtype_ids, internal_ids, external_ids]
        )
        return subtype_ids, internal_ids, external_ids
