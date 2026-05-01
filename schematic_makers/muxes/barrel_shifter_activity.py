# Copyright (c) 2026 Kyle Lopin (Naresuan University) <kylelopin@gmail.com>

"""

"""

__author__ = "Kyle Vitautas Lopin"

# installed libraries
import schemdraw as sd
import schemdraw.elements.intcircuits as ic
import schemdraw.elements as elm

class Mux4(ic.Multiplexer):
    def __init__(self, s_pin_name: str = "S", size=(1.8, 2.5), **kwargs):
        super().__init__(
            pins=[
                ic.IcPin(name='I3', side='L'),
                ic.IcPin(name='I2', side='L'),
                ic.IcPin(name='I1', side='L'),
                ic.IcPin(name='I0', side='L'),
                ic.IcPin(name='Q',  side='R'),
                ic.IcPin(name=s_pin_name, side='B'),
                # ic.IcPin(name='S1', side='B'),
                # ic.IcPin(name='EN', side='T', invert=True),
            ],
            edgepadH=-.2,
            pinspacing=0.8,
            size=size,
            **kwargs
        )


class Mux2(ic.Multiplexer):
    def __init__(self, s_pin_name: str = "S", size=(1.2, 2.0), **kwargs):
        super().__init__(
            pins=[
                ic.IcPin(name='I1', side='L'),
                ic.IcPin(name='I0', side='L'),
                ic.IcPin(name='Q',  side='R'),
                ic.IcPin(name=s_pin_name, side='B'),
                # ic.IcPin(name='S1', side='B'),
                # ic.IcPin(name='EN', side='T', invert=True),
            ],
            edgepadH=-.2,
            pinspacing=1,
            size=size,
            **kwargs
        )

m_size = (1.3, 1.5)
# with sd.Drawing() as d:
#     muxs = []
#     # make select line to align all muxes
#     d += elm.Line().right().label(r"Shift", loc='left')
#     d.push()
#     # d += elm.Line().up(d.unit * 0.2)
#     d += (m0 := Mux4(size=m_size).right().anchor("S"))
#     muxs.append(m0)
#     for i in range(3):
#         d.pop()
#         d += elm.Line().right(d.unit*0.7)
#         d += elm.Line().up(d.unit*1.3)
#         d += elm.Line().left(d.unit*0.7)
#         # d += elm.Line().up(d.unit * 0.2)
#         d += (m := Mux4(size=m_size).right().anchor("S"))
#         muxs.append(m)
#         d.push()
#     for i, mux in enumerate(reversed(muxs)):
#         # add in lines
#         d += elm.Line().at(mux.I0).left(d.unit * 1.2).label(f"$a_{i}$", loc="left")
#         d += elm.Line().at(mux.Q).right(d.unit * 0.01).label(f"$Q_{i}$", loc="right")
#         # d += elm.Line().at(mux.S).down(d.unit * 0.01).label("Select")
#
#     # d += elm.Line().right().label(r"$a_3$", loc='left')
#     # d += Mux4().right().anchor("I0")


with sd.Drawing() as d:
    muxes_1 = []
    muxes_2 = []
    d += elm.Line().right().label(r"S0", loc='left')
    d.push()
    # d += elm.Line().up(d.unit * 0.2)
    d += (m0 := Mux2(size=m_size).right().anchor("S"))
    muxes_1.append(m0)
    for i in range(3):
        d.pop()
        d += elm.Line().right(d.unit*0.5)
        d += elm.Line().up(d.unit*1.3).dot()
        d += elm.Line().left(d.unit*0.5)
        # d += elm.Line().up(d.unit * 0.2)
        d += (m := Mux2(size=m_size).right().anchor("S"))
        muxes_1.append(m)
        d.push()
    # d.show()
    d += elm.Line().at(muxes_1[0].Q).right()
    d += (m0 := Mux2(size=m_size).right().anchor("I0"))
    muxes_2.append(m0)
    d += elm.Line().at(m0.S).left(d.unit * 0.01)

    d.push()
    d += elm.Line().at(m0.S).left(d.unit*0.5).label(r"S1", loc='left')

    for i in range(3):
        d.pop()
        d += elm.Line().right(d.unit*0.7)
        d += elm.Line().up(d.unit*1.3).dot()
        d += elm.Line().left(d.unit*0.7)
        # d += elm.Line().up(d.unit * 0.2)
        d += (m := Mux2(size=m_size).right().anchor("S"))
        muxes_2.append(m)
        d.push()

    for i, mux in enumerate(reversed(muxes_1)):
        # add in lines
        print("i = ", i)
        d += elm.Line().at(mux.I0).left(d.unit * 1.2).label(f"$a_{i}$", loc="left")
    for i, mux in enumerate(reversed(muxes_2)):
        d += elm.Line().at(mux.Q).right(d.unit * 0.01).label(f"$Q_{i}$", loc="right")


# d.save("mux_tree_barrel.png")


d.save(fname="Mux_2.png")
