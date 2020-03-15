# -*- coding: utf-8 -*-

from osv import osv, fields
from tools.translate import _
import string

class tags(osv.osv):
    _name = "tagging.tags"
    _columns = {
        "name": fields.char("Tag", size=64, required=True),
        "color": fields.integer("Color"),
        "description": fields.char("Short Description", size=256),
        "notes": fields.text("Notes"),
        "active": fields.boolean("Active"),
    }
    _defaults = {
        "active": lambda *a: True,
    }
    _sql_constraints = [
        ('tagging_tags_name_unique', 'unique (name)', _('The tag names must be unique!')),
    ]
    _order = 'name'
    
    def strip_accent(self, txt):
        accents = { 'a': ['à', 'ã', 'á', 'â', 'ä'],
                    'c': ['ç'],
                    'e': ['é', 'è', 'ê', 'ë'],
                    'i': ['ì', 'í', 'î', 'ï'],
                    'n': ['ñ'],
                    'u': ['ù', 'ú', 'ü', 'û'], 
                    'y': ['ý', 'ÿ'], 
                    'o': ['ô', 'ö', 'ò', 'ó', 'õ'] } 
        for (char, accented_chars) in accents.iteritems():
            for accented_char in accented_chars:
                txt = txt.replace(accented_char, char)
        return txt


    def on_change_tag_name(self, cr, uid, ids, tag_name, context=None):
        if tag_name:
            v = {}
            
            tag_name = tag_name.strip()
            tag_name = self.strip_accent(tag_name.lower())
            tag_name = tag_name.replace(' ','-')
            
            char_previous = ''
            char_index = 0
            for char_current in tag_name:
                char_index = char_index+1
                if char_current == '-' and char_previous == '-':
                    tag_name = tag_name[:char_index-1] + tag_name[char_index:]
                    char_index = char_index-1
                    
                char_previous = char_current
            
            safe_chars = string.ascii_letters + string.digits + '-'
            tag_name = ''.join([char if char in safe_chars else '' for char in tag_name])
            
            v['name'] = tag_name
            return {'value': v}



tags()

class tagging_related_tags(osv.osv):
    _inherit = "tagging.tags"
    _name = _inherit

    _columns = {
        "related_tags_ids": fields.many2many("tagging.tags", "tagging_related_tags", "tag_id", "related_tag_id", string="Related Tags"),
        
    }
tagging_related_tags()
