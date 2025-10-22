from __future__ import annotations
from typing import List
if __package__ is None or __package__ == "":
    from table import Table, Symbol, TERMINAL, NONTERMINAL
else:
    from .table import Table, Symbol, TERMINAL, NONTERMINAL


class Parser:
    def __init__(self, table: Table, startSymbol: int) -> None:
        self.table = table
        self.startSymbol = startSymbol

    def parse(self, tokens: List[str]) -> bool:
        # Convert tokens to IDs
        input_ids: List[int] = []
        for tok in tokens:
            tid = self.table.getTerminalId(tok)
            if tid < 0:
                print(f"[Parser] Token desconocido: {tok}")
                return False
            input_ids.append(tid)

        dollarId = self.table.getTerminalId('$')
        if not input_ids or input_ids[-1] != dollarId:
            input_ids.append(dollarId)

        st: List[Symbol] = []
        st.append(Symbol(TERMINAL, dollarId))
        st.append(Symbol(NONTERMINAL, self.startSymbol))

        ip = 0
        widthPila = 25
        widthEntrada = 25
        widthRegla = 30

        print("\n=== Tabla de derivación ===")
        print(f"{'Pila':<{widthPila}}{'Entrada':<{widthEntrada}}{'Regla aplicada':<{widthRegla}}")
        print('-' * (widthPila + widthEntrada + widthRegla))

        while st:
            top = st[-1]
            lookahead = input_ids[ip]

            pila_names = [
                (self.table.ntsVec[s.value] if s.type == NONTERMINAL else self.table.tsVec[s.value])
                for s in st
            ]
            pilaStr = ' '.join(pila_names) + ' '
            entradaStr = ' '.join(self.table.tsVec[x] for x in input_ids[ip:]) + ' '

            if top.type == TERMINAL:
                if top.value == lookahead:
                    print(f"{pilaStr:<{widthPila}}{entradaStr:<{widthEntrada}}{'Match: ' + self.table.tsVec[top.value]:<{widthRegla}}")
                    st.pop()
                    ip += 1
                else:
                    print(f"[Parser] Error: esperaba '{self.table.tsVec[top.value]}' pero llegó '{self.table.tsVec[lookahead]}'")
                    return False
            else:
                key = (top.value, lookahead)
                if key not in self.table.parserTable:
                    print(f"[Parser] Error: no hay regla para {self.table.ntsVec[top.value]} con lookahead={self.table.tsVec[lookahead]}")
                    return False
                st.pop()
                rhs = self.table.parserTable[key]
                if not rhs:
                    rhsStr = 'ε'
                else:
                    rhsStr = ' '.join(
                        self.table.ntsVec[s.value] if s.type == NONTERMINAL else self.table.tsVec[s.value]
                        for s in rhs
                    ) + ' '
                print(f"{pilaStr:<{widthPila}}{entradaStr:<{widthEntrada}}{self.table.ntsVec[top.value] + ' -> ' + rhsStr:<{widthRegla}}")
                for s in reversed(rhs):
                    st.append(s)

        if ip == len(input_ids):
            print("\n[Parser] Análisis exitoso ")
            return True
        else:
            print("[Parser] Error sintactico ")
            return False
