# -*- encoding: utf-8 -*-

from openerp import models, fields, api

class ResPartnerAcademy(models.Model):
    """ Description """

    _name = 'res.partner.academy'
    _description = 'Academy'
    _rec_name = 'name'

    _columns = {     
        'name': fields.Text('Name', required=True),
    }

    _defaults = {

    }
 
    _order = 'name'



