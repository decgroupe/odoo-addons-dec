# -*- coding: utf-8 -*-

from osv import osv, fields

class taggings_product(osv.osv):
    _inherit = "tagging.tags"
    _name = _inherit

    _columns = {
        "product_ids": fields.many2many("product.product", "tagging_product", "tag_id", "product_id", string="Products"),
        
    }
    

    def search_tagproduct(self, cr, uid, context=None):
        
        cr.execute('SELECT '\
                        'tagging_tags.name, '\
                        'COUNT(tagging_tags.name) as tagscount '\
                    'FROM '\
                        'tagging_tags, '\
                        'tagging_product '\
                    'WHERE '\
                        'tagging_product.tag_id = tagging_tags.id '\
                    'GROUP BY '\
                        'tagging_tags.name, '\
                        'tagging_tags.id '\
                    'ORDER BY tagscount ')
        
        return cr.fetchall()
    
taggings_product()

class product_taggings(osv.osv):
    _inherit = "product.product"
    _name = _inherit

    _columns = {
        "tagging_ids": fields.many2many("tagging.tags", "tagging_product", "product_id", "tag_id", string="Tags"),
        
    }
    
product_taggings()
