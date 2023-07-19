# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jun 2020

import importlib
import re

from . import parser_helper, parser_helper_prices, parser_site_ldlc


def reload():
    importlib.reload(parser_helper)
    importlib.reload(parser_helper_prices)
    importlib.reload(parser_site_ldlc)


def parse(content):
    print("Parsing with", __name__)

    tree = parser_helper.get_html_tree(content)

    result = parser_site_ldlc._parse_group(tree)
    seller = "Hardware.fr"

    if not result["images"]:
        result["images"] = []
        scripts = tree.xpath('//script[@type="text/javascript"]/text()')
        for script in scripts:
            if "ctl00_cphMainContent" in script:
                search = re.search(r"<!\[CDATA\[((?:[^]]|\](?!\]>))*)\]\]>", script)
                if search:
                    ctl00_cphMainContent = search.group(1)
                    # Use re.S to ignore newline character -> SingleLine
                    search = re.search(
                        r"ctl00_cphMainContent = (\[.*\])", ctl00_cphMainContent, re.S
                    )
                    if search:
                        json_data = search.group(1)
                        data = parser_helper.load_json_string(json_data)
                        for item in data:
                            result["images"].append(item["Url"])

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
