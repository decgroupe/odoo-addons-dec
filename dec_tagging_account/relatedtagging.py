# -*- coding: utf-8 -*-

from osv import osv, fields

class taggings_invoice(osv.osv):
    _inherit = "tagging.tags"
    _name = _inherit

    _columns = {
        "invoice_ids": fields.many2many("account.invoice", "tagging_invoice", "tag_id", "invoice_id", string="Invoices"),
        
    }
taggings_invoice()


class invoice_taggings(osv.osv):
    _inherit = "account.invoice"
    _name = _inherit

    _columns = {
        "tagging_ids": fields.many2many("tagging.tags", "tagging_invoice", "invoice_id", "tag_id", string="Tags"),
        
    }
invoice_taggings()
