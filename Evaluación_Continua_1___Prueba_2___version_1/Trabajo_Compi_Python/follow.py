from __future__ import annotations
from typing import Dict, Set, List
if __package__ is None or __package__ == "":
    from grammar import Grammar
    from utils import trim, split
    from first import First
else:
    from .grammar import Grammar
    from .utils import trim, split
    from .first import First


class Follow:
    def __init__(self, grammar: Grammar, first: First) -> None:
        self.grammar = grammar
        self.first = first
        self.followSets: Dict[str, Set[str]] = {}

    def compute(self) -> None:
        for nt in self.grammar.nonTerminals:
            self.followSets[nt] = set()
        self.followSets[self.grammar.initialState].add('$')

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
                    n = len(symbols)
                    nullableSuffix = [False] * (n + 1)
                    nullableSuffix[n] = True

                    for j in range(n - 1, -1, -1):
                        s = trim(symbols[j])
                        tieneEps = False
                        if s == "''":
                            tieneEps = True
                        elif s in self.grammar.nonTerminals:
                            fset = self.first.firstSets.get(s, set())
                            tieneEps = ("''" in fset)
                        else:
                            tieneEps = False
                        nullableSuffix[j] = tieneEps and nullableSuffix[j + 1]

                    for i in range(n):
                        A = trim(symbols[i])
                        if not A or A not in self.grammar.nonTerminals:
                            continue

                        if i + 1 < n:
                            nextSym = trim(symbols[i + 1])
                            firstNext: Set[str] = set()
                            if len(nextSym) >= 2 and nextSym[0] == "'" and nextSym[-1] == "'":
                                firstNext.add(nextSym[1:-1])
                            elif nextSym in self.grammar.nonTerminals:
                                firstNext = set(self.first.firstSets.get(nextSym, set()))
                            else:
                                firstNext.add(nextSym)
                            before = len(self.followSets[A])
                            for s in firstNext:
                                if s != "''":
                                    self.followSets[A].add(s)
                            if len(self.followSets[A]) > before:
                                changed = True

                        epsInGamma = nullableSuffix[i + 1]
                        if epsInGamma:
                            before = len(self.followSets[A])
                            self.followSets[A].update(self.followSets[left])
                            if len(self.followSets[A]) > before:
                                changed = True

    def print(self) -> None:
        for nt, s in self.followSets.items():
            items = ", ".join(list(s))
            print(f"Follow({nt}) = {{ {items} }}")
