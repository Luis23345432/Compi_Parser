from typing import List


def trim(s: str) -> str:
    s = s.strip(" \t\n\r")
    return s


def split(s: str, delim: str) -> List[str]:
    if delim == ' ':
        # keep simple split behavior similar to C++ that ignores empty segments
        parts = [p for p in s.split(delim) if p != '']
        return parts
    out: List[str] = []
    cur = ''
    for ch in s:
        if ch == delim:
            if cur != '':
                out.append(cur)
            cur = ''
        else:
            cur += ch
    if cur != '':
        out.append(cur)
    return out
