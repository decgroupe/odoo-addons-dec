# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2023

# https://stackoverflow.com/a/42449998

RESET_SEQ = "\033[0m"
FORMAT_SEQ = "\033[%dm"

_NORMAL = 0
_BOLD = 1
_DIM = 2
_ITALIC = 3
_UNDERLINED = 4
_BLINKING = 5
_REVERSE = 7
_INVISIBLE = 8


def bold(text):
    return FORMAT_SEQ % (_BOLD) + text + RESET_SEQ


def dim(text):
    return FORMAT_SEQ % (_DIM) + text + RESET_SEQ


def italic(text):
    return FORMAT_SEQ % (_ITALIC) + text + RESET_SEQ


def underlined(text):
    return FORMAT_SEQ % (_UNDERLINED) + text + RESET_SEQ


def blinking(text):
    return FORMAT_SEQ % (_BLINKING) + text + RESET_SEQ


def reverse(text):
    return FORMAT_SEQ % (_REVERSE) + text + RESET_SEQ


def invisible(text):
    return FORMAT_SEQ % (_INVISIBLE) + text + RESET_SEQ
