# Copyright (C) DEC SARL, Inc - All Rights Reserved.

import string

from odoo import _, api, fields, models


class TaggingTag(models.Model):
    _name = "tagging.tags"
    _description = "Tag"
    _order = "name"

    name = fields.Char(string="Tag", size=64, required=True)
    color = fields.Integer()
    description = fields.Char(string="Short Description", size=256)
    notes = fields.Text()
    active = fields.Boolean(default=True)
    related_tags_ids = fields.Many2many(
        comodel_name="tagging.tags",
        relation="tagging_related_tags",
        column1="tag_id",
        column2="related_tag_id",
        string="Related Tags",
    )

    _sql_constraints = [
        (
            "tagging_tags_name_unique",
            "unique (name)",
            _("The tag names must be unique!"),
        ),
    ]

    def strip_accent(self, txt):
        accents = {
            "a": ["à", "ã", "á", "â", "ä"],
            "c": ["ç"],
            "e": ["é", "è", "ê", "ë"],
            "i": ["ì", "í", "î", "ï"],
            "n": ["ñ"],
            "u": ["ù", "ú", "ü", "û"],
            "y": ["ý", "ÿ"],
            "o": ["ô", "ö", "ò", "ó", "õ"],
        }
        for char, accented_chars in accents.items():
            for accented_char in accented_chars:
                txt = txt.replace(accented_char, char)
        return txt

    @api.onchange("name")
    def _on_change_tag_name(self):
        tag_name = self.name.strip() if self.name else False
        if tag_name:
            tag_name = self.strip_accent(tag_name.lower())
            tag_name = tag_name.replace(" ", "-")

            char_previous = ""
            char_index = 0
            for char_current in tag_name:
                char_index = char_index + 1
                if char_current == "-" and char_previous == "-":
                    tag_name = tag_name[: char_index - 1] + tag_name[char_index:]
                    char_index = char_index - 1

                char_previous = char_current

            safe_chars = string.ascii_letters + string.digits + "-"
            tag_name = "".join(
                [char if char in safe_chars else "" for char in tag_name]
            )
            self.name = tag_name
