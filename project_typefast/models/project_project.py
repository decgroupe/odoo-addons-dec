# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Jul 2021

from odoo import models


class Project(models.Model):
    _name = 'project.project'
    _inherit = ['project.project', 'typefast.mixin']
