# encoding: utf-8
{
	"name" : "DEC Product Pack",
	"version" : "1.0",
	"author" : "Yann Papouin",
	"website" : "http://www.dec-industrie.com",
	"depends" : ["product","dec_sale_layout_margin","dec_purchase"],
	"category" : "Custom Modules",
	"init_xml" : [],
	"demo_xml" : [],
	"update_xml" : [
		'security/ir.model.access.csv',
		'pack_view.xml'
	],
	"active": False,
	"installable": True
}
