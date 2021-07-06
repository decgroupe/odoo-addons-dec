# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Jun 2020

import os
import sys
import random
import re
import json
import requests
import unicodedata
import importlib

from lxml import html
from collections import OrderedDict

# https://stackoverflow.com/questions/23705304/can-json-loads-ignore-trailing-commas
from jsoncomment import JsonComment

from . import requests_html


def reload():
    importlib.reload(requests_html)


def dict_to_json(value):
    return str(json.dumps(
        value,
        indent=4,
        ensure_ascii=False,
    ))


def fill_common_data(
    code,
    name,
    manufacturer,
    description,
    public_price,
    purchase_price,
    supplier,
    image_url,
    other={}
):
    res = {
        'code': code,
        'name': name,
        'manufacturer': manufacturer,
        'description': description,
        'public_price': public_price,
        'purchase_price': purchase_price,
        'supplier': supplier,
        'image_url': image_url,
        'other': other,
    }
    return res


# ua_version = random.randint(75, 78)
# user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:{0}.0) Gecko/20100101 Firefox/{0}.0".format(
#     ua_version
# )

# HEADERS = {
#     "User-Agent": user_agent,
#     "Accept-Encoding": "gzip, deflate",
#     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#     "DNT": "1",
#     "Connection": "close",
#     "Upgrade-Insecure-Requests": "1",
# }

# Internet Explorer 11 on Windows 10
# Using https://www.whatismybrowser.com/detect/what-http-headers-is-my-browser-sending
HEADERS = {
    "ACCEPT":
        "text/html, application/xhtml+xml, image/jxr, */* ",
    "ACCEPT-ENCODING":
        "gzip, deflate",
    "ACCEPT-LANGUAGE":
        "fr-FR,fr;q=0.5 ",
    "USER-AGENT":
        "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko"
}


def get_html_tree(content, use_javascript=False):
    if use_javascript:
        session = requests_html.HTMLSession()
        r = session.get(content)
        r.html.render()  # this call executes the js in the page
        content = r.html.html
    else:
        # Convert URL to HTML content
        if content.startswith('http'):
            page = requests.get(content, headers=HEADERS)
            #print(page.encoding)
            content = page.content.decode(page.encoding)
            #print(content)

        if 'captcha' in str(content):
            path = os.path.dirname(__file__)
            f = open(os.path.join(path, '_captcha_out.html'), 'w')
            f.write(content)
            f.close()
            print(
                'CAPTCHA REQUEST DETECTED, OUTPUT WRITTEN TO _captcha_out.html'
            )

    tree = html.fromstring(content)
    return tree


def normalize_caseless(text):
    return unicodedata.normalize("NFKD", text.casefold())


def caseless_equal(left, right):
    return normalize_caseless(left) == normalize_caseless(right)


def load_json_string(string, create_file=False, output_filename='./out.json'):
    if create_file:
        f = open(output_filename, 'w')
        f.write(string)
        f.close()
    res = JsonComment(json).loads(string, object_pairs_hook=OrderedDict)
    return res


def clean(xpath_res):
    if isinstance(xpath_res, list):
        if not xpath_res:
            return ''
        xpath_res = ' '.join(xpath_res)
    # We could use span[normalize-space(translate(text(),"\n", ""))
    xpath_res = os.linesep.join(
        [s for s in xpath_res.splitlines() if s.strip()]
    )
    xpath_res = xpath_res.strip()
    # Remove non-breaking space characters
    xpath_res = xpath_res.replace(u'\u00a0', '')
    # Remove multiple spaces
    xpath_res = re.sub(' +', ' ', xpath_res)
    return xpath_res


class ParserResultDict(OrderedDict):
    def __init__(self):
        super()
        self['description'] = ''

    def add_description_title(self, name):
        if name:
            if self['description']:
                self['description'] += os.linesep * 2
            self['description'] += '{}:'.format(name.rstrip(':'))

    def add_description(self, name, value, prefix='-'):
        if name and value:
            if self['description']:
                self['description'] += os.linesep
            self['description'] += '{} {}: {}'.format(
                prefix,
                name.rstrip(':'),
                value,
            )


reload()
