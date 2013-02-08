# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP Module
#    
#    Copyright (C) 2010-2011 BREMSKERL-REIBBELAGWERKE EMMERLING GmbH & Co. KG
#    Author Marco Dieckhoff
#
##############################################################################
{
    "name": "Tagging (Stock)",
    "version": "1.0",
    "depends": ["tagging", "stock" ],
    "author": "Marco Dieckhoff, BREMSKERL",
    "category": "Tools",
    "description": "Tags Pickings: Incoming Shipments, Internal Moves, Delivery Orders (see module Tagging)",
    "init_xml": [],
    'update_xml': ["view/tagging_view.xml",
                   ],
    'demo_xml': [],
    'installable': True,
    'active': False,
#    'certificate': '${certificate}',
}