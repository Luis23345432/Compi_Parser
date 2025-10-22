from __future__ import annotations
from typing import Dict, Set, List
if __package__ is None or __package__ == "":
    from grammar import Grammar
    from utils import trim, split
else:
    from .grammar import Grammar
    from .utils import trim, split


class First:
    def __init__(self, grammar: Grammar) -> None:
        self.grammar = grammar
        self.firstSets: Dict[str, Set[str]] = {}

    def compute(self) -> None:
        for nt_raw in self.grammar.nonTerminals:
            nt = trim(nt_raw)
            self.firstSets[nt] = set()

        changed = True
        while changed:
            changed = False
            for r in self.grammar.rules:
                line = trim(r)
                if not line:
                    continue
                pos = line.find('->')
                if pos == -1:
                    continue
                left = trim(line[:pos])
                right = trim(line[pos+2:])
                alternatives = split(right, '|')
                for alt in alternatives:
                    symbols = split(trim(alt), ' ')
                    if not symbols:
                        continue
                    allEmpty = True
                    for sym in symbols:
                        sym = trim(sym)
                        if not sym:
                            continue
                        if sym == "''":
                            continue
                        elif len(sym) >= 2 and sym[0] == "'" and sym[-1] == "'":
                            contenido = sym[1:-1]
                            if contenido:
                                before = len(self.firstSets[left])
                                self.firstSets[left].add(contenido)
                                if len(self.firstSets[left]) > before:
                                    changed = True
                            allEmpty = False
                            break
                        elif sym in self.grammar.nonTerminals:
                            before = len(self.firstSets[left])
                            for t in self.firstSets.get(sym, set()):
                                if t != "''":
                                    self.firstSets[left].add(t)
                            if len(self.firstSets[left]) > before:
                                changed = True
                            xiNullable = ("''" in self.firstSets.get(sym, set()))
                            if not xiNullable:
                                allEmpty = False
                                break
                        else:
                            before = len(self.firstSets[left])
                            self.firstSets[left].add(sym)
                            if len(self.firstSets[left]) > before:
                                changed = True
                            allEmpty = False
                            break
                    if allEmpty:
                        if "''" not in self.firstSets[left]:
                            self.firstSets[left].add("''")
                            changed = True

    def print(self) -> None:
        for nt, s in self.firstSets.items():
            nt = trim(nt)
            items = ", ".join(list(s))
            print(f"First({nt}) = {{ {items} }}")
