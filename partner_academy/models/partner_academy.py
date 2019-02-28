# -*- encoding: utf-8 -*-

from openerp import models, fields, api

class res_partner_academy(models.Model):
    """ Description """

    _name = 'res.partner.academy'
    _description = 'Academy'
    _rec_name = 'name'

    _columns = {     
        'name': fields.text('Name', required=True),
    }

    _defaults = {

    }
 
    _order = 'name'

res_partner_academy()


