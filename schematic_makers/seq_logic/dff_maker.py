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
                ic.IcPin(name='S', side='B'),
                # ic.IcPin(name='S1', side='B'),
                # ic.IcPin(name='EN', side='T', invert=True),
            ],
            edgepadH=-.5,
            pinspacing=1.1,
            size=(3.2, 4.2),
            **kwargs
        )


class DFF_EN_RST(ic.Ic):
    def __init__(self, **kwargs):
        super().__init__(
            pins=[
                ic.IcPin('D','L'),
                ic.IcPin('Q','R'),
                ic.IcPin('CLK','T'),
                ic.IcPin('EN','B'),
                ic.IcPin('RST','B', invert=True),  # active-low bubble; drop invert=False if active-high
            ],
            pinspacing=1.2, edgepadH=-.3, size=(2.6,3.0), **kwargs
        )


with sd.Drawing() as d:

    ffs = []
    muxs = []
    n = 4
    seg=None
    for i in range(n):
        print(i)
        if seg:
            # ff = d.add(ic.DFlipFlop(size=(3,4), preclr=True,
            #                         preclrinvert=False).anchor('D').at(seg.end))
            mux = d.add(Mux4(inputs=4).anchor('D3').at(seg.end).right().scale(0.7))
            d.add(lines.Line().right(d.unit * 0.2).at(mux.Q))
        else:
            seg = d.add(lines.Line().right(d.unit * 0.2).label(r"$D_{in}$", loc="left"))
            mux = d.add(Mux4(inputs=4).right().anchor('D3').at(seg.end).scale(0.7))
            d.add(lines.Line().right(d.unit * 0.2).at(mux.Q))

        muxs.append(mux)
        d.add(lines.Line().down(d.unit * 1.7))
        seg = d.add(lines.Line().right(d.unit * 0.2))
        ff = d.add(ic.DFlipFlop(size=(3,4), preclr=True,
                                preclrinvert=False).anchor('D').at(seg.end))
        ffs.append(ff)
        # seg = d.add(lines.Line().right(d.unit / 4))


        d.add(lines.Line().at(ffs[i].Q).dot().right(d.unit/4).label(fr"$Q_{n-i-1}$", loc='right'))
        d.add(lines.Line().toy(mux.D3).dot())
        d.push()
        # d.show()
        d.add(lines.Line().toy(mux.D0))
        d.add(lines.Line().up(d.unit*0.7))
        d.add(lines.Line().tox(mux.D1))
        d.add(lines.Line().left(d.unit*0.3))
        d.add(lines.Line().toy(mux.D0))
        d.add(lines.Line().tox(mux.D0))
        d.pop()
        if i < n-1:
            seg = d.add(lines.Line().right(d.unit * 1))

    # d.add(lines.Line().right(d.unit / 8).label(r"$Q_{out}$", loc='right'))
    # add clock line
    for ff in ffs:
        d.add(lines.Line().down(d.unit / 2).at(ff.CLK).dot())
    d.add(lines.Line().left().tox(ffs[0].CLK))
    d.add(lines.Line().left().label("CLK", loc="left"))

    # # add clear line
    for ff in ffs:
        d.add(lines.Line().down(d.unit / 2).at(ff.CLR).dot())
    d.add(lines.Line().left().tox(ffs[0].CLR))
    d.add(lines.Line().left(d.unit*1.7).label("RST", loc="left"))

    # add select lines
    for mux in muxs:
        # d.add(lines.Line().down(d.unit/2).at(mux.S0).dot())
        d.add(lines.Line().down(d.unit / 3).at(mux.S).dot())
        # d.add(elm.Node())
    d.add(lines.Line().left().tox(muxs[0].S))
    d.add(lines.Line().left(d.unit * .3).label("S[1:0]", loc="left"))
    # for mux in muxs:
    #     d.add(lines.Line().down(d.unit / 4).at(mux.S1).dot())
    # d.add(lines.Line().left().tox(muxs[0].S1))
    # d.add(lines.Line().left(d.unit * .5).label("S1", loc="left"))

    for i, mux in enumerate(muxs):
        d.add(lines.Line().left(d.unit / 5).at(mux.D1).label(fr'$A_{n-i-1}$', loc="left"))
        d.add(lines.Line().left(d.unit / 5).at(mux.D2).label(fr'$B_{n-i-1}$', loc="left"))

    d.show()
    # d.save('register_HW_2.tiff')
