# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Nov 2021

from odoo import _, api, fields, models
from odoo.exceptions import UserError

SUPERMANAGER_GROUP = 'mrp_acl.group_project_supermanager'


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    @api.model
    def _get_supermanagers(self):
        group = self.env.ref(SUPERMANAGER_GROUP)
        return group.users

    @api.model
    def _raise_not_supermanager(self, message):
        message += [
            _("You must be a member of the « MRP's Super-Manager » group.")
        ]
        managers = [u.name for u in self._get_supermanagers()]
        if managers:
            message += ['', _("Please contact one of them to do it for you:")]
            for manager in managers:
                message += ['- %s' % (manager, )]
        raise UserError('\n'.join(message))
