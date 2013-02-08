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
    "name": "DEC Tagging",
    "version": "1.0",
    "depends": ["base", "base_tools" ],
    "author": "Marco Dieckhoff, BREMSKERL",
    "category": "Tools",
    "description": """
This addon, together with it's modular extensions, provides tagging for multiple modules.

Tags can be used to link different objects, from Sales Offers to Delivery Orders to a specific keyword, thus creating a one-point-overview.
Every object may belong to multiple tags, allowing a kind of project-based fast access over all related elements.
 
Tags can be looked up in Tools / Tagging.

Modular extensions provide relations to the different objects. 
    """,
    "init_xml": [],
    'update_xml': ["security/ir.model.access.csv","tagging_view.xml"],
    'demo_xml': [],
    'installable': True,
    'active': False,
#    'certificate': '${certificate}',
}
