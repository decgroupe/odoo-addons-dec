# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Feb 2022

from odoo import _, api, fields, models, service


# TODO: Use odoo 15+ new class: odoo/odoo/fields.py:Command instead
# according to odoo/fields.py:_RelationalMulti.convert_to_cache
X2M_CREATE =  0
X2M_UPDATE =  1
X2M_DELETE =  2
X2M_UNLINK =  3
X2M_LINK =  4
X2M_CLEAR = 5
X2M_SET = 6

class IrModuleMigration(models.Model):
    _name = "ir.module.migration"
    _description = "Module Migration"

    @api.model
    def _default_version(self):
        res = 0
        if "migration_ids" in self.env.context:
            for x2m_cmd, rec_id, rec_data in self.env.context.get("migration_ids"):
                if x2m_cmd == X2M_DELETE:
                    continue
                # case when item is new/edited
                if isinstance(rec_data, dict):
                    if rec_data.get("version", 0) > res:
                        res = rec_data.get("version")
                # case when item is already in database and has not been edited
                elif isinstance(rec_id, int) and rec_id > 0:
                    migration_id = self.browse(rec_id)
                    if migration_id.version > res:
                        res = migration_id.version
        if res == 0:
            version = service.common.exp_version()
            res = version["server_version_info"][0]
        else:
            res = res + 1
        return res

    module_id = fields.Many2one(
        comodel_name="ir.module.module",
        string="Module",
    )
    version = fields.Integer(
        string="Version",
        default=_default_version,
    )
    repo_address = fields.Char(
        string="Repo.",
        help="Repository address",
    )
    note = fields.Char(
        string="Note",
    )
    state = fields.Selection(
        [
            ("uninstalled", "Not Installed"),
            ("installed", "Installed"),
            ("migrated", "Migrated"),
            ("adopted", "Adopted"),
            ("removed", "🗑️"),
            ("todo", "To-do"),
            ("ready", "---"),
            ("obsolete", "Obsolete"),
        ],
    )
    pr_address = fields.Char(
        string="PR",
        help="Pull-request address",
    )

    @api.model
    def create(self, vals):
        rec = super().create(vals)
        self.env["ir.module.module"]._crud_mig_fields()
        return rec

    def write(self, vals):
        res = super().write(vals)
        self.env["ir.module.module"]._crud_mig_fields()
        return res

    def unlink(self):
        res = super().unlink()
        self.env["ir.module.module"]._crud_mig_fields()
        return res
