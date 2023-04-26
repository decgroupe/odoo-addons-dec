# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jul 2021

from odoo import _, api, models
from odoo.exceptions import AccessError

SUPERMANAGER_GROUP = "project_acl.group_project_supermanager"


class Project(models.Model):
    _inherit = "project.project"

    @api.model
    def create(self, vals):
        if self.env.context.get("bypass_supermanager_check") or self.user_has_groups(
            SUPERMANAGER_GROUP
        ):
            pass
        else:
            self._raise_not_supermanager()
        project = super(Project, self).create(vals)
        return project

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
                message += ["- %s" % (manager,)]
        raise AccessError("\n".join(message))
