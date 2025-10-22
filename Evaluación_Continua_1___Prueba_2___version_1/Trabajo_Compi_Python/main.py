from __future__ import annotations
from pathlib import Path
import sys
if __package__ is None or __package__ == "":
    from grammar import Grammar
    from lr1 import LR1Builder
    from lr_parser import LRParser
else:
    from .grammar import Grammar
    from .lr1 import LR1Builder
    from .lr_parser import LRParser


def main() -> None:
    base = Path(__file__).parent
    grammar_path = base / 'gramatica.txt'

    gramatica = Grammar()
    if not gramatica.load_from_file(str(grammar_path)):
        print('Error al cargar la gramática.')
        return

    print("=== Gramática cargada ===")
    gramatica.print()

    # Construcción LR(1)
    lr1 = LR1Builder(gramatica)
    lr1.build_canonical_collection()
    print("\n=== Estados LR(1) ===")
    lr1.print_states()
    # Also print the closure table (kernel & closure per state) for console output
    lr1.print_closure_table()
    lr1.build_tables()
    print("\n=== Tablas LR(1) ===")
    lr1.print_tables()

    # Parser LR(1)
    parser = LRParser(lr1)

    # Entrada como cadena completa (tokens separados por espacios).
    # Ejemplos válidos: "c d d $" o "1 + 3 $". El parser añadirá '$' si falta.
    if len(sys.argv) > 1:
        entrada_str = ' '.join(sys.argv[1:])
    else:
        # Fallback por defecto para ejecución sin argumentos
        entrada_str = "c d d $"

    entrada_tokens = entrada_str.split()
    print("\n=== Parseando entrada (LR1) ===")
    print(f"Entrada: {entrada_tokens}")
    _ = parser.parse(entrada_tokens)


if __name__ == '__main__':
    main()
