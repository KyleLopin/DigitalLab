# Copyright (c) 2025 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""

"""

__author__ = "Kyle Vitautas Lopin"


import schemdraw as sd
from schemdraw.elements import intcircuits as ic, lines, elements as elm


class Mux4(ic.Multiplexer):
    def __init__(self, **kwargs):
        super().__init__(
            pins=[
                ic.IcPin(name='D3', side='L'),
                ic.IcPin(name='D2', side='L'),
                ic.IcPin(name='D1', side='L'),
                ic.IcPin(name='D0', side='L'),
                ic.IcPin(name='Q',  side='R'),
                ic.IcPin(name='S0', side='B'),
                ic.IcPin(name='S1', side='B'),
                # ic.IcPin(name='EN', side='T', invert=True),
            ],
            edgepadH=-.5,
            pinspacing=0.8,
            size=(2.6, 3.4),
            **kwargs
        )


with sd.Drawing() as d:

    ffs = []
    muxs = []
    n = 4
    seg=None
    for i in range(n):
        if seg:
            ff = d.add(ic.DFlipFlop(size=(3,4), preclr=True,
                                    preclrinvert=False).anchor('D').at(seg.end))
        else:
            ff = d.add(ic.DFlipFlop(size=(3,4), preclr=True,
                                    preclrinvert=False))
        ffs.append(ff)
        d.add(lines.Line().at(ffs[i].Q).right(d.unit/4))
        d.add(lines.Line().up(d.unit))
        seg = d.add(lines.Line().right(d.unit / 4))
        mux = d.add(Mux4(inputs=4).anchor('D3').at(seg.end).scale(0.7))
        muxs.append(mux)
        d.add(lines.Line().right(d.unit / 4).at(mux.Q))
        d.add(lines.Line().down().toy(ff.Q))
        seg = d.add(lines.Line().right(d.unit / 4))

    # add clock line
    for ff in ffs:
        d.add(lines.Line().down(d.unit / 2).at(ff.CLK))
    d.add(lines.Line().left().tox(ffs[0].CLK))
    d.add(lines.Line().left().label("CLK", loc="left"))

    # add select lines
    for mux in muxs:
        d.add(lines.Line().down(d.unit/4).at(mux.S0).dot())
        # d.add(elm.Node())
    d.add(lines.Line().left().tox(muxs[0].S0))
    d.add(lines.Line().left(d.unit * 3).label("S0", loc="left"))
    for mux in muxs:
        d.add(lines.Line().down(d.unit / 6).at(mux.S1).dot())
    d.add(lines.Line().left().tox(muxs[0].S1))
    d.add(lines.Line().left(d.unit * 3.2).label("S1", loc="left"))

    d.show()

    n = 4
    x0, y0 = 0, 0
    dy = -3.5
    ffs = []

    # Place 4 DFFs vertically (Q3 at top)
    for i in range(n):
        ff = d.add(ic.DFlipFlop(size=(2,3)).at((x0, y0 + i*dy)))
        ffs.append(ff)
        # Label Q[i]
        d.add(lines.Line().at(ff.Q).to((ff.Q[0]+1.0, ff.Q[1])))
        d.add(elm.Label('Q').at((ff.Q[0]+1.2, ff.Q[1])))

    print(ffs)
    # MUX & Data wiring per bit
    for i, ff in enumerate(ffs):
        mux = d.add(ic.Multiplexer().at((ff.D[0]-1.7, ff.D[1]))).right()
        # Upper input = DATA[i]
        d.add(lines.Line().at((mux.in0[0]-1.0, mux.in0[1])).to(mux.in0))
        d.add(elm.Label().at((mux.in0[0]-1.2, mux.in0[1])).label(f'DATA{i}'))
        # Lower input = HOLD path (Q[i] feedback)
        d.add(lines.Line().at(ff.Q).to((mux.in1[0]-0.2, ff.Q[1])))
        d.add(lines.Line().at((mux.in1[0]-0.2, ff.Q[1])).to(mux.in1))
        # Select = LOAD
        d.add(lines.Line().at((mux.sel[0], mux.sel[1]-0.9)).to(mux.sel))
        d.add(elm.Label().at((mux.sel[0], mux.sel[1]-1.1)).label('LOAD'))
        # MUX out to D
        d.add(lines.Line().at(mux.out).to(ff.D))

    # Clock bus (left side)
    bus_y = ffs[0].CLK[1] - 1.0
    for ff in ffs:
        d.add(lines.Line().at(ff.CLK).to((ff.CLK[0]-0.6, ff.CLK[1])))
        d.add(lines.Line().at((ff.CLK[0]-0.6, ff.CLK[1])).to((ff.CLK[0]-0.6, bus_y)))
    d.add(lines.Line().at((ffs[-1].CLK[0]-0.6, bus_y)).to((ffs[0].CLK[0]-1.5, bus_y)))
    d.add(elm.Label().at((ffs[0].CLK[0]-1.7, bus_y)).label('CLK'))

    d.save('register_test.svg')
