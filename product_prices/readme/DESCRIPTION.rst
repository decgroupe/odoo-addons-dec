Store prices write dates

Note about prices
=================

**product_template** model, there are five price-related columns:

- price
- list_price
- lst_price
- standard_price
- pricelist_id

**product_product** model, there are three price-related columns:
- price
- price_extra
- lst_price

standard_price
--------------
This is the cost or purchase price of a product. It is used to calculate the cost of goods -- mostly for accounting purpose.  Whenever its value changes, Odoo calls _set_standard_price to store value history in the product.price.history table.

price_extra
-----------
The price_extra is a computed field. A product template may have multiple product variants that have a combination of some attribute values. An attribute value can have an extra price. For example, 32GB memory may add an extra $50. The sum of hose extra prices for applicable product variant attributes will the the price_extra.

list_price
----------
This field is the sales or product price displayed in a web site. When one wants to change the list_price of a product, it should change it in the product template. For individual product variant, change the attribute extra price.

lst_price in **product_template**
---------------------------------
It seems that the lst_price field can be used for both product_template and product_product as the product sale price. In product_template model, it points to the list_price field.

*lst_price* in **product_product**
----------------------------------
In product_product model, it is computed field that calls _product_lst_price.
This function calculates the lst_price of a product variant by adding its list_price and its price_extra.
The field also has an inverse function _set_product_lst_price that sets list_price when lst_price changes.
The list_price value is the subtraction of price_extra from lst_price.

For a product variant, the lst_price is the sales or product price displayed in a web site.

price In both :litteral:product_template model and product_product model, it is a computed field to calculate its value.
The method uses product.pricelist model to calculate a price based on rules defined in product.pricelist.item.
any context variables, such as partner, UOM, currency and rule name, are used in finding the price.
The price_get method is called in the calculation.


Differences between *consumable* and *storable*
===============================================

Consumables are meant for products you need to receive in the warehouse, but you will not use to make other products and will not sell them to Customers.  You consume them yourselves.

Examples:  Cleaning Supplies, Coffee, Printer Paper.

- These are the things you would NOT count during a cycle count or full Inventory count.

- You can receive them, deliver  them and see  the movement history.

- Odoo will NOT generate draft Purchase Orders (RFQ's) to tell you to order more nor generate Manufacturing Orders to tell you to make more.

- You would NOT expect to see them in your Inventory Valuation Report.

- You would NOT expect to see them valued on your Balance Sheet.

- They do NOT have any value (always expensed) and are created within Product Categories that are setup to not value Inventory, in other words Manual.

- The COST field on these Products is always $0.00.

- The Expense Account on the Product Category (or Product) is used during processing of the Vendor Bill to post the expense debit.


Storables are meant for products you also need to use in Manufacturing, or sell, or convert into Fixed Assets.

Examples: Raw Material, Resale Products, Forklift.

- These are the things you WOULD count during a cycle count or full inventory count.

- You can receive them, move them  and  deliver  them and see how many (quantity) are in each location (and how much they are worth).

- If these products are replenished through buying them, Odoo WILL generate draft Purchase Orders (RFQ's) to tell you to order more (if you have a Vendor setup on the product and a reordering rule defined)

- If these products are replenished through making them, Odoo WILL generate Manufacturing Orders to tell you to make more (if you have a Bill of Materials defined).

- You WOULD expect to see them in your Inventory Valuation Report.

- You WOULD expect to see them valued on your Balance Sheet.

- They DO have a value (current asset in Inventory) and are created within Product Categories that are setup to value Inventory, in other words Automated.

- The COST field on these Products (set this logic on the Category) is either manually maintained by you (Standard) or automatically maintained by Odoo based on past Purchase Orders (FIFO and Average).

- The Expense Account on the Product Category (or Product) is used during processing of the Customer Invoice (when you sell the storable) to post the cost of goods debit.  Accounts setup on the Production Location determine (for when you use the storable in a Manufacturing Order) where WIP debits (when consumed) and credits (when the finished product is created) are posted.