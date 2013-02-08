# -*- coding: utf-8 -*-

from osv import osv, fields

class taggings_purchaseorder(osv.osv):
    _inherit = "tagging.tags"
    _name = _inherit

    _columns = {
        "purchase_order_ids": fields.many2many("purchase.order", "tagging_purchaseorder", "tag_id", "purchaseorder_id", string="Purchase Orders"),
        
    }
taggings_purchaseorder()


class purchaseorder_taggings(osv.osv):
    _inherit = "purchase.order"
    _name = _inherit

    _columns = {
        "tagging_ids": fields.many2many("tagging.tags", "tagging_purchaseorder", "purchaseorder_id", "tag_id", string="Tags"),
        
    }
purchaseorder_taggings()
