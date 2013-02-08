# -*- coding: utf-8 -*-

from osv import osv, fields

class taggings_picking(osv.osv):
    _inherit = "tagging.tags"
    _name = _inherit

    _columns = {
        "picking_ids": fields.many2many("stock.picking", "tagging_pickings", "tag_id", "picking_id", string="Pickings"),
        
    }
taggings_picking()


class picking_taggings(osv.osv):
    _inherit = "stock.picking"
    _name = _inherit

    _columns = {
        "tagging_ids": fields.many2many("tagging.tags", "tagging_pickings", "picking_id", "tag_id", string="Tags"),
    }
picking_taggings()
