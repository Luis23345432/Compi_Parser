from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Set, Tuple, Iterable

# Dual-imports to support running as script or module
if __package__ is None or __package__ == "":
    from grammar import Grammar
    from first import First
    from utils import trim, split
else:
    from .grammar import Grammar
    from .first import First
    from .utils import trim, split


@dataclass(frozen=True)
class Production:
    lhs: str
    rhs: Tuple[str, ...]  # empty tuple for epsilon
    def __str__(self) -> str:
        if not self.rhs:
            return f"{self.lhs} -> ''"
        return f"{self.lhs} -> {' '.join(self.rhs)}"


@dataclass(frozen=True)
class LR1Item:
    lhs: str
    rhs: Tuple[str, ...]
    dot: int
    la: str  # lookahead terminal
    def __str__(self) -> str:
        parts = list(self.rhs)
        parts.insert(self.dot, '·')
        rhs_str = ' '.join(parts) if parts else '·'
        return f"[{self.lhs} -> {rhs_str}, {self.la}]"


class LR1State:
    def __init__(self, items: Iterable[LR1Item], sid: int = -1) -> None:
        self.id = sid
        self.items: Set[LR1Item] = set(items)
    def __iter__(self):
        return iter(self.items)
    def __len__(self):
        return len(self.items)
    def __eq__(self, other: object) -> bool:
        return isinstance(other, LR1State) and self.items == other.items
    def __hash__(self) -> int:
        # Hash by frozenset of items
        return hash(frozenset(self.items))
    def pretty(self) -> str:
        lines = [f"State I{self.id}:"]
        for it in sorted(self.items, key=lambda x: (x.lhs, x.rhs, x.dot, x.la)):
            lines.append(f"  {it}")
        return '\n'.join(lines)


