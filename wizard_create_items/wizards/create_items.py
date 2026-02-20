# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Nov 2025


from odoo import Command, _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools.mail import is_html_empty

from ..utils import _extract_items_from_html


class CreateItemsWizard(models.TransientModel):
    _name = "create.items.wizard"
    _description = "Create Items from List"
    _model_wizard_line = "create.items.wizard.line"

    content = fields.Html(
        string="List",
        help="Enter content as a table (1st column: identifier, 2nd column: name), "
        "an HTML list (<ul> or <ol> with <li> tags), "
        "as lines starting with '-', or simply as one item per line.",
    )
    content_separator = fields.Char(
        string="Separator",
        trim=False,
        help="The separator between identifier and name in the provided content.",
    )
    line_ids = fields.One2many(
        comodel_name=_model_wizard_line,
        inverse_name="wizard_id",
        string="Items to Generate",
    )

    @api.onchange("content")
    def _onchange_content(self):
        for rec in self:
            rec.action_parse_content()

    @api.onchange("content_separator")
    def _onchange_content_separator(self):
        for rec in self:
            rec.action_parse_content(rec.content_separator)

    def action_parse_content(self, separator=None):
        self.ensure_one()
        self.content_separator = False
        lines = [Command.clear()]
        if not is_html_empty(self.content):
            items, separator = _extract_items_from_html(self.content, separator)
            for _index, item in enumerate(items):
                identifier, name = item
                if not name:
                    name = _("Item %d", _index + 1)
                lines.append(Command.create({"identifier": identifier, "name": name}))
            self.content_separator = separator
        self.line_ids = lines
        return self._reopen()

    def action_create_items(self):
        self.ensure_one()
        if not self.content or is_html_empty(self.content):
            raise UserError(_("Please enter at least one item."))
        if not self.line_ids:
            self.action_parse_content()

        if not self.line_ids:
            raise UserError(
                _(
                    "No data could be parsed from the provided content. "
                    "Please ensure you have entered items as an HTML list, "
                    "lines starting with '-', or one item per line."
                )
            )

        # Inherit this method to create items in your specific model and
        # return an action to display them
        return self._reopen()

    def _reopen(self, enforce_id=False):
        return {
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "res_id": enforce_id or self.id,
            "view_mode": "form",
            "target": "new",
        }


class CreateItemsWizardLine(models.TransientModel):
    _name = "create.items.wizard.line"
    _description = "Create Items Wizard Line"
    _model_wizard = "create.items.wizard"

    wizard_id = fields.Many2one(
        comodel_name=_model_wizard,
        string="Wizard",
        required=True,
        ondelete="cascade",
    )
    identifier = fields.Char(
        string="Identifier",
        help="You can set an identifier for the item before creation.",
    )
    name = fields.Char(
        string="Name",
        required=True,
        help="You can rename the item before creation.",
    )
