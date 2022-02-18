# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Feb 2022

from odoo import _, api, models, fields


class IrModuleMigration(models.Model):
    _name = "ir.module.migration"
    _description = "Module Migration"

    @api.model
    def _default_version(self):
        res = 0
        if 'migration_ids' in self.env.context:
            for o2m in self.env.context.get('migration_ids'):
                if isinstance(o2m[1], int):
                    rec_id = o2m[1]
                    migration_id = self.browse(rec_id)
                    if migration_id.version > res:
                        res = migration_id.version
                elif isinstance(o2m[1], str) and isinstance(o2m[2], dict):
                    rec_data = o2m[2]
                    if rec_data.get('version', 0) > res:
                        res = rec_data.get('version')
        if res == 0:
            res = 12
        else:
            res = res + 1
        return res

    module_id = fields.Many2one(
        comodel_name='ir.module.module',
        string='Module',
    )
    version = fields.Integer(
        string="Version",
        default=_default_version,
    )
    repo_address = fields.Char(
        string="Repo.",
        help="Repository address",
    )
    note = fields.Char(string="Note", )
    state = fields.Selection(
        [
            ('installed', 'Installed'),
            ('migrated', 'Migrated'),
            ('removed', '🗑️'),
            ('todo', 'To-do'),
            ('ready', '---'),
            ('obsolete', 'Obsolete'),
        ],
    )
    pr_address = fields.Char(
        string="PR",
        help="Pull-request address",
    )
