# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Feb 2022

import logging
from odoo import _, api, fields, models
from odoo.addons.tools_miscellaneous.tools.material_design_colors import *


MIG_FIELD_PREFIX = "x_mig_"
MIG_VIEW_PREFIX = "ir.module.module.tree@base_module_migration_tracking#x_mig_"


_logger = logging.getLogger(__name__)


class IrModule(models.Model):
    _inherit = "ir.module.module"

    migration_ids = fields.One2many(
        comodel_name="ir.module.migration",
        inverse_name="module_id",
        string="Migrations",
    )

    @api.depends("migration_ids", "migration_ids.state", "migration_ids.pr_address")
    def _compute_mig_x(self):
        # set default value for all records
        for field in [f for f in self._fields if f.startswith(MIG_FIELD_PREFIX)]:
            self[field] = False
        for rec in self:
            for migration_id in rec.migration_ids:
                status = self._get_mig_status_field_name(migration_id.version)
                color = self._get_mig_color_field_name(migration_id.version)
                if status in rec._fields and color in rec._fields:
                    if migration_id.pr_address:
                        rec[status] = migration_id.pr_address
                        rec[color] = ORANGE["500"][0]
                    else:
                        state = dict(
                            migration_id._fields["state"]._description_selection(
                                self.env
                            )
                        ).get(migration_id.state)
                        rec[status] = state or "?"
                        if not migration_id.state:
                            rec[color] = INDIGO["100"][0]
                        elif migration_id.state == "todo":
                            rec[color] = YELLOW["A400"][0]
                        elif migration_id.state == "adopted":
                            rec[color] = TEAL["A400"][0]
                        elif migration_id.state == "uninstalled":
                            rec[color] = RED["100"][0]
                        else:
                            rec[color] = LIGHTGREEN["500"][0]

    def action_init_migration_status(self):
        for rec in self:
            if not rec.migration_ids.ids:
                if rec.state in ("installed", "uninstalled"):
                    self.env["ir.module.migration"].create(
                        {
                            "module_id": rec.id,
                            "state": rec.state,
                        }
                    )

    def _crud_mig_fields(self):
        """CREATE/UPDATE/DELETE migration fields and views"""
        res = self.env["ir.module.migration"].read_group([], ["version"], ["version"])
        versions = [r["version"] for r in res]
        valid_fields = []
        valid_views = []
        for version in versions:
            status_field = self._create_mig_status_field(version)
            if status_field:
                valid_fields.append(status_field.name)
            color_field = self._create_mig_color_field(version)
            if color_field:
                valid_fields.append(color_field.name)
            view = self._create_mig_view(version)
            if view:
                valid_views.append(view.name)
        # detect and delete invalid views
        views = self.env["ir.ui.view"].search(
            [
                ("name", "=like", MIG_VIEW_PREFIX + "%"),
                ("name", "not in", valid_views),
            ]
        )
        if views:
            _logger.debug("Removing views %s", views)
            views.unlink()
        # detect and delete invalid fields
        fields = self.env["ir.model.fields"].search(
            [
                ("name", "=like", MIG_FIELD_PREFIX + "%"),
                ("name", "not in", valid_fields),
            ]
        )
        if fields:
            _logger.debug("Removing fields %s", fields)
            fields.unlink()

    def _create_mig_status_field(self, version):
        status_field = False
        name = self._get_mig_status_field_name(version)
        if name not in self._fields:
            status_field = self.create_computed_field(
                name=name,
                description=self._get_mig_status_field_description(version),
                compute="self._compute_mig_x()",
            )
        else:
            status_field = self.env["ir.model.fields"]._get(self._name, name)
        return status_field

    def _create_mig_color_field(self, version):
        color_field = False
        name = self._get_mig_color_field_name(version)
        if name not in self._fields:
            color_field = self.create_computed_field(
                name=name,
                description=self._get_mig_color_field_description(version),
                compute="self._compute_mig_x()",
            )
        else:
            color_field = self.env["ir.model.fields"]._get(self._name, name)
        return color_field

    def create_computed_field(self, name, description, compute, field_type="char"):
        """create a custom field and return it"""
        model = self.env["ir.model"].search([("model", "=", self._name)])
        data = {
            "model_id": model.id,
            "name": name,
            "field_description": description,
            "ttype": field_type,
            "compute": compute,
            "store": False,
            "readonly": True,
        }
        _logger.debug("Creating field %s", data)
        field = self.env["ir.model.fields"].create(data)
        return field

    def _create_mig_view(self, version):
        """create a view with the given field name"""
        name = self._get_mig_view_name(version)
        view_id = self.env["ir.ui.view"].search([("name", "=", name)], limit=1)
        if not self.env["ir.ui.view"].search([("name", "=", name)]):
            data = {
                "name": self._get_mig_view_name(version),
                "model": self._name,
                "type": "tree",
                "inherit_id": self.env.ref("base.module_tree").id,
                "priority": 1000 - version,
                "arch": """
                        <xpath expr="//tree/field[@name='name']" position="after">
                            <field
                                name="%(status_field_name)s"
                                options='{"bg_color": "%(color_field_name)s"}'
                                class="d_mig_status"
                                optional="show"
                            />
                            <field name="%(color_field_name)s" invisible="1" />
                        </xpath>
                    """
                % {
                    "status_field_name": self._get_mig_status_field_name(version),
                    "color_field_name": self._get_mig_color_field_name(version),
                },
            }
            _logger.debug("Creating view %s", data)
            view_id = self.env["ir.ui.view"].create(data)
        return view_id

    @api.model
    def _get_mig_view_name(self, version):
        return "%s%d_view" % (MIG_VIEW_PREFIX, version)

    @api.model
    def _get_mig_status_field_name(self, version):
        return "%s%d_status" % (MIG_FIELD_PREFIX, version)

    @api.model
    def _get_mig_color_field_name(self, version):
        return "%s%d_color" % (MIG_FIELD_PREFIX, version)

    @api.model
    def _get_mig_status_field_description(self, version):
        return "%d" % (version)

    @api.model
    def _get_mig_color_field_description(self, version):
        return "%d (color)" % (version)
