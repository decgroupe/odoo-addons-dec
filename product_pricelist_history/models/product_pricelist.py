# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2020

from itertools import chain

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ProductPricelist(models.Model):
    _inherit = "product.pricelist"

    def _ensure_history_struct(self, history, key):
        if not key in history:
            history[key] = {
                "steps": [],
                "indent": 0,
                "graph": {
                    "header": ["graph TD", ""],
                    "body": [],
                    "descriptions": {},
                    "depth": 0,
                    "state": {
                        "last_id": "",
                        "count": 0,
                    },
                },
            }

    @api.model
    def _addto_history(
        self,
        key,
        message=False,
        indent=False,
        unindent=False,
        last_state_id=False,
        action="",
    ):
        res = message
        if "history" in self.env.context:
            self._ensure_history_struct(self.env.context["history"], key)
            ctx = self.env.context["history"][key]
            if indent:
                ctx["indent"] = ctx["indent"] + 2
            elif unindent:
                ctx["indent"] = max(0, ctx["indent"] - 2)

            tab = " " * ctx["indent"]

            graph = ctx["graph"]
            state = graph["state"]
            descriptions = graph["descriptions"]
            state_id = False

            if action == "open":
                graph["depth"] = graph["depth"] + 1
            elif action == "close":
                graph["depth"] = graph["depth"] - 1
            if not last_state_id:
                last_state_id = state.get("last_id", False)

            if message:
                ctx["steps"].append(tab + message)

                state["count"] = state["count"] + 1
                state_id = "s{}".format(state["count"])
                descriptions[state_id] = message
                state["last_id"] = state_id
                res = state_id

            if state_id:
                if action == "end":
                    graph["body"].append(
                        '{}["{}"]'.format(
                            state_id,
                            descriptions[state_id],
                        )
                    )
                elif last_state_id:
                    graph["body"].append(
                        '{}["{}"] --> {}["{}"]'.format(
                            last_state_id,
                            descriptions[last_state_id],
                            state_id,
                            descriptions[state_id],
                        )
                    )

        return res

    def _compute_price_rule(self, products_qty_partner, date=False, uom_id=False):
        history = self.env.context.get("history", False)
        if isinstance(history, dict) and history.get("level", 0) >= 0:
            if not "level" in history:
                history["level"] = 0
            history["level"] += 1
            res = self._compute_price_rule_history(products_qty_partner, date, uom_id)
            history["level"] -= 1
            if history["level"] == 0:
                history["level"] = -1
                # for product, qty, partner in products_qty_partner:
                #     hkey = (product, qty, partner)
                #     self._addto_history(hkey, _('Done ...').format(self.name))
        res = super()._compute_price_rule(products_qty_partner, date, uom_id)
        return res

    # This method is a copy/paste of the one in:
    #   ./addons/product/models/product_pricelist.py
    # except that `_addto_history` has been added.
    # yapf: disable
    def _compute_price_rule_history(self, products_qty_partner, date=False, uom_id=False):
        """ Low-level method - Mono pricelist, multi products
        Returns: dict{product_id: (price, suitable_rule) for the given pricelist}

        Date in context can be a date, datetime, ...

            :param products_qty_partner: list of typles products, quantity, partner
            :param datetime date: validity date
            :param ID uom_id: intermediate unit of measure
        """
        self.ensure_one()
        if not date:
            date = self._context.get('date') or fields.Datetime.now()
        if not uom_id and self._context.get('uom'):
            uom_id = self._context['uom']
        if uom_id:
            # rebrowse with uom if given
            products = [item[0].with_context(uom=uom_id) for item in products_qty_partner]
            products_qty_partner = [(products[index], data_struct[1], data_struct[2]) for index, data_struct in enumerate(products_qty_partner)]
        else:
            products = [item[0] for item in products_qty_partner]

        if not products:
            return {}

        categ_ids = {}
        for p in products:
            categ = p.categ_id
            while categ:
                categ_ids[categ.id] = True
                categ = categ.parent_id
        categ_ids = list(categ_ids)

        is_product_template = products[0]._name == "product.template"
        if is_product_template:
            prod_tmpl_ids = [tmpl.id for tmpl in products]
            # all variants of all products
            prod_ids = [p.id for p in
                        list(chain.from_iterable([t.product_variant_ids for t in products]))]
        else:
            prod_ids = [product.id for product in products]
            prod_tmpl_ids = [product.product_tmpl_id.id for product in products]

        items = self._compute_price_rule_get_items(products_qty_partner, date, uom_id, prod_tmpl_ids, prod_ids, categ_ids)

        results = {}
        for product, qty, partner in products_qty_partner:
            hkey = (product, qty, partner)
            self._addto_history(hkey, _('Using {}').format(self.name), action='open')
            if len(items) > 0:
                self._addto_history(hkey, _('{} rule(s) loaded').format(len(items)))
            else:
                self._addto_history(hkey, _('No rules loaded at this step'), action='close')

            results[product.id] = 0.0
            suitable_rule = False

            # Final unit price is computed according to `qty` in the `qty_uom_id` UoM.
            # An intermediary unit price may be computed according to a different UoM, in
            # which case the price_uom_id contains that UoM.
            # The final price will be converted to match `qty_uom_id`.
            qty_uom_id = self._context.get('uom') or product.uom_id.id
            qty_in_product_uom = qty
            if qty_uom_id != product.uom_id.id:
                try:
                    qty_in_product_uom = self.env['uom.uom'].browse([self._context['uom']])._compute_quantity(qty, product.uom_id)
                except UserError:
                    # Ignored - incompatible UoM in context, use default product UoM
                    pass
            history_state_id = self._addto_history(hkey, _('Quantity is {}').format(qty_in_product_uom))

            # if Public user try to access standard price from website sale, need to call price_compute.
            # TDE SURPRISE: product can actually be a template
            price = product.price_compute('list_price')[product.id]
            # history_state_id = self._addto_history(hkey, _('Base price is {}').format(price))

            price_uom = self.env['uom.uom'].browse([qty_uom_id])
            for rule in items:
                self._addto_history(hkey, _('Parse rule [{}] {}').format(rule.id, rule.name), last_state_id=history_state_id)
                if rule.min_quantity and qty_in_product_uom < rule.min_quantity:
                    continue
                if is_product_template:
                    if rule.product_tmpl_id and product.id != rule.product_tmpl_id.id:
                        continue
                    if rule.product_id and not (product.product_variant_count == 1 and product.product_variant_id.id == rule.product_id.id):
                        # product rule acceptable on template if has only one variant
                        continue
                else:
                    if rule.product_tmpl_id and product.product_tmpl_id.id != rule.product_tmpl_id.id:
                        continue
                    if rule.product_id and product.id != rule.product_id.id:
                        continue

                if rule.categ_id:
                    cat = product.categ_id
                    while cat:
                        if cat.id == rule.categ_id.id:
                            break
                        cat = cat.parent_id
                    if not cat:
                        continue

                if rule.base == 'pricelist' and rule.base_pricelist_id:
                    self._addto_history(hkey, _('Price is based on another pricelist: {}').format(rule.base_pricelist_id.name))
                    self._addto_history(hkey, indent=True)
                    price = rule.base_pricelist_id._compute_price_rule([(product, qty, partner)], date, uom_id)[product.id][0]  # TDE: 0 = price, 1 = rule
                    src_currency = rule.base_pricelist_id.currency_id
                    self._addto_history(hkey, unindent=True)
                else:
                    # if base option is public price take sale price else cost price of product
                    # price_compute returns the price in the context UoM, i.e. qty_uom_id
                    self._addto_history(hkey, _('Price is based on "{}"').format(rule.base))
                    price = product.price_compute(rule.base)[product.id]
                    if rule.base == 'standard_price':
                        src_currency = product.cost_currency_id
                    else:
                        src_currency = product.currency_id

                if src_currency != self.currency_id:
                    price = src_currency._convert(
                        price, self.currency_id, self.env.company, date, round=False)

                if price is not False:
                    self._addto_history(hkey, _('Base price is {}').format(price))
                    price = rule._compute_price(price, price_uom, product, quantity=qty, partner=partner)
                    suitable_rule = rule
                break

            if not suitable_rule:
                cur = product.currency_id
                price = cur._convert(price, self.currency_id, self.env.company, date, round=False)
            results[product.id] = (price, suitable_rule and suitable_rule.id or False)
            if suitable_rule:
                rule_name = _('with rule [{}] {}').format(suitable_rule.id, suitable_rule.name)
            else:
                rule_name = _("without any rule")
            self._addto_history(hkey, _('Returns {} {}').format(price, rule_name), action='close')
        return results
    # yapf: enable

    def price_get_multi_history(self, raw_products_by_qty_by_partner):
        """Multi pricelist, multi product  - return tuple"""
        history = {}
        products_by_qty_by_partner = []
        for product, qty, partner in raw_products_by_qty_by_partner:
            if type(product) == int:
                product = self.env["product.product"].browse(product)
            if type(partner) == int:
                partner = self.env["res.partner"].browse(partner)
            products_by_qty_by_partner.append((product, qty, partner))
        res = self.with_context(history=history)._compute_price_rule_multi(
            products_by_qty_by_partner
        )
        return history

    # def _register_hook(self):
    #     model = self.env[self._name]
    #     model._patch_method(
    #         "_compute_price_rule",
    #         ProductPricelist._compute_price_rule_history,
    #     )
    #     return super()._register_hook()
