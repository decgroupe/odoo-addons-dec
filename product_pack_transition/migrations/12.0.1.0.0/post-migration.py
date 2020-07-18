from openupgradelib import openupgrade

@openupgrade.migrate()
def migrate(env, version):
    for line in env['product.pack.line'].search([]):
        if line.parent_product_id:
            template = line.parent_product_id.product_tmpl_id
            template.pack_ok = True
            template.pack_type = 'detailed'
            template.pack_component_price = 'ignored'
