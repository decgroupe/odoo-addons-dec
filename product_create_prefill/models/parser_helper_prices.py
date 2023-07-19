# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jun 2020

import locale

TVA_20 = 1.2


def _price_to_float(price, utf8_locale):
    default_locale = locale.getdefaultlocale()
    locale.setlocale(locale.LC_ALL, "{}.UTF-8".format(utf8_locale))
    conv = locale.localeconv()
    # Override user settings from OS with mondial values
    locale._override_localeconv["decimal_point"] = conv["mon_decimal_point"]
    raw_numbers = price.strip().strip(conv["currency_symbol"])
    amount = locale.atof(raw_numbers)
    # Dont use locale.resetlocale(), not working on Win32
    locale.setlocale(locale.LC_ALL, default_locale)
    return amount


def fr_to_float(price):
    return _price_to_float(price, "fr_FR")


def us_to_float(price):
    return _price_to_float(price, "en_US")


def replace_dot_with_comma(p):
    if p.count(".") == 1 and not "," in p:
        p = p.replace(".", ",")
    return p


def replace_comma_with_dot(p):
    if p.count(",") == 1 and not "." in p:
        p = p.replace(",", ".")
    return p


def to_float(price, currency=""):
    if isinstance(price, float):
        return price
    if "€" in (currency or price):
        price = replace_dot_with_comma(price)
        return fr_to_float(price)
    elif "EUR" in (currency or price):
        price = replace_dot_with_comma(price)
        return fr_to_float(price)
    elif "$" in (currency or price):
        price = replace_comma_with_dot(price)
        return us_to_float(price)
    else:
        return fr_to_float(price)


def test_to_float():
    m1 = "6,150 €"
    m2 = " $1,730.44"
    print(to_float(m1))
    print(to_float(m2))


# Main Program
if __name__ == "__main__":
    test_to_float()
