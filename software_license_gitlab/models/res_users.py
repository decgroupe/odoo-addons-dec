# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2021

import logging

from odoo import api, models, fields

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = 'res.users'

    user_gitlab_resource_id = fields.Many2one(
        related='partner_id.user_gitlab_resource_id',
        string='GitLab User',
        inherited=True,
        readonly=False,
    )

    @api.multi
    def _get_gitlab_project_uids(self):
        self.ensure_one()
        SoftwareLicense = self.env['software.license']
        # Search all applications currently owned by this partner
        domain = SoftwareLicense._get_license_default_portal_domain(
            request_partner_id=self.partner_id,
            include_pass_licenses=True,
        )
        application_ids = SoftwareLicense.search(domain).\
            mapped('application_id')
        # Keep only GitLab resources
        return application_ids._get_gitlab_project_uids()

    def _get_joined_gitlab_projects(self):
        self.ensure_one()
        GitLab = self.env['gitlab.service']
        # Prefetch a list of projects where this user is already a member
        # for optimization
        memberships = GitLab.get_user_memberships(
            self.user_gitlab_resource_id.uid
        )
        project_uids = [
            resource['source_id']
            for resource in memberships if resource['source_type'] == 'Project'
        ]
        return project_uids

    def _set_access_to_gitlab_projects(self, project_uids=False):
        self.ensure_one()
        GitLab = self.env['gitlab.service']
        if not project_uids:
            project_uids = self._get_gitlab_project_uids()
        _logger.info(
            "Give an access to GitLab projects %s for %s",
            project_uids,
            self.name,
        )
        joined_project_uids = self._get_joined_gitlab_projects()
        # Give a 'guest' access to all linked documentation projects
        for project_uid in project_uids:
            if project_uid not in joined_project_uids:
                GitLab.add_project_member(
                    project_uid,
                    self.user_gitlab_resource_id.uid,
                )

    def _remove_access_to_gitlab_projects(self, project_uids=False):
        self.ensure_one()
        GitLab = self.env['gitlab.service']
        if not project_uids:
            project_uids = self._get_gitlab_project_uids()
        _logger.info(
            "Remove all access to GitLab projects %s for %s",
            project_uids,
            self.name,
        )
        joined_project_uids = self._get_joined_gitlab_projects()
        # Remove existing access
        for project_uid in project_uids:
            if project_uid in joined_project_uids:
                GitLab.remove_project_member(
                    project_uid,
                    self.user_gitlab_resource_id.uid,
                )

    def _create_or_update_gitlab_user(self, password=False):
        user_uid = super()._create_or_update_gitlab_user(password)
        if user_uid:
            self._set_access_to_gitlab_projects()

    @api.multi
    def write(self, vals):
        res = super().write(vals)
        if 'password' in vals:
            self._create_or_update_gitlab_user(vals.get('password'))
        return res
