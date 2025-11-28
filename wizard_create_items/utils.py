# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Nov 2025

import itertools
import re

from lxml import etree
from lxml import html as lxml_html

from odoo.tools.mail import is_html_empty


# Function copy from `Odoo 18.0 > mail/tools/mail.py:html2plaintext` to also
# consider <div> tags as new lines
def html2plaintext(
    html, body_id=None, encoding="utf-8", include_references=True
):  # pragma: no cover
    # fmt: off
    """ From an HTML text, convert the HTML to plain text.
    If @param body_id is provided then this is the tag where the
    body (not necessarily <body>) starts.
    :param include_references: If False, numbered references and
        URLs for links and images will not be included.
    """
    ## (c) Fry-IT, www.fry-it.com, 2007
    ## <peter@fry-it.com>
    ## download here: http://www.peterbe.com/plog/html2plaintext
    if not (html and html.strip()):
        return ''

    if isinstance(html, bytes):
        html = html.decode(encoding)
    else:
        assert isinstance(html, str), f"expected str got {html.__class__.__name__}"

    tree = etree.fromstring(html, parser=etree.HTMLParser())

    if body_id is not None:
        source = tree.xpath(f'//*[@id="{body_id}"]')
    else:
        source = tree.xpath('//body')
    if len(source):
        tree = source[0]

    url_index = []
    linkrefs = itertools.count(1)
    if include_references:
        for link in tree.findall('.//a'):
            if url := link.get('href'):
                link.tag = 'span'
                link.text = f'{link.text} [{next(linkrefs)}]'
                url_index.append(url)

        for img in tree.findall('.//img'):
            if src := img.get('src'):
                img.tag = 'span'
                if src.startswith('data:'):
                    img_name = None  # base64 image
                else:
                    img_name = re.search(r'[^/]+(?=\.[a-zA-Z]+(?:\?|$))', src)
                name = img_name[0] if img_name else 'Image'
                img.text = f'{name} [{next(linkrefs)}]'
                url_index.append(src)

    html = etree.tostring(tree, encoding="unicode")
    # \r char is converted into &#13;, must remove it
    html = html.replace('&#13;', '')

    html = html.replace('<strong>', '*').replace('</strong>', '*')
    html = html.replace('<b>', '*').replace('</b>', '*')
    html = html.replace('<h3>', '*').replace('</h3>', '*')
    html = html.replace('<h2>', '**').replace('</h2>', '**')
    html = html.replace('<h1>', '**').replace('</h1>', '**')
    html = html.replace('<em>', '/').replace('</em>', '/')
    html = html.replace('<tr>', '\n')
    html = html.replace('</div>', '\n')
    html = html.replace('</p>', '\n')
    html = re.sub(r'<br\s*/?>', '\n', html)
    html = re.sub('<.*?>', ' ', html)
    html = html.replace(' ' * 2, ' ')
    html = html.replace('&gt;', '>')
    html = html.replace('&lt;', '<')
    html = html.replace('&amp;', '&')
    html = html.replace('&nbsp;', '\N{NO-BREAK SPACE}')

    # strip all lines
    html = '\n'.join([x.strip() for x in html.splitlines()])
    html = html.replace('\n' * 2, '\n')

    if url_index:
        html += '\n\n'
        for i, url in enumerate(url_index, start=1):
            html += f'[{i}] {url}\n'

    return html.strip()
    # fmt: on


def _deduplicate(items):
    # Deduplicate while preserving order
    seen = set()
    unique = []
    for item in items:
        if item not in seen:
            seen.add(item)
            unique.append(item)
    return unique


def _detect_separator(items):
    """
    Detect common separator pattern in a list of items.

    Scans items to find a consistent separator that could indicate
    an identifier-name pattern (e.g., "=", ":", "---", " - ").

    Returns the detected separator string, or None if no consistent pattern found.
    """
    if not items or len(items) < 2:
        return None

    # Common separators to check, in order of preference
    separators = [":", "=", " - ", " – ", " — ", "---", "--", "|"]
    # Probability map table based on items count
    probabilities = {
        1: 0,  # With 1 item, always detect separator
        2: 0.3,  # With 2 items, need at least - (--%) to match
        3: 0.4,  # With 3 items, need at least - (--%) to match
        4: 0.5,  # With 4 items, need at least - (--%) to match
        5: 0.6,  # With 5 items, need at least - (--%) to match
    }

    for sep in separators:
        # Count how many items contain this separator
        count = sum(1 for item in items if sep in item)
        if count == 0:
            continue
        probability_threshold = probabilities.get(len(items), 0.7)
        # If at least the probability threshold of items have this separator,
        # consider it valid
        if count >= len(items) * probability_threshold:
            return sep

    return None


