"""Render inert Foundry enrichers as labels; never execute source commands."""
import re

START = re.compile(r'[@&]([A-Za-z][A-Za-z0-9_]*)\[')


def display_enrichers(value):
    """Keep UUID markup for the link resolver; flatten every other enricher.

    Balanced brackets retain nested damage types. Explicit labels win; otherwise
    use positional text or the first stored option value, omitting command flags.
    Malformed/unclosed markup is retained rather than consuming unrelated text.
    """
    parts = []; end = 0
    for match in START.finditer(value):
        if match.start() < end: continue
        pos = match.end(); depth = 1
        while pos < len(value) and depth:
            if value[pos] == '[': depth += 1
            elif value[pos] == ']': depth -= 1
            pos += 1
        if depth: break
        stop = pos; label = None
        if pos < len(value) and value[pos] == '{':
            close = value.find('}', pos + 1)
            if close >= 0: label = value[pos+1:close]; stop = close+1
        if match[1] == 'UUID' and value[match.start()] == '@': continue
        body = value[match.end():pos-1].strip()
        tokens = body.split()
        positional = [t for t in tokens if '=' not in t]
        fallback = ' '.join(positional) if positional else (tokens[0].split('=',1)[-1] if tokens else '')
        parts.extend((value[end:match.start()], label if label is not None else fallback))
        end = stop
    parts.append(value[end:])
    return ''.join(parts)
