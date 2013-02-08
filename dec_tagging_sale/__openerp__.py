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
    "name": "DEC Tagging (Sale)",
    "version": "1.0",
    "depends": ["dec_tagging", "sale" ],
    "author": "Marco Dieckhoff, BREMSKERL",
    "category": "Tools",
    "description": "Tags Sales Orders (see module Tagging)",
    "init_xml": [],
    'update_xml': ["tagging_view.xml"],
    'demo_xml': [],
    'installable': True,
    'active': False,
#    'certificate': '${certificate}',
}
