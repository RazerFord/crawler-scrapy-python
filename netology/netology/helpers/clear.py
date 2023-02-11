import html2text

"""Очистка текста от html-тегов

Args:
    text_ (str): строка с html-тегами

Returns:
    str: строка без html-тегами
"""
def clear(text_):
    if text_ is None:
        return ""
    h = html2text.HTML2Text()
    h.ignore_links = True
    return h.handle(text_)
