# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jun 2020

import importlib
import re

from . import parser_helper, parser_helper_prices


def reload():
    importlib.reload(parser_helper)
    importlib.reload(parser_helper_prices)


def parse(content):
    print("Parsing with", __name__)

    tree = parser_helper.get_html_tree(content)
    result = parser_helper.ParserResultDict()

    jsons = tree.xpath('//script[@type="application/ld+json"]/text()')
    for item in jsons:
        data = parser_helper.load_json_string(item)
        if data.get("@type") == "Product":
            result["name"] = data.get("name")
            result["code"] = data.get("sku")
            result["images"] = data.get("image")
            result["description_short"] = data.get("description")
            brand = data.get("brand")
            if brand:
                result["brand"] = brand.get("name")
            offers = data.get("offers")
            if offers:
                result["price"] = offers.get("price")
                result["currency"] = offers.get("priceCurrency")

    data = False
    res = tree.xpath("//script/text()")
    for r in res:
        if "dataLayer =" in r:
            search = re.search(r"dataLayer = (\[.*\])", r, re.S)
            if search:
                json_data = search.group(1)
                data = parser_helper.load_json_string(json_data)
                # print(pformat(data))
                break

    if data:
        if isinstance(data, list):
            data = data[0]

        result["name"] = data.get("product_name")
        result["barcode"] = data.get("EAN")
        result["category"] = data.get("category_name")
        result["price"] = data.get("product_price")
        result["seller"] = data.get("seller_name")
        result["brand"] = data.get("product_brand_name")

    seller = "ManoMano"
    if result.get("seller"):
        seller = "{} ({})".format(seller, result["seller"])

    if not result.get("images"):
        result["images"] = tree.xpath('//ul[@id="thumbnails"]/li/@data-image')

    lis = tree.xpath('//div[@class="product-section"]//ul[@class="list-table"]/li')
    for li in lis:
        spans = li.xpath("./span/text()")
        name = parser_helper.clean(spans[0])
        value = parser_helper.clean(spans[1])
        result.add_description(name, value)

    result["price_ttc"] = parser_helper_prices.to_float(result["price"] or "0")

    result = parser_helper.fill_common_data(
        code=result["code"] or "",
        name=result["name"] or "",
        manufacturer=result["brand"] or "",
        description=result["description"] or "",
        public_price=result["price_ttc"] / parser_helper_prices.TVA_20,
        purchase_price=result["price_ttc"] / parser_helper_prices.TVA_20,
        supplier=seller,
        image_url=result["images"] and result["images"][0] or "",
        other=result,
    )
    return result


reload()
