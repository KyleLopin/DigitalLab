# Copyright (c) 2025 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""

"""

__author__ = "Kyle Vitautas Lopin"

# bool2schemdraw.py
# Render unsimplified Boolean expressions to Schemdraw logic schematics.
# Supported ops: NOT:  !A, ~A, A' ; AND: A&B or A*B ; OR: A|B or A+B ; XOR: A^B ; parentheses

from dataclasses import dataclass
from typing import List, Tuple, Union
import re
import random

import schemdraw
from schemdraw import Drawing
from schemdraw import elements as elm
from schemdraw.logic import And, Or, Not, Xor, Buf

# ---------------------------
# 1) Tokenizer & AST classes
# ---------------------------

TOK_VAR   = 'VAR'   # variable names: A, B1, X_2, etc.
TOK_LPAR  = '('
TOK_RPAR  = ')'
TOK_NOT   = 'NOT'   # !, ~, or postfix '
TOK_AND   = 'AND'   # &, *
TOK_OR    = 'OR'    # |, +
TOK_XOR   = 'XOR'   # ^
TOK_END   = 'END'

_token_spec = [
    (TOK_VAR,  r"[A-Za-z]\w*"),
    (TOK_NOT,  r"[!~]"),
    (TOK_AND,  r"[&*]"),
    (TOK_OR,   r"[|+]"),
    (TOK_XOR,  r"\^"),
    (TOK_LPAR, r"\("),
    (TOK_RPAR, r"\)"),
    ('SKIP',   r"[ \t\r\n]+"),
    ('MISC',   r"."),
]

tok_re = re.compile("|".join(f"(?P<{name}>{pat})" for name, pat in _token_spec))

@dataclass
class Tok:
    type: str
    value: str

def tokenize(s: str) -> List[Tok]:
    tokens = []
    i = 0
    while i < len(s):
        m = tok_re.match(s, i)
        if not m:
            raise ValueError(f"Unexpected character at {i}")
        typ = m.lastgroup
        val = m.group(typ)
        i = m.end()
        if typ == 'SKIP':
            continue
        if typ == 'MISC':
            if val == "'":
                tokens.append(Tok(TOK_NOT, val))  # postfix NOT
            else:
                raise ValueError(f"Unsupported char: {val}")
        else:
            tokens.append(Tok(typ, val))
    tokens.append(Tok(TOK_END, ''))
    return tokens

# AST
@dataclass
class Node: pass

@dataclass
class Var(Node):
    name: str
    inv: bool = False  # if it came with postfix ', we convert to NOT(Var)

@dataclass
class Unary(Node):
    op: str   # 'NOT'
    child: Node

@dataclass
class Binary(Node):
    op: str   # 'AND'|'OR'|'XOR'
    left: Node
    right: Node

# ---------------------------
# 2) Recursive-descent parser
#    Precedence: NOT > AND > XOR > OR
# ---------------------------

class Parser:
    def __init__(self, tokens: List[Tok]):
        self.toks = tokens
        self.i = 0

    def cur(self) -> Tok:
        return self.toks[self.i]

    def eat(self, ttype=None) -> Tok:
        tok = self.cur()
        if ttype and tok.type != ttype:
            raise ValueError(f"Expected {ttype}, got {tok.type}")
        self.i += 1
        return tok

    def parse(self) -> Node:
        node = self.parse_or()
        if self.cur().type != TOK_END:
            raise ValueError("Trailing tokens")
        return node

    def parse_or(self) -> Node:
        node = self.parse_xor()
        while self.cur().type == TOK_OR:
            self.eat()
            node = Binary('OR', node, self.parse_xor())
        return node

    def parse_xor(self) -> Node:
        node = self.parse_and()
        while self.cur().type == TOK_XOR:
            self.eat()
            node = Binary('XOR', node, self.parse_and())
        return node

    def parse_and(self) -> Node:
        node = self.parse_not()
        while self.cur().type == TOK_AND:
            self.eat()
            node = Binary('AND', node, self.parse_not())
        return node

    def parse_not(self) -> Node:
        # prefix NOTs
        if self.cur().type == TOK_NOT:
            self.eat()
            return Unary('NOT', self.parse_not())
        # primary
        node = self.parse_primary()
        # postfix ' (handled by tokenizer as NOT)
        while self.cur().type == TOK_NOT:
            self.eat()
            node = Unary('NOT', node)
        return node

    def parse_primary(self) -> Node:
        t = self.cur()
        if t.type == TOK_LPAR:
            self.eat(TOK_LPAR)
            node = self.parse_or()
            self.eat(TOK_RPAR)
            return node
        if t.type == TOK_VAR:
            name = self.eat(TOK_VAR).value
            return Var(name)
        raise ValueError(f"Unexpected token {t.type}")

def parse_expr(s: str) -> Node:
    return Parser(tokenize(s)).parse()

# ---------------------------
# 3) Tree layout & drawing
# ---------------------------

# We’ll draw each node as a gate placed at (x_offset, y_center).
# Children are stacked vertically with a fixed spacing.
X_STEP = 3.0
Y_STEP = 2.0

@dataclass
class DrawResult:
    out_anchor: elm.Element
    leaves: List[str]  # variable names seen (for labeling and reference)

def subtree_height(node: Node) -> int:
    if isinstance(node, Var):
        return 1
    if isinstance(node, Unary):
        return subtree_height(node.child)
    if isinstance(node, Binary):
        return subtree_height(node.left) + subtree_height(node.right)
    return 1

def draw_node(d: Drawing, node: Node, x: float, y: float) -> DrawResult:
    """Draw node with center at (x,y). Returns output anchor and leaves list."""
    if isinstance(node, Var):
        # Input wire with label
        inp = d.add(elm.Dot().at((x, y)))
        w = d.add(elm.Line().right(1.0).at((x, y)))
        d.add(elm.Label().at((x-0.3, y)).label(node.name, loc='left'))
        out_anchor = w.end
        return DrawResult(out_anchor, [node.name])

    if isinstance(node, Unary) and node.op == 'NOT':
        # Draw child first to the left
        h = subtree_height(node.child)
        child_y = y
        child = draw_node(d, node.child, x - X_STEP, child_y)
        g = d.add(Not().at(child.out_anchor).anchor('in'))
        return DrawResult(g.out, child.leaves)

    if isinstance(node, Binary):
        # Compute child heights to stack
        hl = subtree_height(node.left)
        hr = subtree_height(node.right)
        top_y = y + (hl - 0.5) * (Y_STEP / 1.0)
        # Left child
        left = draw_node(d, node.left, x - X_STEP, top_y)
        # Right child
        right = draw_node(d, node.right, x - X_STEP, top_y - hl * (Y_STEP / 1.0))
        # Gate type
        if node.op == 'AND':
            gate = And(inputs=2)
        elif node.op == 'OR':
            gate = Or(inputs=2)
        elif node.op == 'XOR':
            gate = Xor(inputs=2)
        else:
            raise ValueError(f"Unsupported op {node.op}")
        g = d.add(gate.at((x, y)))
        # Connect inputs
        d.add(elm.Line().at(left.out_anchor).to(g.in1))
        d.add(elm.Line().at(right.out_anchor).to(g.in2))
        return DrawResult(g.out, left.leaves + right.leaves)

    # Fallback (shouldn’t happen)
    b = d.add(Buf().at((x, y)))
    return DrawResult(b.out, [])

def draw_expression(expr: str, outfile: str = "circuit.svg"):
    """
    Draws the boolean expression as a gate schematic.
    Example operators:
      A & (B | C') ^ ~D   OR   (A + B)*(C' + D)   OR   !A & B ^ (C + D')
    """
    ast = parse_expr(expr)

    with schemdraw.Drawing(file=outfile, show=False) as d:
        d.config(unit=1.0)  # keep scale consistent
        height = subtree_height(ast)
        center_y = 0
        res = draw_node(d, ast, x=0, y=center_y)
        # Output label
        d.add(elm.Line().at(res.out_anchor).right(1.0))
        d.add(elm.Dot().at((res.out_anchor[0] + 1.0, res.out_anchor[1])))
        d.add(elm.Label().at((res.out_anchor[0] + 1.2, res.out_anchor[1])).label('OUT', loc='right'))

    print(f"Wrote {outfile}")

# ---------------------------
# 4) Random unsimplified expression generator
# ---------------------------

OPS_BIN = ['AND', 'OR', 'XOR']

def random_expr(variables=('A','B','C','D','E'), max_depth=3, p_unary=0.25) -> Node:
    if max_depth <= 0 or (max_depth == 1 and random.random() < 0.6):
        v = Var(random.choice(variables))
        # random postfix inversion chance
        if random.random() < 0.3:
            return Unary('NOT', v)
        return v
    # sometimes make a NOT chain
    if random.random() < p_unary:
        return Unary('NOT', random_expr(variables, max_depth-1, p_unary))
    # binary
    op = random.choice(OPS_BIN)
    left = random_expr(variables, max_depth-1, p_unary)
    right = random_expr(variables, max_depth-1, p_unary)
    return Binary(op, left, right)

def ast_to_str(n: Node) -> str:
    if isinstance(n, Var):
        return n.name
    if isinstance(n, Unary):
        return f"!({ast_to_str(n.child)})"
    if isinstance(n, Binary):
        op = {'AND':'&','OR':'|','XOR':'^'}[n.op]
        return f"({ast_to_str(n.left)} {op} {ast_to_str(n.right)})"
    return "?"

if __name__ == "__main__":
    # Example 1: explicit expression -> SVG
    expr = "A & (B | C') ^ ~D"
    draw_expression(expr, "example1.svg")

    # Example 2: random unsimplified circuit
    random.seed(7)
    r = random_expr(variables=('A','B','C','D'), max_depth=3, p_unary=0.35)
    s = ast_to_str(r)
    print("Random expression:", s)
    draw_expression(s, "random_example.svg")

