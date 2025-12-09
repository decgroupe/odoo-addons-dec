# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2020

from odoo import fields, models


class RefLog(models.Model):
    """Reference log for all operations"""

    _name = "ref.log"
    _description = "Log"
    _rec_name = "operation"
    _order = "id desc"

    operation = fields.Text(
        string="Operation",
        required=True,
    )
    username = fields.Text(
        string="User",
        required=True,
    )
    localcomputername = fields.Text(
        string="Computer",
        required=True,
    )
    localusername = fields.Text(
        string="Local Username",
        required=True,
    )
    ipaddress = fields.Text(
        string="IP Address",
        required=True,
    )
    datetime = fields.Datetime(
        string="Modification date",
        default=fields.Datetime.now,
    )
