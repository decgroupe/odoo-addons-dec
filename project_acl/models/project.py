# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jul 2021

from odoo import _, api, models
from odoo.exceptions import AccessError
from odoo.tools import str2bool

SUPERMANAGER_GROUP = "project_acl.group_project_supermanager"


class Project(models.Model):
    _inherit = "project.project"

    @api.model_create_multi
    def create(self, vals_list):
        if (
            not self._get_supermanager_check_enabled()
            or self.env.context.get("bypass_supermanager_check")
            or self.env.user.has_groups(SUPERMANAGER_GROUP)
            or self.env.is_superuser()
        ):
            pass
        else:
            self._raise_not_supermanager()
        project_ids = super().create(vals_list)
        return project_ids

    @api.model
    def _get_supermanager_check_enabled(self):
        ICP = self.env["ir.config_parameter"].sudo()
        enabled = str2bool(
            ICP.get_param("project_acl.supermanager_check_enabled", default=False)
        )
        return enabled

    @api.model
    def _get_supermanagers(self):
        group = self.env.ref(SUPERMANAGER_GROUP)
        return group.users

    @api.model
    def _raise_not_supermanager(self):
        message = [_("You are not allowed to create a new project!")]
        message += [_("You must be a member of the « Project's Super-Manager » group.")]
        managers = [u.name for u in self._get_supermanagers()]
        if managers:
            message += ["", _("Please contact one of them to do it for you:")]
            for manager in managers:
                message += [f"- {manager}"]
        raise AccessError("\n".join(message))
