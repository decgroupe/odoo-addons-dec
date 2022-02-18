# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Feb 2022

from odoo import _, api, models, fields


class IrModuleMigration(models.Model):
    _name = "ir.module.migration"
    _description = "Module Migration"

    module_id = fields.Many2one(
        comodel_name='ir.module.module',
        string='Module',
    )
    version = fields.Integer(string="Version", )
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
