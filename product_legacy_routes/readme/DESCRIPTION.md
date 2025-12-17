This module restores legacy procurement and supply selectors on products.

- Adds a Procurement method field with Make to Stock / Make to Order choices.
- Adds a Supply method field with Buy / Produce choices.
- Keeps product routes synchronized automatically when users change these
  selectors.

## Technical details

**Legacy product selectors**

The module extends `product.template` with two stored computed selection fields,
`procure_method` and `supply_method`, each with an inverse method. The compute
methods read `route_ids` and map active routes to legacy-style values. The
inverse methods update `route_ids` so route configuration follows the selected
legacy value.

**Route resolution**

The implementation resolves standard routes through helper methods:
- buy: `purchase_stock.route_warehouse0_buy`
- manufacture: `mrp.route_warehouse0_manufacture`
- mto: `stock.route_warehouse0_mto`
- mto+mts: `stock_mts_mto_rule.route_mto_mts`

These helpers rely on `_find_or_create_global_route(..., raise_if_not_found=True)`
to ensure route references are available and consistent.

**Product form integration**

An inherited `product.template` form view injects both fields before `type`,
hidden for services (`invisible="type == 'service'"`) and restricted to ERP
managers (`groups="base.group_erp_manager"`).

**Post-init behavior**

The post-init hook explicitly reactivates `stock.route_warehouse0_mto` so the
Make to Order path remains available after installation.
