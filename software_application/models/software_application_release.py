# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2021

import semver

from odoo import _, api, fields, models


class SoftwareApplicationRelease(models.Model):
    _name = "software.application.release"
    _description = "License Application Release"
    _order = "version_major desc, version_minor desc, version_patch desc"
    _rec_name = "version"

    application_id = fields.Many2one(
        comodel_name="software.application",
        string="Application",
        required=True,
    )
    version = fields.Char(
        string="Version",
        default=lambda self: self._get_default_version(),
        required=True,
        help="Version numbering using semver https://semver.org.\n"
        "A normal version number MUST take the form X.Y.Z where X, Y, and Z "
        "are non-negative integers, and MUST NOT contain leading zeroes.\n"
        "X is the major version, Y is the minor version, and Z is the patch "
        "version.\n"
        "Each element MUST increase numerically. For instance: 1.9.0 -> "
        "1.10.0 -> 1.11.0.\n"
        "Once a versioned package has been released, the contents of that "
        "version MUST NOT be modified.\n"
        "Any modifications MUST be released as a new version.",
    )
    version_major = fields.Integer(
        string="Major",
        compute="_compute_version_number_metadata",
        inverse="_inverse_version_number_metadata",
        readonly=False,
        store=True,
        required=False,
        help="Major version X (X.y.z | X > 0) MUST be incremented if any "
        "backwards incompatible changes are introduced to the public API.\n"
        "It MAY also include minor and patch level changes.\n"
        "Patch and minor versions MUST be reset to 0 when major version is "
        "incremented.",
    )
    version_minor = fields.Integer(
        string="Minor",
        compute="_compute_version_number_metadata",
        inverse="_inverse_version_number_metadata",
        readonly=False,
        store=True,
        required=False,
        help="Minor version Y (x.Y.z | x > 0) MUST be incremented if new, "
        "backwards compatible functionality is introduced to the public API.\n"
        "It MUST be incremented if any public API functionality is marked as "
        "deprecated.\n"
        "It MAY be incremented if substantial new functionality "
        "or improvements are introduced within the private code.\n"
        "It MAY include patch level changes.\n"
        "Patch version MUST be reset to 0 when minor version is incremented.",
    )
    version_patch = fields.Integer(
        string="Patch",
        compute="_compute_version_number_metadata",
        inverse="_inverse_version_number_metadata",
        readonly=False,
        store=True,
        required=False,
        help="Patch version Z (x.y.Z | x > 0) MUST be incremented if only "
        "backwards compatible bug fixes are introduced.\n"
        "A bug fix is defined as an internal change that fixes incorrect "
        "behavior.",
    )
    version_prerelease = fields.Char(
        string="Pre-release",
        compute="_compute_version_number_metadata",
        inverse="_inverse_version_number_metadata",
        readonly=False,
        store=True,
        help="A pre-release version MAY be denoted by appending a hyphen and "
        "a series of dot separated identifiers immediately following the "
        "patch version.\n"
        "Identifiers MUST comprise only ASCII alphanumerics and hyphens "
        "[0-9A-Za-z-].\n"
        "Identifiers MUST NOT be empty.\n"
        "Numeric identifiers MUST NOT include leading zeroes.\n"
        "Pre-release versions have a lower precedence than the associated "
        "normal version.\n"
        "A pre-release version indicates that the version "
        "is unstable and might not satisfy the intended compatibility "
        "requirements as denoted by its associated normal version.\n"
        "Examples: 1.0.0-alpha, 1.0.0-alpha.1, 1.0.0-0.3.7, 1.0.0-x.7.z.92, "
        "1.0.0-x-y-z.–.",
    )
    version_build = fields.Char(
        string="Build",
        compute="_compute_version_number_metadata",
        inverse="_inverse_version_number_metadata",
        readonly=False,
        store=True,
        help="Build metadata MAY be denoted by appending a plus sign and a "
        "series of dot separated identifiers immediately following the patch "
        "or pre-release version.\n"
        "Identifiers MUST comprise only ASCII alphanumerics and hyphens "
        "[0-9A-Za-z-].\n"
        "Identifiers MUST NOT be empty.\n"
        "Build metadata MUST be ignored when determining version "
        "precedence.\n"
        "Thus two versions that differ only in the build "
        "metadata, have the same precedence.\n"
        "Examples: 1.0.0-alpha+001, 1.0.0+20130313144700, "
        "1.0.0-beta+exp.sha.5114f85, 1.0.0+21AF26D3—-117B344092BD.",
    )
    date = fields.Date(
        string="Date",
        help="Release's Date",
        required=True,
        default=lambda self: self._get_default_date(),
    )
    content = fields.Html(
        string="Release Notes",
        translate=False,
        sanitize=False,
        default=lambda self: self._get_default_content(),
    )
    url = fields.Char(
        string="Download URL",
        default=lambda self: self._get_default_url(),
    )

    _sql_constraints = [
        (
            "app_version_uniq",
            "unique (application_id,version)",
            "The release version must be unique per application !",
        ),
        (
            "app_url_uniq",
            "unique (application_id,url)",
            "The release url must be unique per application !",
        ),
    ]

    @api.depends("version")
    def _compute_version_number_metadata(self):
        for rec in self:
            ver = semver.VersionInfo.parse(rec.version)
            rec.version_major = ver.major
            rec.version_minor = ver.minor
            rec.version_patch = ver.patch
            rec.version_prerelease = ver.prerelease
            rec.version_build = ver.build

    @api.depends(
        "version_major",
        "version_minor",
        "version_patch",
        "version_prerelease",
        "version_build",
    )
    def _inverse_version_number_metadata(self):
        self._recompute_version_from_number_metadata()

    @api.onchange(
        "version_major",
        "version_minor",
        "version_patch",
        "version_prerelease",
        "version_build",
    )
    def _onchange_version_number_metadata(self):
        self._recompute_version_from_number_metadata()

    def _recompute_version_from_number_metadata(self):
        for rec in self:
            ver = semver.VersionInfo(
                rec.version_major,
                rec.version_minor,
                rec.version_patch,
                rec.version_prerelease or "",
                rec.version_build or "",
            )
            rec.version = str(ver)

    @api.model
    def _get_default_version(self):
        res = "1.0.0"
        if "release_ids" in self.env.context:
            sem_ver = False
            for o2m in self.env.context.get("release_ids"):
                version = False
                if isinstance(o2m[1], int):
                    rec_id = o2m[1]
                    version = self.browse(rec_id).version
                elif isinstance(o2m[1], str) and isinstance(o2m[2], dict):
                    rec_data = o2m[2]
                    version = rec_data.get("version", False)
                if version:
                    cur_sem_ver = semver.VersionInfo.parse(version)
                    if not sem_ver or cur_sem_ver > sem_ver:
                        sem_ver = cur_sem_ver
            if sem_ver:
                res = str(sem_ver.bump_major())
        return res

    @api.model
    def _get_default_date(self):
        return fields.Date.context_today(self)

    def _get_default_content_items(self, name="item", count=1):
        items = []
        for i in range(count):
            items.append("<li><p>%s %d</p></li>" % (name, i + 1))
        return "<ul>%s</ul>" % "".join(items)

    @api.model
    def _get_default_content(self):
        default_titles = [
            (_("What's New"), _("new")),
            (_("Fixes"), _("fix")),
            (_("Known Issues"), _("issue")),
        ]
        content = []
        for title, item_name in default_titles:
            content.append(
                "<h2>%s</h2>%s"
                % (
                    title,
                    self._get_default_content_items(item_name, 3),
                )
            )
        return "".join(content)

    @api.model
    def _get_default_url(self):
        return ""
