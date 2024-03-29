# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Feb 2022

from odoo import models, api, fields


class ProjectTask(models.Model):
    _name = "project.task"
    _inherit = ['project.task', 'mail.activity.my.mixin']
