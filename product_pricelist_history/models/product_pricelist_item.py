# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2020
# ruff: noqa: E501
# ruff: noqa: E731

from odoo import api, models, tools


class ProductPricelistItem(models.Model):
    _inherit = "product.pricelist.item"

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
        self.pricelist_id._addto_history(
            key, message, indent, unindent, last_state_id, set_as_last_state, action
        )

    def _is_applicable_for(self, product, qty_in_product_uom):
        history = self.env.context.get("history", False)
        if history and history.get("level") > 0:
            self._is_applicable_for_history(product, qty_in_product_uom)
        # Call the real method (to also execute overrides)
        price = super()._is_applicable_for(product, qty_in_product_uom)
        return price

    # This method is a copy/paste of the one in:
    #   ./addons/product/models/product_pricelist_item.py:_is_applicable_for
    # except that `_addto_history` has been added.
    # yapf: disable
    def _is_applicable_for_history(self, product, qty_in_product_uom):
        """Check whether the current rule is valid for the given product & qty.

        Note: self.ensure_one()

        :param product: product record (product.product/product.template)
        :param float qty_in_product_uom: quantity, expressed in product UoM
        :returns: Whether rules is valid or not
        :rtype: bool
        """

        def _addto_history(msg):
            hkey = self.env.context.get("hkey", False)
            last_state_id = self.env.context.get("last_state_id", False)
            self._addto_history(
                hkey, self.env._("Rule %(rule_id)d ignored: %(msg)s", rule_id=self.id, msg=msg), last_state_id=last_state_id, set_as_last_state=False
            )

        self.ensure_one()
        product.ensure_one()
        res = True
        is_product_template = product._name == 'product.template'
        if self.min_quantity and qty_in_product_uom < self.min_quantity:
            _addto_history(
                self.env._(
                    "Quantity %(quantity)d is less than min_quantity %(min_quantity)d",
                    quantity=qty_in_product_uom,
                    min_quantity=self.min_quantity,
                )
            )
            res = False

        elif self.applied_on == "2_product_category":
            if (
                product.categ_id != self.categ_id
                and not product.categ_id.parent_path.startswith(self.categ_id.parent_path)
            ):
                _addto_history(
                    self.env._(
                        "Product category %(product_category)s does not match "
                        "rule category %(rule_category)s",
                        product_category=product.categ_id,
                        rule_category=self.categ_id,
                    )
                )
                res = False
        else:
            # Applied on a specific product template/variant
            if is_product_template:
                if self.applied_on == "1_product" and product._origin.id != self.product_tmpl_id.id:
                    _addto_history(self.env._("Product template %(product_template)s does not match rule template %(rule_template)s", product_template=product, rule_template=self.product_tmpl_id))
                    res = False
                elif self.applied_on == "0_product_variant" and not (
                    product.product_variant_count == 1
                    and product.product_variant_id.id == self.product_id.id
                ):
                    # product self acceptable on template if has only one variant
                    _addto_history(self.env._("Product template %(product_template)s does not match rule variant %(rule_variant)s", product_template=product, rule_variant=self.product_id))
                    res = False
            else:
                if self.applied_on == "1_product" and product.product_tmpl_id.id != self.product_tmpl_id.id:
                    _addto_history(self.env._("Product variant %(product_variant)s does not match rule template %(rule_template)s", product_variant=product, rule_template=self.product_tmpl_id))
                    res = False
                elif self.applied_on == "0_product_variant" and product.id != self.product_id.id:
                    _addto_history(self.env._("Product variant %(product_variant)s does not match rule variant %(rule_variant)s", product_variant=product, rule_variant=self.product_id))
                    res = False

        return res
    # yapf: enable

    def _compute_price(self, product, quantity, uom, date, currency=None):
        """Compute the unit price of a product in the context of a pricelist application.
        The unused parameters are there to make the full context available for overrides.
        """
        history = self.env.context.get("history", False)
        if self and history and history.get("level") > 0:
            self._compute_price_history(product, quantity, uom, date, currency=currency)
        # Call the real method (to also execute overrides)
        price = super()._compute_price(product, quantity, uom, date, currency=currency)
        return price

    # This method is a copy/paste of the one in:
    #   ./addons/product/models/product_pricelist_item.py:_compute_price
    # except that `_addto_history` has been added.
    # yapf: disable
    def _compute_price_history(self, product, quantity, uom, date, currency=None):
        """Compute the unit price of a product in the context of a pricelist application.

        Note: self and self.ensure_one()

        :param product: recordset of product (product.product/product.template)
        :param float qty: quantity of products requested (in given uom)
        :param uom: unit of measure (uom.uom record)
        :param datetime date: date to use for price computation and currency conversions
        :param currency: currency (for the case where self is empty)

        :returns: price according to pricelist rule or the product price, expressed in the param
                  currency, the pricelist currency or the company currency
        :rtype: float
        """
        self and self.ensure_one()  # self is at most one record
        product.ensure_one()
        uom.ensure_one()

        currency = currency or self.currency_id or self.env.company.currency_id
        currency.ensure_one()

        hkey = (product, quantity, uom)

        # Pricelist specific values are specified according to product UoM
        # and must be multiplied according to the factor between uoms
        product_uom = product.uom_id
        if product_uom != uom:
            convert = lambda p: product_uom._compute_price(p, uom)
        else:
            convert = lambda p: p

        if self.compute_price == 'fixed':
            price = convert(self.fixed_price)
            self._addto_history(hkey, self.env._('Price (fixed) set to {}').format(price))
        elif self.compute_price == 'percentage':
            base_price = self._compute_base_price(product, quantity, uom, date, currency)
            price = (base_price - (base_price * (self.percent_price / 100))) or 0.0
            self._addto_history(hkey, self.env._('Price (percentage) set to {}').format(price))
        elif self.compute_price == 'formula':
            base_price = self._compute_base_price(product, quantity, uom, date, currency)
            # complete formula
            price_limit = base_price
            discount = self.price_discount if self.base != 'standard_price' else -self.price_markup
            price = base_price - (base_price * (discount / 100))

            if discount:
                self._addto_history(hkey, self.env._('Price discounted to %(price)d (%(discount)d%)', price=price, discount=discount))

            if self.price_round:
                price = tools.float_round(price, precision_rounding=self.price_round)
                self._addto_history(hkey, self.env._('Price rounded to {}').format(price))

            if self.price_surcharge:
                price_surcharge = convert(self.price_surcharge)
                self._addto_history(hkey, self.env._('Price surcharge applied %(price)d (+%(surcharge)d)',price=price+price_surcharge, surcharge=price_surcharge))
                price += price_surcharge

            if self.price_min_margin:
                price = max(price, price_limit + convert(self.price_min_margin))
                self._addto_history(hkey, self.env._('Price updated (minimum margin) to %(price)d', price=price))

            if self.price_max_margin:
                price = min(price, price_limit + convert(self.price_max_margin))
                self._addto_history(hkey, self.env._('Price updated (maximum margin) to %(price)d', price=price))
        else:  # empty self, or extended pricelist price computation logic
            price = self._compute_base_price(product, quantity, uom, date, currency)

        return price
    # yapf: enable

    def _compute_base_price(self, product, quantity, uom, date, currency):
        history = self.env.context.get("history", False)
        if history and history.get("level") > 0:
            self._compute_base_price_history(product, quantity, uom, date, currency)
        # Call the real method (to also execute overrides)
        price = super()._compute_base_price(product, quantity, uom, date, currency)

        if history and history.get("level") > 0:
            hkey = (product, quantity, uom)
            self._addto_history(hkey, self.env._("Base price is {}").format(price))
        return price

    # This method is a copy/paste of the one in:
    #   ./addons/product/models/product_pricelist_item.py:_compute_base_price
    # except that `_addto_history` has been added.
    # yapf: disable
    def _compute_base_price_history(self, product, quantity, uom, date, currency):
        """ Compute the base price for a given rule

        :param product: recordset of product (product.product/product.template)
        :param float qty: quantity of products requested (in given uom)
        :param uom: unit of measure (uom.uom record)
        :param datetime date: date to use for price computation and currency conversions
        :param currency: currency in which the returned price must be expressed

        :returns: base price, expressed in provided pricelist currency
        :rtype: float
        """
        currency.ensure_one()
        hkey = (product, quantity, uom)
        rule_base = self.base or 'list_price'
        if rule_base == 'pricelist' and self.base_pricelist_id:
            self._addto_history(hkey, self.env._('Price is based on another pricelist: %(pricelist)s', pricelist=self.base_pricelist_id.name))
            self._addto_history(hkey, indent=True)
            price = self.base_pricelist_id._get_product_price(
                product, quantity, currency=self.base_pricelist_id.currency_id, uom=uom, date=date
            )
            src_currency = self.base_pricelist_id.currency_id
            self._addto_history(hkey, unindent=True)
        elif rule_base == "standard_price":
            self._addto_history(hkey, self.env._('Price is based on "%(rule_base)s"', rule_base=rule_base))
            src_currency = product.cost_currency_id
            price = product._price_compute(rule_base, uom=uom, date=date)[product.id]
        else: # list_price
            self._addto_history(hkey, self.env._('Price is based on "%(rule_base)s"', rule_base=rule_base))
            src_currency = product.currency_id
            price = product._price_compute(rule_base, uom=uom, date=date)[product.id]

        if src_currency != currency:
            price = src_currency._convert(price, currency, self.env.company, date, round=False)

        return price
    # yapf: enable
