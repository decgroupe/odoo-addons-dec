# -*- coding: utf-8 -*-

from osv import osv, fields

class taggings_mrporder(osv.osv):
    _inherit = "tagging.tags"
    _name = _inherit

    _columns = {
        "mrp_order_ids": fields.many2many("mrp.production", "tagging_mrp", "tag_id", "production_id", string="Production"),
        
    }
taggings_mrporder()


class mrporder_taggings(osv.osv):
    _inherit = "mrp.production"
    _name = _inherit

    _columns = {
        "tagging_ids": fields.many2many("tagging.tags", "tagging_mrp", "production_id", "tag_id", string="Tags"),
        
    }
mrporder_taggings()
