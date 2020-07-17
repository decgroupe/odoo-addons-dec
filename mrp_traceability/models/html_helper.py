# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Apr 2020


def div(content, html_class):
    return '<div class="{}">{}</div>'.format(html_class, content)


def ul(content):
    return '<ul>{}</ul>'.format(content)


def li(content):
    return '<li>{}</li>'.format(content)


def small(content):
    return '<small>{}</small>'.format(content)