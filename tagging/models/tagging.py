# Copyright (C) DEC SARL, Inc - All Rights Reserved.
#
# CONFIDENTIAL NOTICE: Unauthorized copying and/or use of this file,
# via any medium is strictly prohibited.
# All information contained herein is, and remains the property of
# DEC SARL and its suppliers, if any.
# The intellectual and technical concepts contained herein are
# proprietary to DEC SARL and its suppliers and may be covered by
# French Law and Foreign Patents, patents in process, and are
# protected by trade secret or copyright law.
# Dissemination of this information or reproduction of this material
# is strictly forbidden unless prior written permission is obtained
# from DEC SARL.
# Written by Yann Papouin <y.papouin@dec-industrie.com>, Mar 2020

from odoo import api, fields, models, _
import string


class TaggingTag(models.Model):
    _name = "tagging.tags"
    _order = 'name'

    name = fields.Char("Tag", size=64, required=True)
    color = fields.Integer()
    description = fields.Char("Short Description", size=256)
    notes = fields.Text()
    active = fields.Boolean( default=True)
    related_tags_ids = fields.Many2many(
        "tagging.tags",
        "tagging_related_tags",
        "tag_id",
        "related_tag_id",
        string="Related Tags",
    )

    _sql_constraints = [
        (
            'tagging_tags_name_unique', 'unique (name)',
            _('The tag names must be unique!')
        ),
    ]

    def strip_accent(self, txt):
        accents = {
            'a': ['à', 'ã', 'á', 'â', 'ä'],
            'c': ['ç'],
            'e': ['é', 'è', 'ê', 'ë'],
            'i': ['ì', 'í', 'î', 'ï'],
            'n': ['ñ'],
            'u': ['ù', 'ú', 'ü', 'û'],
            'y': ['ý', 'ÿ'],
            'o': ['ô', 'ö', 'ò', 'ó', 'õ']
        }
        for (char, accented_chars) in accents.items():
            for accented_char in accented_chars:
                txt = txt.replace(accented_char, char)
        return txt

    @api.model
    def on_change_tag_name(self, tag_name):
        if tag_name:
            v = {}

            tag_name = tag_name.strip()
            tag_name = self.strip_accent(tag_name.lower())
            tag_name = tag_name.replace(' ', '-')

            char_previous = ''
            char_index = 0
            for char_current in tag_name:
                char_index = char_index + 1
                if char_current == '-' and char_previous == '-':
                    tag_name = tag_name[:char_index - 1] + tag_name[char_index:]
                    char_index = char_index - 1

                char_previous = char_current

            safe_chars = string.ascii_letters + string.digits + '-'
            tag_name = ''.join(
                [char if char in safe_chars else '' for char in tag_name]
            )

            v['name'] = tag_name
            return {'value': v}
        else:
            return False
