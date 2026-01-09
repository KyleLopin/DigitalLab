# Copyright (c) 2025 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""

"""

__author__ = "Kyle Vitautas Lopin"

# pip install schemdraw==0.15
import schemdraw
import schemdraw.elements as elm
from schemdraw.logic import And, Or, Not

with schemdraw.Drawing(file='images/logic_expr.svg') as d:
    d.config(fontsize=12)
    # --- Inputs ---
    A = d.add(elm.Dot(open=True).label('A', 'left')).left()
    d.move_from(A, 0, -1.0)
    B = d.add(elm.Dot(open=True).label('B', 'left')).left()
    d.move_from(B, 0, -1.0)
    C = d.add(elm.Dot(open=True).label('C', 'left')).left()

    # Space to the right for logic
    d += elm.Line().right(1.2).at(A)
    d += elm.Line().right(1.2).at(B)
    d += elm.Line().right(1.2).at(C)

    # --- Inverters for complements ---
    Ainv = d.add(Not().at(A.end).anchor('in'))
    Binv = d.add(Not().at(B.end).anchor('in'))
    Cinv = d.add(Not().at(C.end).anchor('in'))

    # --- Term T1 = A(B' + C') ---
    # OR of B' and C', then AND with A
    # Tap outputs of Binv, Cinv
    d.move_from(Binv, 1.2, 0.6)
    or1 = d.add(Or(inputs=2).anchor('in1'))
    d += elm.Line().at(Binv.out).to(or1.in1)
    d += elm.Line().at(Cinv.out).to(or1.in2)

    # AND with A
    d.move_from(or1, 1.4, 0)
    and1 = d.add(And(inputs=2).anchor('in1'))
    # route A (non-inverted) to and1.in1
    d += elm.Line().at(A.out).to(and1.in1)
    # route OR output to and1.in2
    d += elm.Line().at(or1.out).to(and1.in2)
    T1 = and1

    # --- Term T2 = BC' ---
    d.move_from(Cinv, 1.6, -0.2)
    and2 = d.add(And(inputs=2).anchor('in1'))
    d += elm.Line().at(B.out).to(and2.in1)
    d += elm.Line().at(Cinv.out).to(and2.in2)
    T2 = and2

    # --- Term T3 = AB ---
    d.move_from(B, 1.6, -1.2)
    and3 = d.add(And(inputs=2).anchor('in1'))
    d += elm.Line().at(A.out).to(and3.in1)
    d += elm.Line().at(B.out).to(and3.in2)
    T3 = and3

    # --- Term T4 = A'B ---
    d.move_from(Binv, 1.6, -1.8)
    and4 = d.add(And(inputs=2).anchor('in1'))
    d += elm.Line().at(Ainv.out).to(and4.in1)
    d += elm.Line().at(B.out).to(and4.in2)
    T4 = and4

    # --- Final OR (4 inputs) ---
    # Stack outputs to a 4-input OR
    max_x = max(T1.out.x, T2.out.x, T3.out.x, T4.out.x)
    d += elm.Line().at(T1.out).to((max_x, T1.out.y))
    d += elm.Line().at(T2.out).to((max_x, T2.out.y))
    d += elm.Line().at(T3.out).to((max_x, T3.out.y))
    d += elm.Line().at(T4.out).to((max_x, T4.out.y))

    d.move_from((max_x + 0.8, (T1.out.y + T4.out.y)/2), 0, 0)
    or_final = d.add(Or(inputs=4).anchor('out'))
    d += elm.Line().at((max_x, T1.out.y)).to(or_final.in1)
    d += elm.Line().at((max_x, T2.out.y)).to(or_final.in2)
    d += elm.Line().at((max_x, T3.out.y)).to(or_final.in3)
    d += elm.Line().at((max_x, T4.out.y)).to(or_final.in4)

    # Output node
    d += elm.Line().right(1.0).at(or_final.out)
    d += elm.Dot().label('Y', 'right')

# Also save PNG (optional)
schemdraw.Drawing('logic_expr.png')

