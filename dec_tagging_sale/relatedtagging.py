# -*- coding: utf-8 -*-

from osv import osv, fields

class taggings_saleorder(osv.osv):
    _inherit = "tagging.tags"
    _name = _inherit

    _columns = {
        "sale_order_ids": fields.many2many("sale.order", "tagging_saleorder", "tag_id", "saleorder_id", string="Sale Orders"),
        
    }
taggings_saleorder()


class saleorder_taggings(osv.osv):
    _inherit = "sale.order"
    _name = _inherit

    _columns = {
        "tagging_ids": fields.many2many("tagging.tags", "tagging_saleorder", "saleorder_id", "tag_id", string="Tags"),
        
    }
saleorder_taggings()
