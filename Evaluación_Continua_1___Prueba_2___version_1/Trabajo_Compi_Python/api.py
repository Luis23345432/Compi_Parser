from __future__ import annotations
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# dual imports
if __package__ is None or __package__ == "":
    from grammar import Grammar
    from lr1 import LR1Builder
    from lr_parser import LRParser, ParseNode, _render_ascii
else:
    from .grammar import Grammar
    from .lr1 import LR1Builder
    from .lr_parser import LRParser, ParseNode, _render_ascii

app = FastAPI(title="LR(1) Parser API")


# Enable CORS so a frontend (running on a different origin) can call this API.
# By default this allows all origins. For production, restrict `allow_origins`
# to a list of trusted origins like ["https://example.com"] or read from env.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class GrammarRequest(BaseModel):
    grammar: str  # raw grammar text, lines like: S -> C C\nC -> c C\nC -> d


class ParseRequest(BaseModel):
    grammar: str
    input: str  # tokens separated by spaces


def build_lr1_from_text(grammar_text: str):
    g = Grammar()
    if not g.load_from_string(grammar_text):
        raise HTTPException(status_code=400, detail="No se pudo cargar la gramática.")
    lr1 = LR1Builder(g)
    lr1.build_canonical_collection()
    lr1.build_tables()
    return g, lr1


def serialize_states(lr1: LR1Builder) -> List[Dict[str, Any]]:
    out = []
    for st in lr1.states:
        items = []
        for it in sorted(st.items, key=lambda x: (x.lhs, x.rhs, x.dot, x.la)):
            items.append({
                "lhs": it.lhs,
                "rhs": list(it.rhs),
                "dot": it.dot,
                "lookahead": it.la,
                "text": str(it),
            })
        transitions = []
        for (sid, sym), to in lr1.transitions.items():
            if sid == st.id:
                transitions.append({"symbol": sym, "to": to})
        out.append({
            "id": st.id,
            "items": items,
            "transitions": sorted(transitions, key=lambda x: x["symbol"]),
        })
    return out


def serialize_closure_table(lr1: LR1Builder) -> List[Dict[str, Any]]:
    """Return a serializable closure table suitable for frontend display.

    Each entry contains:
      - id: state id
      - kernel: list of item dicts (items that form the kernel)
      - closure: full closure as list of item dicts
      - transitions: outgoing transitions from this state as list of {symbol, to}
    """
    table: List[Dict[str, Any]] = []
    for st in lr1.states:
        # full closure: all items in the state
        closure_items = sorted(st.items, key=lambda x: (x.lhs, x.rhs, x.dot, x.la))
        # kernel: items with dot > 0 or the augmented start production
        try:
            aug_start = lr1.aug_start
        except Exception:
            aug_start = None
        kernel_items = [it for it in closure_items if it.dot > 0 or (aug_start is not None and it.lhs == aug_start)]

        def item_to_dict(it: LR1Item) -> Dict[str, Any]:
            return {
                "lhs": it.lhs,
                "rhs": list(it.rhs),
                "dot": it.dot,
                "lookahead": it.la,
                "text": str(it),
            }

        transitions = []
        for (sid, sym), to in lr1.transitions.items():
            if sid == st.id:
                transitions.append({"symbol": sym, "to": to})

        table.append({
            "id": st.id,
            "kernel": [item_to_dict(it) for it in kernel_items],
            "closure": [item_to_dict(it) for it in closure_items],
            "transitions": sorted(transitions, key=lambda x: x["symbol"]),
        })
    return table


def serialize_tables(lr1: LR1Builder) -> Dict[str, Any]:
    terms = sorted(list(lr1.grammar.terminals))
    nts = sorted(list(lr1.grammar.nonTerminals))
    action = {}
    for (s, a), act in lr1.ACTION.items():
        if str(s) not in action:
            action[str(s)] = {}
        if act[0] == 'shift':
            val = {"type": "shift", "to": act[1]}
        elif act[0] == 'reduce':
            prod = act[1]
            val = {"type": "reduce", "lhs": prod.lhs, "rhs": list(prod.rhs), "text": str(prod)}
        elif act[0] == 'accept':
            val = {"type": "accept"}
        else:
            val = {"type": "error"}
        action[str(s)][a] = val
    goto = {}
    for (s, A), j in lr1.GOTO.items():
        if str(s) not in goto:
            goto[str(s)] = {}
        goto[str(s)][A] = j
    return {"terminals": terms, "nonterminals": nts, "action": action, "goto": goto}


def render_tree_ascii(node: Optional[ParseNode]) -> Optional[str]:
    if node is None:
        return None
    return "\n".join(_render_ascii(node))


def tree_to_json(node: Optional[ParseNode]) -> Optional[Dict[str, Any]]:
    if node is None:
        return None
    return {
        "label": node.label,
        "children": [tree_to_json(ch) for ch in node.children] if node.children else []
    }


@app.post("/build")
def build(req: GrammarRequest):
    g, lr1 = build_lr1_from_text(req.grammar)
    return {
        "initial": g.initialState,
        "terminals": sorted(list(g.terminals)),
        "nonterminals": sorted(list(g.nonTerminals)),
        "rules": g.rules,
        "states": serialize_states(lr1),
        "closure_table": serialize_closure_table(lr1),
        "tables": serialize_tables(lr1),
        "conflicts": lr1.conflicts,
    }


@app.post("/parse")
def parse(req: ParseRequest):
    g, lr1 = build_lr1_from_text(req.grammar)
    tokens = req.input.split()
    parser = LRParser(lr1)
    accepted = parser.parse(tokens, collect_trace=True)
    return {
        "accepted": accepted,
        # Structured trace suitable for a frontend table. Each step has stack and action info.
        "trace": parser.last_trace,
        # JSON tree for UI rendering; keep ASCII version as convenience.
        "tree": tree_to_json(parser.last_tree),
        "tree_ascii": render_tree_ascii(parser.last_tree),
    }


# For uvicorn: uvicorn Trabajo_Compi_Python.api:app --reload
