# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jun 2021

from odoo import api, fields, models, _
from odoo.tools.safe_eval import safe_eval


class MrpProduction(models.Model):
    _name = 'mrp.production'
    _inherit = ['mrp.production', 'mail.alias.mixin']

    alias_id = fields.Many2one(
        comodel_name='mail.alias',
        string='Alias',
        ondelete="restrict",
        required=True,
        help="Internal email associated with this production order. "
        "Incoming emails are automatically added as chat message."
    )

    def _alias_get_creation_values(self):
        values = super()._alias_get_creation_values()
        values["alias_model_id"] = self.env.ref("mrp.model_mrp_production").id
        if self.id:
            values["alias_defaults"] = defaults = safe_eval(
                self.alias_defaults or "{}"
            )
            defaults["parent_id"] = self.id
        return values

    def autocreate_mail_alias(self):
        for rec in self:
            if not rec.alias_name:
                rec.alias_name = rec.name

    def _clean_alias_name(self, alias_name):
        return alias_name.replace('/', "")

    @api.model
    def create(self, vals):
        production = super(MrpProduction, self).create(vals)
        if not production.alias_name:
            production.alias_name = production.name
        return production

    def write(self, vals):
        if vals.get('alias_name'):
            vals['alias_name'] = self._clean_alias_name(vals['alias_name'])
        res = super().write(vals)
        if vals.get('alias_name'):
            for rec in self:
                if rec.alias_id:
                    # Force thead_id since we don't wont to create a new
                    # production order, we just want add incoming message
                    # to the chatter
                    rec.alias_force_thread_id = rec.id
                else:
                    rec.alias_force_thread_id = 0
        return res
