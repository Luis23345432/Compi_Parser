from __future__ import annotations
from typing import Dict, List, Tuple
if __package__ is None or __package__ == "":
    from grammar import Grammar
    from first import First
    from follow import Follow
else:
    from .grammar import Grammar
    from .first import First
    from .follow import Follow


TERMINAL = 'T'
NONTERMINAL = 'N'


class Symbol:
    def __init__(self, typ: str, value: int) -> None:
        self.type = typ
        self.value = value


class Table:
    def __init__(self, g: Grammar, first: First, follow: Follow) -> None:
        self.parserTable: Dict[Tuple[int, int], List[Symbol]] = {}
        self.ntMap: Dict[str, int] = {}
        self.ntsVec: List[str] = []
        self.termMap: Dict[str, int] = {}
        self.tsVec: List[str] = []

        # IDs for non-terminals (sorted like std::set)
        for i, nt in enumerate(sorted(g.nonTerminals)):
            self.ntMap[nt] = i
            self.ntsVec.append(nt)

        # IDs for terminals (sorted)
        for i, t in enumerate(sorted(g.terminals)):
            self.termMap[t] = i
            self.tsVec.append(t)

        # Build LL(1) table
        for ruleStr in g.rules:
            pos = ruleStr.find('->')
            if pos == -1:
                continue
            lhs = ruleStr[:pos].strip()
            rhs = ruleStr[pos + 2 :].strip()
            alternatives = [a.strip() for a in rhs.split('|')]

            for alt in alternatives:
                if not alt or alt == "''" or alt == 'ε':
                    for term in follow.followSets.get(lhs, set()):
                        lhsId = self.getNonTerminalId(lhs)
                        termName = '$' if term == "''" else term
                        termId = self.getTerminalId(termName)
                        self.parserTable[(lhsId, termId)] = []
                    continue

                firstAlpha = set()
                canBeEpsilon = True
                symbols = [s for s in alt.split(' ') if s]

                for s in symbols:
                    if s in g.nonTerminals:
                        firstS = first.firstSets.get(s, set())
                    else:
                        firstS = {s}
                    for f in firstS:
                        if f != "''":
                            firstAlpha.add(f)
                    if "''" not in firstS:
                        canBeEpsilon = False
                        break

                lhsId = self.getNonTerminalId(lhs)
                for term in firstAlpha:
                    tid = self.getTerminalId(term)
                    self.parserTable[(lhsId, tid)] = []
                    for sym in symbols:
                        if sym in self.ntMap:
                            self.parserTable[(lhsId, tid)].append(Symbol(NONTERMINAL, self.ntMap[sym]))
                        elif sym in self.termMap:
                            self.parserTable[(lhsId, tid)].append(Symbol(TERMINAL, self.termMap[sym]))

                if canBeEpsilon:
                    for term in follow.followSets.get(lhs, set()):
                        tid = self.getTerminalId('$' if term == "''" else term)
                        self.parserTable[(lhsId, tid)] = []

    def print(self) -> None:
        from textwrap import shorten
        # header
        print(f"{'NT/T':>5}", end='')
        for t in self.tsVec:
            print(f"{t:>10}", end='')
        print()
        print('-' * (5 + 10 * len(self.tsVec)))
        for i, nt in enumerate(self.ntsVec):
            print(f"{nt:>5}", end='')
            for j, t in enumerate(self.tsVec):
                key = (i, j)
                if key not in self.parserTable:
                    cell = '-'
                else:
                    rhs = self.parserTable[key]
                    if not rhs:
                        cell = "''"
                    else:
                        parts: List[str] = []
                        for s in rhs:
                            parts.append(self.ntsVec[s.value] if s.type == NONTERMINAL else self.tsVec[s.value])
                        cell = ' '.join(parts)
                print(f"{cell:>10}", end='')
            print()

    def getNonTerminalId(self, nt: str) -> int:
        return self.ntMap.get(nt, -1)

    def getTerminalId(self, t: str) -> int:
        return self.termMap.get(t, -1)
