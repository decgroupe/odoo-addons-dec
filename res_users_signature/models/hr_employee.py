# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2021

from odoo import fields, models, api


class Employee(models.Model):
    _inherit = "hr.employee"

    other_websites = fields.Text(
        'Other Websites',
        help="Use one line per website",
    )
    other_work_emails = fields.Text(
        'Other Work Emails',
        help="Use one line per e-mail",
    )
    work_phone_extension = fields.Char(
        string="Phone Extension",
        help="Work Phone Extension",
    )
