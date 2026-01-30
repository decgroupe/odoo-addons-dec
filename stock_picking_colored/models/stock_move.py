# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2020


from odoo import api, fields, models

from odoo.addons.tools_miscellaneous.tools.material_design_colors import (
    AMBER,
    BLUE,
    BLUEGREY,
    BROWN,
    CYAN,
    DEEPORANGE,
    DEEPPURPLE,
    GREEN,
    GREY,
    INDIGO,
    LIGHTBLUE,
    LIGHTGREEN,
    LIME,
    ORANGE,
    PINK,
    PURPLE,
    RED,
    TEAL,
    YELLOW,
)

INDEX_1 = "50"
INDEX_2 = "100"
INDEX_3 = "200"

LIST_COLORS = [
    RED[INDEX_1],
    LIGHTBLUE[INDEX_1],
    YELLOW[INDEX_1],
    BLUEGREY[INDEX_1],
    PINK[INDEX_1],
    CYAN[INDEX_1],
    AMBER[INDEX_1],
    PURPLE[INDEX_1],
    TEAL[INDEX_1],
    ORANGE[INDEX_1],
    DEEPPURPLE[INDEX_1],
    GREEN[INDEX_1],
    DEEPORANGE[INDEX_1],
    INDIGO[INDEX_1],
    LIGHTGREEN[INDEX_1],
    BROWN[INDEX_1],
    BLUE[INDEX_1],
    LIME[INDEX_1],
    GREY[INDEX_1],
    RED[INDEX_2],
    LIGHTBLUE[INDEX_2],
    YELLOW[INDEX_2],
    BLUEGREY[INDEX_2],
    PINK[INDEX_2],
    CYAN[INDEX_2],
    AMBER[INDEX_2],
    PURPLE[INDEX_2],
    TEAL[INDEX_2],
    ORANGE[INDEX_2],
    DEEPPURPLE[INDEX_2],
    GREEN[INDEX_2],
    DEEPORANGE[INDEX_2],
    INDIGO[INDEX_2],
    LIGHTGREEN[INDEX_2],
    BROWN[INDEX_2],
    BLUE[INDEX_2],
    LIME[INDEX_2],
    GREY[INDEX_2],
    RED[INDEX_3],
    LIGHTBLUE[INDEX_3],
    YELLOW[INDEX_3],
    BLUEGREY[INDEX_3],
    PINK[INDEX_3],
    CYAN[INDEX_3],
    AMBER[INDEX_3],
    PURPLE[INDEX_3],
    TEAL[INDEX_3],
    ORANGE[INDEX_3],
    DEEPPURPLE[INDEX_3],
    GREEN[INDEX_3],
    DEEPORANGE[INDEX_3],
    INDIGO[INDEX_3],
    LIGHTGREEN[INDEX_3],
    BROWN[INDEX_3],
    BLUE[INDEX_3],
    LIME[INDEX_3],
    GREY[INDEX_3],
]


class StockMove(models.Model):
    _inherit = "stock.move"

    list_fg_color = fields.Char(
        string="Foreground Color (List view)",
        compute="_compute_list_colors",
        store=False,
    )
    list_bg_color = fields.Char(
        string="Background Color (List view)",
        compute="_compute_list_colors",
        store=False,
    )

    @api.depends("group_id")
    def _compute_list_colors(self):
        self.list_bg_color = False
        self.list_fg_color = False
        move_group = self._read_group(
            domain=[("id", "in", self.ids)],
            groupby=["group_id"],
            aggregates=["__count"],
        )
        if len(move_group) > 1:
            colors = {}
            for i, group in enumerate(move_group):
                group_id, _count = group
                colors[group_id.id] = LIST_COLORS[i % len(LIST_COLORS)]
            # Apply group colors per record
            for record in self:
                if record.group_id.id in colors:
                    record.list_bg_color = colors[record.group_id.id][0]
                    record.list_fg_color = colors[record.group_id.id][1]
