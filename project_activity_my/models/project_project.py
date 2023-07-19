# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2022

from odoo import models


class ProjectProject(models.Model):
    _name = "project.project"
    _inherit = ["project.project", "mail.activity.my.mixin"]
