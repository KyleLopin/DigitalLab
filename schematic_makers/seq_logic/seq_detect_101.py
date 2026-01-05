# Copyright (c) 2025 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""

"""

__author__ = "Kyle Vitautas Lopin"


# installed libaries
import schemdraw as sd
from schemdraw.elements import intcircuits as ic, lines
import schemdraw.logic as logic


def detect_101(filename=None):
    with sd.Drawing() as d:
        # region make DFFs
        dff_a = d.add(ic.DFlipFlop().label("A").color("blue"))
        # Add "A+" next to the D input
        # dff_a.add_label("A+", loc="D", ofst=(-0.2, 0))
        d.add(lines.Line().at(dff_a.D).left(d.unit*0.01).label("A+"))
        print(dff_a.anchors.keys())
        d.add(lines.Line().at(dff_a.CLK).left(d.unit * 0.9).color("blue"))
        d.add(lines.Line().down(d.unit * 2).color("blue"))
        d.push()
        d.add(lines.Line().right(d.unit * 0.9).color("blue"))
        dff_b = d.add(ic.DFlipFlop().anchor("CLK").color("blue"))
        d.add(lines.Line().at(dff_b.D).left(d.unit * 0.01).label("B+"))

        d.pop()
        d.add(lines.Line().down(d.unit * 0.5).label("CLK", loc="left").color("blue"))
        # endregion make DFFs

        # region make seq logic
        a_and = d.add(logic.Or().at(dff_a.D).anchor("out").right().scale(1))
        not1 = d.add(logic.Not(leadin=0.01, leadout=0.01).at(a_and.in1).anchor("end").right())

        d.add(lines.Line().at(not1.start).left(d.unit * 0.01).label("X", loc="top"))
        d.add(lines.Line().at(a_and.in2).left(d.unit * 0.1).label("B", loc="left"))
        d.add(lines.Line().at(dff_a.Q).right(d.unit * 0.1).label("A", loc="right"))

        b_and = d.add(logic.And().at(dff_b.D).anchor("out").scale(1))
        # d.add(lines.Line().at(b_and.in1).left(d.unit * 0.1).label(r"X", loc="left"))
        d.add(lines.Line().at(not1.start).idot().toy(b_and.in1))
        d.add(lines.Line().to(b_and.in1))

        d.add(lines.Line().at(b_and.in2).left(d.unit * 0.1).label("A", loc="left"))
        d.add(lines.Line().at(dff_b.Q).right(d.unit * 0.1).label("B", loc="right"))
        # endregion make seq logic

        # make output line
        d.add(lines.Line().at(dff_b.D).down(d.unit * 1).idot())
        d.add(lines.Line().right(d.unit * 1.2).label("Z\u0334", loc="right"))

        if filename:
            d.save(filename)


if __name__ == '__main__':
    detect_101(filename="seq_detect_101.svg")
