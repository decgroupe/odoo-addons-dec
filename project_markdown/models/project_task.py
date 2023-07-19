# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2022

from odoo import fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    description = fields.Html(
        string="HTML Description",
    )
    description_markdown = fields.Text(
        string="Markdown Description",
    )
    description_html_visible = fields.Boolean(
        string="Display HTML Description",
        default=True,
    )
    description_markdown_visible = fields.Boolean(
        string="Display Markdown Description",
        default=False,
    )
