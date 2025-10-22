from __future__ import annotations
from typing import List, Set
import os, sys
if __package__ is None or __package__ == "":
    from utils import trim, split
else:
    from .utils import trim, split


class Grammar:
    def __init__(self) -> None:
        self.terminals: Set[str] = set()
        self.nonTerminals: Set[str] = set()
        self.initialState: str = ''
        self.rules: List[str] = []

    def load_from_file(self, filename: str) -> bool:
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                rhs_symbols: List[str] = []
                for raw in f:
                    line = trim(raw)
                    if not line or line.startswith('#'):
                        continue
                    self.rules.append(line)

                    pos = line.find('->')
                    if pos == -1:
                        print(f"Regla inválida: {line}")
                        continue
                    left = trim(line[:pos])
                    if not self.nonTerminals:
                        self.initialState = left
                    self.nonTerminals.add(left)

                    right = trim(line[pos+2:])
                    alternatives = split(right, '|')
                    for alt in alternatives:
                        alt = trim(alt)
                        if not alt or alt == "''" or alt == 'ε':
                            continue
                        symbols = split(alt, ' ')
                        for sym in symbols:
                            sym = trim(sym)
                            if sym and sym != "''" and sym != 'ε':
                                rhs_symbols.append(sym)
                for s in rhs_symbols:
                    if s not in self.nonTerminals:
                        self.terminals.add(s)
                self.terminals.add('$')
            return True
        except OSError as e:
            print(f"Error al abrir archivo: {filename}: {e}")
            return False

    def print(self) -> None:
        print(f"Estado inicial: {self.initialState}")
        print("No terminales: ", end='')
        for nt in self.nonTerminals:
            print(nt, end=' ')
        print()
        print("Terminales: ", end='')
        for t in self.terminals:
            print(t, end=' ')
        print()
        print("Reglas:")
        for r in self.rules:
            print(f"  {r}")

    # New: load grammar from a raw string (for API usage)
    def load_from_string(self, text: str) -> bool:
        try:
            # reset
            self.terminals.clear()
            self.nonTerminals.clear()
            self.initialState = ''
            self.rules.clear()

            rhs_symbols: List[str] = []
            for raw in text.splitlines():
                line = trim(raw)
                if not line or line.startswith('#'):
                    continue
                self.rules.append(line)

                pos = line.find('->')
                if pos == -1:
                    print(f"Regla inválida: {line}")
                    continue
                left = trim(line[:pos])
                if not self.nonTerminals:
                    self.initialState = left
                self.nonTerminals.add(left)

                right = trim(line[pos+2:])
                alternatives = split(right, '|')
                for alt in alternatives:
                    alt = trim(alt)
                    if not alt or alt == "''" or alt == 'ε':
                        continue
                    symbols = split(alt, ' ')
                    for sym in symbols:
                        sym = trim(sym)
                        if sym and sym != "''" and sym != 'ε':
                            rhs_symbols.append(sym)

            for s in rhs_symbols:
                if s not in self.nonTerminals:
                    self.terminals.add(s)
            self.terminals.add('$')
            return True
        except Exception as e:
            print(f"Error al cargar gramática desde cadena: {e}")
            return False
