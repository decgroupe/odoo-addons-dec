# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Feb 2021

from odoo import models, api, fields


class Project(models.Model):
    _inherit = "project.project"

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        # Make a search with default criteria
        names = super().name_search(
            name=name, args=args, operator=operator, limit=limit
        )
        # Add type to quickly identify a project
        result = []
        for item in names:
            project = self.browse(item[0])[0]
            name = item[1]
            type_id = project.type_id
            if type_id:
                name = '%s / %s' % (type_id.complete_name, project.name)
            result.append((item[0], name))
        return result