def _parse_items_with_separator(raw_items, separator=None):
    """
    Parse a list of items and extract identifier-name pairs.

    Detects separator patterns and splits each item into (identifier, name) tuples.
    If no separator is detected or an item doesn't contain the separator,
    returns (empty_string, item) tuples.

    Returns a list of unique tuples (identifier, name) (deduplicated while preserving
    order).
    """
    if not raw_items:
        return [], separator

    # Try to detect identifier-name separator
    if not separator:
        separator = _detect_separator(raw_items)

    if separator:
        # Split items into (identifier, name) tuples
        items = []
        for item in raw_items:
            if separator in item:
                parts = item.split(separator, 1)
                identifier = parts[0].strip()
                name = parts[1].strip()
                items.append((identifier, name))
            else:
                # No separator found, use empty identifier
                items.append(("", item.strip()))
    else:
        # No separator detected, use empty identifiers
        items = [("", item) for item in raw_items]

    return _deduplicate(items), separator


def _extract_items_from_list(html_content):
    if not html_content or is_html_empty(html_content):
        return []

    items = []
    doc = lxml_html.fromstring(html_content)

    for xpath in ("//ul/li", "//ol/li"):
        for li in doc.xpath(xpath):
            text = " ".join(t.strip() for t in li.itertext() if t.strip())
            if text:
                items.append(text)

    return items


def _extract_items_from_table(html_content):
    """
    Extract items from HTML table.

    Expects table where:
    - Single column: item name only (returns list of strings)
    - Two columns: item ID and name (returns list of tuples)
      - If first column is empty, ID will be empty string

    Returns a list of item names (strings) or tuples (ID, name),
    or empty list if no valid table found.
    """
    if not html_content or is_html_empty(html_content):
        return []

    items = []
    doc = lxml_html.fromstring(html_content)

    # Find all table rows
    rows = doc.xpath("//table//tr")
    for row in rows:
        cells = row.xpath(".//td | .//th")

        if len(cells) == 1:
            # Single column: just the item name
            id_text = ""
            name_text = " ".join(t.strip() for t in cells[0].itertext() if t.strip())
        elif len(cells) >= 2:
            # Two or more columns: ID and name
            id_text = " ".join(t.strip() for t in cells[0].itertext() if t.strip())
            name_text = " ".join(t.strip() for t in cells[1].itertext() if t.strip())

        # Only require name to be non-empty; ID can be empty
        if name_text:
            items.append((id_text, name_text))

    return _deduplicate(items)


def _extract_items_from_plaintext(html_content):
    """
    Extract items from plain text content.

    Tries two methods in order:
    1. Extract from lines starting with "-" (Markdown-style lists)
    2. Extract from all non-empty lines

    Returns a list of unique tuples (identifier, name) (deduplicated while preserving
    order).
    """
    if not html_content or is_html_empty(html_content):
        return []

    # Strip HTML tags for plain text processing
    plain_text = html2plaintext(html_content)

    # Split into lines
    lines = plain_text.split("\n")

    # Method 1: Try to extract lines starting with "-"
    dash_items = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("-"):
            # Remove leading dash and whitespace
            item = stripped[1:].strip()
            if item:
                dash_items.append(item)

    if dash_items:
        items = dash_items
    else:
        # Method 2: Use all non-empty lines
        items = [line.strip() for line in lines if line.strip()]

    return items


def _extract_items_from_html(html_content, separator=None):
    """
    Extract a list of items from HTML content.

    Tries four methods in order:
    1. Extract from HTML <table> where first column is identifier, second is name
    2. Extract from HTML <li> tags (ordered or unordered lists)
    3. Extract from lines starting with "-" (Markdown-style lists)
    4. Extract from all non-empty lines

    All methods attempt to detect identifier-name separators (e.g., ":", "=", " - ")
    to extract structured data.

    Returns a list of unique tuples (identifier, name). If no identifier is found, the
    first element of the tuple will be an empty string.
    """
    if not html_content or is_html_empty(html_content):
        return [], separator

    # Method 1: Try to extract from table rows
    items_data = _extract_items_from_table(html_content)
    if not items_data:
        # Method 2: Try to extract <li> items using existing function
        items = _extract_items_from_list(html_content)
        if not items:
            # Method 3 & 4: Parse as plain text
            items = _extract_items_from_plaintext(html_content)
        if items:
            items_data, separator = _parse_items_with_separator(items, separator)

    return items_data, separator
