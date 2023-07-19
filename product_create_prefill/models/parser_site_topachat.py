# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jun 2020

import importlib

from . import parser_helper, parser_helper_prices, parser_site_ldlc


def reload():
    importlib.reload(parser_helper)
    importlib.reload(parser_helper_prices)
    importlib.reload(parser_site_ldlc)


def parse(content):
    print("Parsing with", __name__)

    tree = parser_helper.get_html_tree(content)

    result = parser_site_ldlc._parse_group(tree)
    seller = "TopAchat"

    # Get technical description
    rows = tree.xpath('//div[@class="carac"]//div')
    print(len(rows))
    for line in rows:
        name = parser_helper.clean(
            line.xpath(
                'string(.//div[@class="caracName"]/descendant-or-self::*/text())'
            )
        )
        value = parser_helper.clean(
            line.xpath(
                'string(.//div[@class="caracDesc"]/descendant-or-self::*/text())'
            )
        )
        result.add_description(name, value)

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
