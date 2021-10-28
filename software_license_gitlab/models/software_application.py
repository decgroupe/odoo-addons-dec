# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2021

from odoo import api, fields, models


class SoftwareApplication(models.Model):
    _inherit = 'software.application'

    documentation_gitlab_resource_id = fields.Many2one(
        comodel_name='gitlab.resource',
        domain=[('type', '=', 'project')],
        string='Documentation',
        help="Userguide GitLab Pages mapped to this application",
        ondelete='restrict'
    )

    @api.multi
    def _get_gitlab_project_uids(self):
        return self.\
            mapped('documentation_gitlab_resource_id').\
            mapped('uid')

    @api.model
    def _get_all_partners_with_gitlab_access(self):
        domain = [('user_gitlab_resource_id', '!=', False)]
        partner_ids = self.env['res.partner'].search(domain)
        return partner_ids

    @api.multi
    def _remove_access_to_gitlab_projects(self, project_uids=False):
        # TODO: Optimize by getting a list of all members for each project
        if not project_uids:
            project_uids = self._get_gitlab_project_uids()
        partner_ids = self._get_all_partners_with_gitlab_access()
        for partner_id in partner_ids:
            for user_id in partner_id.user_ids:
                user_id._remove_access_to_gitlab_projects(project_uids)

    @api.multi
    def _set_access_to_gitlab_projects(self):
        """ [summary]
            - Find all partners that already have a gitlab access
        """
        SoftwareLicense = self.env['software.license']
        partner_ids = self._get_all_partners_with_gitlab_access()
        for partner_id in partner_ids:
            # Search all existing licenses
            domain = SoftwareLicense._get_default_portal_domain(partner_id)
            domain.append(('application_id', 'in', self.ids))
            application_ids = SoftwareLicense.search(domain).\
                mapped('application_id')
            project_uids = application_ids._get_gitlab_project_uids()
            # If this partner owns these applications then give it an access
            if len(project_uids) > 0:
                for user_id in partner_id.user_ids:
                    user_id._set_access_to_gitlab_projects(project_uids)

    @api.multi
    def write(self, vals):
        if 'documentation_gitlab_resource_id' in vals:
            if not vals.get('documentation_gitlab_resource_id'):
                project_uids = self._get_gitlab_project_uids()

        res = super().write(vals)
        if 'documentation_gitlab_resource_id' in vals:
            if vals.get('documentation_gitlab_resource_id'):
                self._set_access_to_gitlab_projects()
            else:
                self._remove_access_to_gitlab_projects(project_uids)
        return res
