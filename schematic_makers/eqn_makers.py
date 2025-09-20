# Copyright (c) 2025 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""

"""

__author__ = "Kyle Vitautas Lopin"

import schemdraw
import schemdraw.logic as lg
import schemdraw.elements as elm

with schemdraw.Drawing() as d:
    # --- Inputs as short buses on the left ---
    Aline = d += elm.Line().right().at((0,  0)).length(2).label('A', 'left')
    Bline = d += elm.Line().right().at((0, -1)).length(2).label('B', 'left')
    Cline = d += elm.Line().right().at((0, -2)).length(2).label('C', 'left')

    # --- OR gate for (A + B) ---
    or1 = d += lg.Or().at((2.8, -0.5)).anchor('in1')   # 2-input OR by default
    d += elm.Line().at(Aline.end).to(or1.in1)
    d += elm.Line().at(Bline.end).to(or1.in2)

    # --- AND gate for (A + B) * C ---
    and1 = d += lg.And().at((6.0, -1.0)).anchor('in1')
    d += elm.Line().at(or1.out).to(and1.in1)
    d += elm.Line().at(Cline.end).to(and1.in2)

    # --- AND gate for (A * B) ---
    and2 = d += lg.And().at((3.2, -3.0)).anchor('in1')
    # Tap A down to and2.in1
    d += elm.Wire('|-').at((1.0,  0.0)).to((1.0, -3.1))
    d += elm.Wire('-|').at((1.0, -3.1)).to(and2.in1)
    # Tap B down to and2.in2
    d += elm.Wire('|-').at((1.6, -1.0)).to((1.6, -3.4))
    d += elm.Wire('-|').at((1.6, -3.4)).to(and2.in2)

    # --- NOT gate to make (A * B)' ---
    not1 = d += lg.Not().at((6.0, -3.0)).anchor('in')
    d += elm.Line().at(and2.out).to(not1.in)

    # --- Final OR: (A+B)*C + (A*B)' ---
    or2 = d += lg.Or().at((9.0, -2.0)).anchor('in1')
    d += elm.Line().at(and1.out).to(or2.in1)
    d += elm.Line().at(not1.out).to(or2.in2)

    # --- Output ---
    d += elm.Line().right().at(or2.out).length(1.5).label('F', 'right')

    d.draw()