class LR1Builder:
    def __init__(self, grammar: Grammar) -> None:
        self.grammar = grammar
        self.first = First(grammar)
        self.first.compute()

        # Build production list (including augmented start)
        self.start_symbol = grammar.initialState
        self.aug_start = self.start_symbol + "'"
        while self.aug_start in grammar.nonTerminals:
            self.aug_start += "'"

        # Build structured productions
        self.productions: List[Production] = []
        self._build_productions()

        # Canonical collection
        self.states: List[LR1State] = []
        self.transitions: Dict[Tuple[int, str], int] = {}

        # Parsing tables
        self.ACTION: Dict[Tuple[int, str], Tuple[str, object]] = {}
        self.GOTO: Dict[Tuple[int, str], int] = {}
        self.conflicts: List[str] = []

    # -------------------- helpers --------------------
    def _build_productions(self) -> None:
        # Augmented production: S' -> S
        self.productions.append(Production(self.aug_start, (self.start_symbol,)))
        # Parse grammar rules
        for rule in self.grammar.rules:
            pos = rule.find('->')
            if pos == -1:
                continue
            lhs = trim(rule[:pos])
            rhs = trim(rule[pos+2:])
            alts = [trim(a) for a in rhs.split('|')]
            for alt in alts:
                if alt == '' or alt == "''" or alt == 'ε':
                    self.productions.append(Production(lhs, tuple()))
                else:
                    symbols = tuple(s for s in alt.split(' ') if s)
                    self.productions.append(Production(lhs, symbols))

    def _is_nonterminal(self, sym: str) -> bool:
        return sym in self.grammar.nonTerminals or sym == self.aug_start

    def first_of_sequence(self, seq: List[str], lookahead: str) -> Set[str]:
        # Compute FIRST(seq · lookahead)
        result: Set[str] = set()
        if not seq:
            result.add(lookahead)
            return result
        for s in seq:
            if s == "''":
                continue
            # terminal
            if (s in self.grammar.terminals) and (s not in self.grammar.nonTerminals):
                result.add(s)
                return result
            # non-terminal
            if self._is_nonterminal(s):
                fset = self.first.firstSets.get(s, set())
                result.update(x for x in fset if x != "''")
                if "''" not in fset:
                    return result
            else:
                # unknown symbol: treat as terminal
                result.add(s)
                return result
        # all nullable
        result.add(lookahead)
        return result

    # -------------------- closure/goto --------------------
    def closure(self, items: Iterable[LR1Item]) -> Set[LR1Item]:
        I: Set[LR1Item] = set(items)
        changed = True
        while changed:
            changed = False
            new_items: Set[LR1Item] = set()
            for it in I:
                # if dot before a nonterminal B
                if it.dot < len(it.rhs):
                    B = it.rhs[it.dot]
                    if self._is_nonterminal(B):
                        beta = list(it.rhs[it.dot+1:])
                        lookaheads = self.first_of_sequence(beta, it.la)
                        for prod in self.productions:
                            if prod.lhs == B:
                                for a in lookaheads:
                                    cand = LR1Item(B, prod.rhs, 0, a)
                                    if cand not in I:
                                        new_items.add(cand)
            if new_items:
                before = len(I)
                I.update(new_items)
                if len(I) > before:
                    changed = True
        return I

    def goto(self, items: Iterable[LR1Item], X: str) -> Set[LR1Item]:
        moved: Set[LR1Item] = set()
        for it in items:
            if it.dot < len(it.rhs) and it.rhs[it.dot] == X:
                moved.add(LR1Item(it.lhs, it.rhs, it.dot+1, it.la))
        if not moved:
            return set()
        return self.closure(moved)

    # -------------------- canonical collection --------------------
    def build_canonical_collection(self) -> None:
        I0 = self.closure({LR1Item(self.aug_start, (self.start_symbol,), 0, '$')})
        states: List[LR1State] = []
        state_map: Dict[frozenset, int] = {}

        def get_state_id(itemset: Set[LR1Item]) -> int:
            key = frozenset(itemset)
            if key in state_map:
                return state_map[key]
            sid = len(states)
            st = LR1State(itemset, sid)
            states.append(st)
            state_map[key] = sid
            return sid

        worklist: List[int] = []
        s0 = get_state_id(I0)
        worklist.append(s0)

        all_symbols = sorted(list(self.grammar.nonTerminals | self.grammar.terminals | {self.aug_start}))

        while worklist:
            sid = worklist.pop()
            I = states[sid].items
            for X in all_symbols:
                J = self.goto(I, X)
                if not J:
                    continue
                jid = get_state_id(J)
                if (sid, X) not in self.transitions:
                    self.transitions[(sid, X)] = jid
                if jid >= len(states) - 1:  # newly created
                    worklist.append(jid)

        # assign final
        self.states = states

    # -------------------- tables --------------------
    def build_tables(self) -> None:
        if not self.states:
            self.build_canonical_collection()

        terminals = set(self.grammar.terminals)
        nonterminals = set(self.grammar.nonTerminals)
        nonterminals.add(self.aug_start)

        for state in self.states:
            sid = state.id
            # shifts
            for (s, X), jid in self.transitions.items():
                if s != sid:
                    continue
                if X in terminals:
                    self._set_action(sid, X, ("shift", jid))
                elif X in nonterminals:
                    if X != self.aug_start:
                        self.GOTO[(sid, X)] = jid
            # reduces/accept
            for it in state.items:
                if it.dot == len(it.rhs):
                    if it.lhs == self.aug_start and it.la == '$':
                        self._set_action(sid, '$', ("accept", None))
                    else:
                        prod = Production(it.lhs, it.rhs)
                        self._set_action(sid, it.la, ("reduce", prod))

    def _set_action(self, sid: int, a: str, action: Tuple[str, object]) -> None:
        key = (sid, a)
        if key in self.ACTION and self.ACTION[key] != action:
            prev = self.ACTION[key]
            msg = f"[Conflict] state {sid}, lookahead '{a}': existing {prev}, new {action}"
            self.conflicts.append(msg)
        else:
            self.ACTION[key] = action

    # -------------------- printing --------------------
    def print_states(self) -> None:
        for st in self.states:
            print(st.pretty())
            # outgoing transitions
            outs = [(sym, self.transitions[(st.id, sym)]) for (sid, sym) in self.transitions if sid == st.id]
            for sym, to in sorted(outs, key=lambda x: x[0]):
                print(f"  on '{sym}' -> I{to}")
            print()

    def print_tables(self) -> None:
        # Print ACTION table
        terms = sorted([t for t in self.grammar.terminals])
        nts = sorted([nt for nt in self.grammar.nonTerminals])
        print("=== ACTION table ===")
        header = ["st"] + terms
        print(' '.join(f"{h:>12}" for h in header))
        print('-' * (13 * len(header)))
        for st in self.states:
            row = [f"{st.id:>12}"]
            for a in terms:
                act = self.ACTION.get((st.id, a))
                if not act:
                    cell = ''
                elif act[0] == 'shift':
                    cell = f"s{act[1]}"
                elif act[0] == 'reduce':
                    cell = f"r({act[1]})"
                elif act[0] == 'accept':
                    cell = 'acc'
                else:
                    cell = ''
                row.append(f"{cell:>12}")
            print(' '.join(row))
        print()
        print("=== GOTO table ===")
        header = ["st"] + nts
        print(' '.join(f"{h:>12}" for h in header))
        print('-' * (13 * len(header)))
        for st in self.states:
            row = [f"{st.id:>12}"]
            for A in nts:
                j = self.GOTO.get((st.id, A))
                row.append(f"{(j if j is not None else ''):>12}")
            print(' '.join(row))
        print()
        if self.conflicts:
            print("=== Conflicts ===")
            for c in self.conflicts:
                print(c)
            print()

    def print_closure_table(self) -> None:
        """Print a human-readable LR(1) closure table to the console.

        The output lists for each state its kernel, state id, full closure and
        outgoing transitions (goto). This is intended for console inspection
        and resembles the closure table in the project README/image.
        """
        print("\nLR(1) closure table")
        print("{:^20} | {:^40} | {:^6} | {:^60}".format('Goto', 'Kernel', 'State', 'Closure'))
        print('-' * 140)
        for st in self.states:
            # sorted lists for deterministic output
            closure_items = sorted(st.items, key=lambda x: (x.lhs, x.rhs, x.dot, x.la))
            aug_start = getattr(self, 'aug_start', None)
            kernel_items = [it for it in closure_items if it.dot > 0 or (aug_start is not None and it.lhs == aug_start)]

            kernel_text = ', '.join(str(it) for it in kernel_items)
            closure_text = ', '.join(str(it) for it in closure_items)

            # find outgoing transitions from this state
            outs = [(sym, self.transitions[(st.id, sym)]) for (sid, sym) in self.transitions if sid == st.id]
            if not outs:
                # single row with empty Goto column
                print("{:20} | {:40} | {:6} | {:60}".format('', kernel_text, st.id, closure_text))
            else:
                # print one row per outgoing transition, repeating kernel/closure for readability
                for i, (sym, to) in enumerate(sorted(outs, key=lambda x: x[0])):
                    goto_text = f"goto({st.id}, {sym})"
                    print("{:20} | {:40} | {:6} | {:60}".format(goto_text, kernel_text, st.id, closure_text))
        print()
