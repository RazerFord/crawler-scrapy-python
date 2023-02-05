import html2text


def clear(text_):
    if text_ is None:
        return ""
    h = html2text.HTML2Text()
    h.ignore_links = True
    return h.handle(text_)
