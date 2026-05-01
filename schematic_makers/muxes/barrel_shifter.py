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
    def __init__(self, s_pin_name: str = "S", size=(1.2, 1.9), **kwargs):
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
            pinspacing=0.8,
            size=size,
            **kwargs
        )


m_size = (1.5, 2.1)
colors = ["black", "red", "green", "blue", "orange"]
mux_map = {0: [[1, "I1"], [2, "I2"], [3, "I3"]],
           1: [[2, "I1"], [3, "I2"], [0, "I3"]]}
# 4, 4-bit muxes into barrel
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
#
#     for i, mux in enumerate(muxs):
#         # if i==2:
#         #     break
#         # add in lines
#         start_dist = (i+1) * d.unit * 0.2
#         d += elm.Line().at(mux.I0).left(start_dist).dot().color(colors[i])
#         d.push()
#         # for mux_num, pin_num in mux_map[i]:
#         for j in range(3):
#             mux_num = (j+i+1) % 4
#             # pin_num = (j+i+1) % 4
#             pin_num = f"I{j+1}"
#             print(f"i: {i}, mux: {mux_num}; I{pin_num}, pin: {pin_num}")
#             d += elm.Line().toy(muxs[mux_num][pin_num]).dot().color(colors[i])
#             d.push()
#             d += elm.Line().tox(muxs[mux_num][pin_num]).color(colors[i])
#             d.pop()
#
#         d.pop()
#         print(f"i = {i}, start_dist = {start_dist}, dist = {d.unit * 2 - start_dist}")
#         print("check: ", i, d.unit * 2)
#         d += (elm.Line().at(mux.I0).left(d.unit * 2)
#               .label(f"$a_{3-i}$", loc="left").color(colors[i]))
#         d += elm.Line().at(mux.Q).right(d.unit * 0.01).label(f"$Q_{3-i}$", loc="right")
#         # d += elm.Line().at(mux.S).down(d.unit * 0.01).label("Select")
#
# d.save(fname="Barrel_shifter.png")
# d.show()

# 4-bit mux tree
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
    d += elm.Line().at(muxes_1[0].Q).right(1.5*d.unit)
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

    for i, mux in enumerate(muxes_1):
        # if i == 3:
        #     break
        # add in lines
        print("i = ", i)
        d += (elm.Line().at(mux.I0).left(d.unit * 1.2)
              .label(f"$a_{i}$", loc="left").color(colors[i]))
        back_dist = 1
        if i ==3:
            back_dist = 0.8
        d += elm.Line().right(back_dist * d.unit).dot().color(colors[i])
        next_mux = muxes_1[(i+1)%4]
        d += elm.Line().toy(next_mux.I1).color(colors[i])
        d += elm.Line().tox(next_mux.I1).color(colors[i])

    dists = [0.2,0.4, 0.6, 0.8]
    for i, mux in enumerate(muxes_1):
        print("i2 = ", i)
        d += elm.Line().at(mux.Q).to(muxes_2[i].I0).color(colors[i])

        branch_pt = (
            muxes_2[i].I0.x - dists[i] * d.unit,
            muxes_2[i].I0.y
        )
        d += elm.Line().at(muxes_2[i].I0).to(branch_pt).dot().color(colors[i])

        dest = muxes_2[(i + 2) % 4].I1

        d += elm.Line().at(branch_pt).toy(dest.y).color(colors[i])
        d += elm.Line().at((branch_pt[0], dest.y)).tox(dest.x).color(colors[i])

        # d += elm.Line().tox(muxes_2[(i+2)%4].I1)

    for i, mux in enumerate(reversed(muxes_2)):
        d += elm.Line().at(mux.Q).right(d.unit * 0.01).label(f"$Q_{i}$", loc="right")

    d.save(fname="barrel_shifter_tree.png")
