'''
Renderers
'''

import html
import re


URL = re.compile(r'((?:https?|mailto|ftp|gopher|gemini)://\S+)', re.IGNORECASE)


def _split_header(text):
    '''Split header from git commit message (if any)'''
    lines = text.splitlines()
    if len(lines) > 2 and lines[1] == '' and len(lines[0]) <= 100:
        header = lines[0]
        body = '\n'.join(lines[2:])
    else:
        header = ''
        body = text
    return header, body


def plaintext(text):
    '''Render HTML from plain text'''
    header, body = _split_header(text)
    parts = []
    if header:
        parts.append(f'<h1>{html.escape(header)}</h1>')
    for paragraph in body.split('\n\n'):
        if not paragraph.strip():
            continue
        chunks = []
        for chunk in URL.split(paragraph):
            if not chunk.strip():
                continue
            if URL.fullmatch(chunk):
                chunks.append(f'<a href="{chunk}">{html.escape(chunk)}</a>')
            else:
                chunks.append(html.escape(chunk))
        paragraph = '\n'.join(chunks)
        parts.append(f'<p>{paragraph}</p>')
    return '\n'.join(parts)


def lowercase(text):
    return plaintext(text.lower())


def uppercase(text):
    return plaintext(text.upper())


def wikitext(text):  # TODO
    return plaintext(text)


def markdown(text, header=None): # TODO
    '''Render HTML from Markdown text'''
    return plaintext(text)  # TODO