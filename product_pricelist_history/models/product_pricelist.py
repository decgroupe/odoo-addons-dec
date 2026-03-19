# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2020
# ruff: noqa: E501

from odoo import api, fields, models


class ProductPricelist(models.Model):
    _inherit = "product.pricelist"

    def _ensure_history_struct(self, history, key):
        if key not in history:
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
        return self.with_context(history=history)

    @api.model
    def _addto_history(
        self,
        key,
        message=False,
        indent=False,
        unindent=False,
        last_state_id=False,
        set_as_last_state=True,
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
                if set_as_last_state:
                    state["last_id"] = state_id
                res = state_id

            if state_id:
                if action == "end":
                    graph["body"].append(f'{state_id}["{descriptions[state_id]}"]')
                elif last_state_id:
                    graph["body"].append(
                        f'{last_state_id}["{descriptions[last_state_id]}"] --> {state_id}["{descriptions[state_id]}"]'
                    )

        return res

    def _compute_price_rule(
        self,
        products,
        quantity,
        currency=None,
        uom=None,
        date=False,
        compute_price=True,
        **kwargs,
    ):
        # first, check if we have to use history
        history = self.env.context.get("history", False)
        if isinstance(history, dict) and history.get("level", 0) >= 0:
            if "level" not in history:
                history["level"] = 0
            history["level"] += 1
            res = self._compute_price_rule_history(
                products, quantity, currency, uom, date, compute_price, **kwargs
            )
            history["level"] -= 1
            if history["level"] == 0:
                history["level"] = -1
        # finally, call the super to keep normal behavior
        res = super()._compute_price_rule(
            products, quantity, currency, uom, date, compute_price, **kwargs
        )
        return res

    # This method is a copy/paste of the one in:
    #   ./addons/product/models/product_pricelist.py:_compute_price_rule
    # except that `_addto_history` has been added.
    # yapf: disable
    def _compute_price_rule_history(
            self, products, quantity, currency=None, uom=None, date=False, compute_price=True,
            **kwargs
    ):
        """ Low-level method - Mono pricelist, multi products
        Returns: dict{product_id: (price, suitable_rule) for the given pricelist}

        Note: self and self.ensure_one()

        :param products: recordset of products (product.product/product.template)
        :param float quantity: quantity of products requested (in given uom)
        :param currency: record of currency (res.currency)
                         note: currency.ensure_one()
        :param uom: unit of measure (uom.uom record)
            If not specified, prices returned are expressed in product uoms
        :param date: date to use for price computation and currency conversions
        :type date: date or datetime
        :param bool compute_price: whether the price should be computed (default: True)

        :returns: product_id: (price, pricelist_rule)
        :rtype: dict
        """
        self and self.ensure_one()  # self is at most one record

        currency = currency or self.currency_id or self.env.company.currency_id
        currency.ensure_one()

        if not products:
            return {}

        if not date:
            # Used to fetch pricelist rules and currency rates
            date = fields.Datetime.now()

        # Fetch all rules potentially matching specified products/templates/categories and date
        rules = self._get_applicable_rules(products, date, **kwargs)

        results = {}
        for product in products:
            # Build a history key based on function parameters
            hkey = (product, quantity, uom)
            self._addto_history(hkey, self.env._('Using {}').format(self.name), action='open')
            if len(rules) > 0:
                self._addto_history(hkey, self.env._('{} rule(s) loaded').format(len(rules)))
            else:
                self._addto_history(hkey, self.env._('No rules loaded at this step'), action='close')

            suitable_rule = self.env['product.pricelist.item']

            product_uom = product.uom_id
            target_uom = uom or product_uom  # If no uom is specified, fall back on the product uom

            # Compute quantity in product uom because pricelist rules are specified
            # w.r.t product default UoM (min_quantity, price_surchage, ...)
            if target_uom != product_uom:
                qty_in_product_uom = target_uom._compute_quantity(
                    quantity, product_uom, raise_if_failure=False
                )
            else:
                qty_in_product_uom = quantity

            history_state_id = self._addto_history(hkey, self.env._('Quantity is %(quantity)d', quantity=qty_in_product_uom))

            for rule in rules:
                last_state_id = self._addto_history(hkey, self.env._('Parse rule [%(rule_id)d] %(rule_name)s', rule_id=rule.id, rule_name=rule.name), last_state_id=history_state_id)
                if rule.with_context(hkey=hkey, last_state_id=last_state_id)._is_applicable_for(product, qty_in_product_uom):
                    suitable_rule = rule
                    break

            if not suitable_rule:
                # This step is needed for proper graph generation, otherwise, the
                # price computation step would be directly linked to the last rule
                # parsing step.
                self._addto_history(hkey, self.env._('No suitable rule found'), last_state_id=history_state_id)

            if compute_price:
                price = suitable_rule._compute_price(
                    product, quantity, target_uom, date=date, currency=currency)
            else:
                # Skip price computation when only the rule is requested.
                price = 0.0
            results[product.id] = (price, suitable_rule.id)

            if suitable_rule:
                rule_name = self.env._('with rule [%(rule_id)d] %(rule_name)s', rule_id=suitable_rule.id, rule_name=suitable_rule.name)
            else:
                rule_name = self.env._("without any rule")
            self._addto_history(hkey, self.env._('Returns %(price)s %(rule_name)s', price=price, rule_name=rule_name), action='close')

        return results
    # yapf: enable
