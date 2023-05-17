# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Feb 2022

from odoo import _, api, fields, models
from odoo.addons.tools_miscellaneous.tools.material_design_colors import *


class IrModule(models.Model):
    _inherit = "ir.module.module"

    migration_ids = fields.One2many(
        comodel_name="ir.module.migration",
        inverse_name="module_id",
        string="Migrations",
    )

    mig_12_status = fields.Char(
        string="12",
        compute="_compute_mig_x",
    )
    mig_12_color = fields.Char(
        string="Color (12)",
        compute="_compute_mig_x",
    )

    mig_13_status = fields.Char(
        string="13",
        compute="_compute_mig_x",
    )
    mig_13_color = fields.Char(
        string="Color (13)",
        compute="_compute_mig_x",
    )

    mig_14_status = fields.Char(
        string="14",
        compute="_compute_mig_x",
    )
    mig_14_color = fields.Char(
        string="Color (14)",
        compute="_compute_mig_x",
    )

    mig_15_status = fields.Char(
        string="15",
        compute="_compute_mig_x",
    )
    mig_15_color = fields.Char(
        string="Color (15)",
        compute="_compute_mig_x",
    )

    mig_16_status = fields.Char(
        string="16",
        compute="_compute_mig_x",
    )
    mig_16_color = fields.Char(
        string="Color (16)",
        compute="_compute_mig_x",
    )

    mig_17_status = fields.Char(
        string="17",
        compute="_compute_mig_x",
    )
    mig_17_color = fields.Char(
        string="Color (17)",
        compute="_compute_mig_x",
    )

    mig_18_status = fields.Char(
        string="18",
        compute="_compute_mig_x",
    )
    mig_18_color = fields.Char(
        string="Color (18)",
        compute="_compute_mig_x",
    )

    @api.depends("migration_ids", "migration_ids.state", "migration_ids.pr_address")
    def _compute_mig_x(self):
        self.mig_12_status = False
        self.mig_12_color = False
        self.mig_13_status = False
        self.mig_13_color = False
        self.mig_14_status = False
        self.mig_14_color = False
        self.mig_15_status = False
        self.mig_15_color = False
        self.mig_16_status = False
        self.mig_16_color = False
        self.mig_17_status = False
        self.mig_17_color = False
        self.mig_18_status = False
        self.mig_18_color = False
        for rec in self:
            for migration_id in rec.migration_ids:
                status_field = "mig_%d_status" % (migration_id.version)
                color_field = "mig_%d_color" % (migration_id.version)
                if status_field in rec._fields and color_field in rec._fields:
                    if migration_id.pr_address:
                        rec[status_field] = migration_id.pr_address
                        rec[color_field] = ORANGE["500"][0]
                    else:
                        state = dict(
                            migration_id._fields["state"]._description_selection(
                                self.env
                            )
                        ).get(migration_id.state)
                        rec[status_field] = state
                        if migration_id.state == "todo":
                            rec[color_field] = YELLOW["A400"][0]
                        elif migration_id.state == "adopted":
                            rec[color_field] = TEAL["A400"][0]
                        else:
                            rec[color_field] = LIGHTGREEN["500"][0]

    def action_init_migration_status(self):
        for rec in self:
            if rec.state == "installed" and not rec.migration_ids.ids:
                self.env["ir.module.migration"].create(
                    {
                        "module_id": rec.id,
                        "version": 12,
                        "state": "installed",
                    }
                )
