from __future__ import annotations
from typing import List, Tuple, Optional
from dataclasses import dataclass

# Dual-imports for script/module
if __package__ is None or __package__ == "":
    from lr1 import LR1Builder, Production
else:
    from .lr1 import LR1Builder, Production


@dataclass
class ParseNode:
    label: str
    children: List["ParseNode"]


def _render_ascii(node: ParseNode, prefix: str = "", is_last: bool = True) -> List[str]:
    lines: List[str] = []
    if prefix == "":
        lines.append(node.label)
    else:
        connector = "└── " if is_last else "├── "
        lines.append(prefix + connector + node.label)
    new_prefix = prefix + ("    " if is_last else "│   ")
    for i, ch in enumerate(node.children):
        last = (i == len(node.children) - 1)
        lines.extend(_render_ascii(ch, new_prefix, last))
    return lines


class LRParser:
    def __init__(self, lr1: LR1Builder) -> None:
        self.lr1 = lr1
        self.last_tree: Optional["ParseNode"] = None
        # Structured trace captured when collect_trace=True in parse()
        # Each step is a dict with keys: stackStates, stackSymbols, stackDisplay, input, action
        self.last_trace: Optional[List[dict]] = None

    def parse(self, tokens: List[str], collect_trace: bool = False) -> bool:
        # Ensure tables built
        if not self.lr1.states:
            self.lr1.build_canonical_collection()
            self.lr1.build_tables()

        # Append end marker
        if not tokens or tokens[-1] != '$':
            tokens = tokens + ['$']

        # Stacks: states and symbols (for trace)
        state_stack: List[int] = [0]
        symbol_stack: List[str] = []

        ip = 0
        # stack for parse tree nodes aligned with grammar symbols (ignore '$')
        node_stack: List[ParseNode] = []
        widthPila = 30
        widthEntrada = 30
        widthAccion = 25
        # Human-readable row trace (still printed)
        trace_rows: List[Tuple[str, str, str]] = []
        # JSON-friendly structured trace for frontend tables
        json_trace: List[dict] = []
        print("\n=== Trazas LR(1) ===")
        print(f"{'Estados|Símbolos':<{widthPila}}{'Entrada':<{widthEntrada}}{'Acción':<{widthAccion}}")
        print('-' * (widthPila + widthEntrada + widthAccion))

        def pila_str() -> str:
            # Combine states and symbols for readability: (s0) X (s1) Y ...
            parts: List[str] = []
            parts.append(f"({state_stack[0]})")
            for i, sym in enumerate(symbol_stack):
                parts.append(sym)
                parts.append(f"({state_stack[i+1]})")
            return ' '.join(parts)

        while True:
            s = state_stack[-1]
            a = tokens[ip]
            act = self.lr1.ACTION.get((s, a))
            entrada_rest = ' '.join(tokens[ip:])

            if act is None:
                row = (pila_str(), entrada_rest, 'error')
                trace_rows.append(row)
                print(f"{row[0]:<{widthPila}}{row[1]:<{widthEntrada}}{row[2]:<{widthAccion}}")
                if collect_trace:
                    json_trace.append({
                        "stackStates": list(state_stack),
                        "stackSymbols": list(symbol_stack),
                        "stackDisplay": row[0],
                        "input": entrada_rest,
                        "action": {"type": "error", "state": s, "lookahead": a},
                    })
                print(f"[LR(1)] Error en estado {s} con lookahead '{a}'")
                self.last_trace = json_trace if collect_trace else None
                return False

            if act[0] == 'shift':
                t = act[1]
                row = (pila_str(), entrada_rest, 'shift ' + str(t))
                trace_rows.append(row)
                print(f"{row[0]:<{widthPila}}{row[1]:<{widthEntrada}}{row[2]:<{widthAccion}}")
                if collect_trace:
                    json_trace.append({
                        "stackStates": list(state_stack),
                        "stackSymbols": list(symbol_stack),
                        "stackDisplay": row[0],
                        "input": entrada_rest,
                        "action": {"type": "shift", "to": t, "symbol": a},
                    })
                symbol_stack.append(a)
                state_stack.append(t)
                ip += 1
                if a != '$':
                    node_stack.append(ParseNode(a, []))
            elif act[0] == 'reduce':
                prod: Production = act[1]
                beta = list(prod.rhs)
                row = (pila_str(), entrada_rest, 'reduce ' + str(prod))
                trace_rows.append(row)
                print(f"{row[0]:<{widthPila}}{row[1]:<{widthEntrada}}{row[2]:<{widthAccion}}")
                if collect_trace:
                    json_trace.append({
                        "stackStates": list(state_stack),
                        "stackSymbols": list(symbol_stack),
                        "stackDisplay": row[0],
                        "input": entrada_rest,
                        "action": {
                            "type": "reduce",
                            "production": {"lhs": prod.lhs, "rhs": list(prod.rhs), "text": str(prod)}
                        },
                    })
                # Pop |beta| symbols/states
                for _ in beta:
                    if not symbol_stack:
                        print('[LR(1)] Pila inconsistente durante reduce')
                        self.last_trace = json_trace if collect_trace else None
                        return False
                    symbol_stack.pop()
                    state_stack.pop()
                # Build parse tree node: pop |beta| nodes from node_stack
                children: List[ParseNode] = []
                for _ in beta:
                    # Only pop when beta had a symbol (term or nonterm). For epsilon, len(beta)==0
                    if node_stack:
                        children.append(node_stack.pop())
                children.reverse()
                node_stack.append(ParseNode(prod.lhs, children))
                # GOTO on lhs
                s = state_stack[-1]
                j = self.lr1.GOTO.get((s, prod.lhs))
                if j is None:
                    print(f"[LR(1)] GOTO indefinido para estado {s} con {prod.lhs}")
                    self.last_trace = json_trace if collect_trace else None
                    return False
                symbol_stack.append(prod.lhs)
                state_stack.append(j)
                # Extra trace row to show the GOTO destination state as a standalone action
                # (keeps the same input view; stack already reflects the goto)
                row2 = (pila_str(), entrada_rest, str(j))
                trace_rows.append(row2)
                print(f"{row2[0]:<{widthPila}}{row2[1]:<{widthEntrada}}{row2[2]:<{widthAccion}}")
                if collect_trace:
                    json_trace.append({
                        "stackStates": list(state_stack),
                        "stackSymbols": list(symbol_stack),
                        "stackDisplay": row2[0],
                        "input": entrada_rest,
                        "action": {"type": "goto", "to": j, "on": prod.lhs},
                    })
            elif act[0] == 'accept':
                row = (pila_str(), entrada_rest, 'accept')
                trace_rows.append(row)
                print(f"{row[0]:<{widthPila}}{row[1]:<{widthEntrada}}{row[2]:<{widthAccion}}")
                if collect_trace:
                    json_trace.append({
                        "stackStates": list(state_stack),
                        "stackSymbols": list(symbol_stack),
                        "stackDisplay": row[0],
                        "input": entrada_rest,
                        "action": {"type": "accept"},
                    })
                # The remaining node on node_stack should be the parse tree root
                root: Optional[ParseNode] = node_stack[-1] if node_stack else None
                self.last_tree = root
                self.last_trace = json_trace if collect_trace else None
                if root is not None and not collect_trace:
                    # In API mode (collect_trace=True) skip console tree printing.
                    # When printing on Windows consoles, fall back silently if Unicode can't be encoded.
                    try:
                        print("\nÁrbol de derivación (LR):")
                        for line in _render_ascii(root):
                            print(line)
                    except UnicodeEncodeError:
                        pass
                print("\n[LR(1)] Cadena aceptada")
                return True
            else:
                print(f"{pila_str():<{widthPila}}{entrada_rest:<{widthEntrada}}{'error':<{widthAccion}}")
                print(f"[LR(1)] Acción desconocida {act}")
                if collect_trace:
                    json_trace.append({
                        "stackStates": list(state_stack),
                        "stackSymbols": list(symbol_stack),
                        "stackDisplay": pila_str(),
                        "input": entrada_rest,
                        "action": {"type": "error", "detail": str(act)},
                    })
                self.last_trace = json_trace if collect_trace else None
                return False
