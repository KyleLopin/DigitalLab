# Copyright (c) 2025 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""

"""

__author__ = "Kyle Vitautas Lopin"

# installed libaries
import schemdraw as sd
import schemdraw.elements as elm
from schemdraw.elements import lines
import schemdraw.logic as logic

# local files
from schematic_makers.ALU.base import CPU_L, RAM


def make_7_seg():
    with sd.Drawing() as d:
        disp = elm.SevenSegment(cathode=False, labelsegments=False).anchor('a')

        d.save("7-segment.pdf")


def make_ram(filename=None):
    with sd.Drawing() as d:
        d.add(RAM("RAM\n\n\n", size=(5, 4.5)))

        if filename:
            d.save(filename)


def make_ram_connected(filename=None):
    with sd.Drawing() as d:
        ram = d.add(RAM("RAM\n\n\n", size=(5, 4.5)))
        d.add(lines.Line().at(ram["Data In"]).down(d.unit*2.4))
        d.add(lines.Line().tox(ram["Data Out"]).label("DQ[7:0]", loc="bottom").dot())
        d.push()
        # d.add(lines.Line().right())
        d.pop()
        d.add(lines.Line().to(ram["Data Out"]))

        # address line
        d.add(lines.Line().at(ram["Addr"]).right(d.unit*0.1).label("ADDR[15:0]", loc="left"))

        if filename:
            d.save(filename)


def make_ram_bus_up(filename=None):
    with sd.Drawing() as d:
        ram = d.add(RAM("RAM\n\n\n", size=(5, 4.5)))
        d.add(lines.Line().at(ram["Data In"]).up(d.unit*2.4))
        d.add(lines.Line().tox(ram["Data Out"]).label("DQ[7:0]", loc="bottom").dot())
        d.push()
        # d.add(lines.Line().right())
        d.pop()
        d.add(lines.Line().to(ram["Data Out"]))

        # address line
        d.add(lines.Line().at(ram["Addr"]).right(d.unit*0.1).label("ADDR[15:0]", loc="left"))

        if filename:
            d.save(filename)


def cpu_for_ram(filename=None):
    with sd.Drawing() as d:
        cpu = d.add(CPU_L("\n\n\n\n\nCPU\n\nMemory\nController", size=(5, 6)))

    if filename:
        d.save(filename)


def timing_schematic_1(filename=None):
    """ To show a hazard """
    with sd.Drawing() as d:
        # 3-input AND gate, output labeled F
        and3 = d.add(logic.And(3).right().scale(2))

        # Inputs B and C go straight into the AND
        d += logic.Line().left(d.unit*0.1).at(and3.in1).label('B', 'left')
        d += logic.Line().left(d.unit*0.1).at(and3.in2).label('C', 'left')
        seg = d.add(lines.Line().at(and3.in3).left(d.unit*0.2))

        # D goes through a NOT gate before the AND
        notd = d.add(
            logic.Not()
            .at(seg.end)  # place NOT so its output is at the 3rd AND input
            .anchor('out')
            .right().label('D', 'left')
        )

        seg = d.add(lines.Line().at(and3.out).right(d.unit*0.5).label('E', 'bottom'))
        or2 = d.add(logic.Or().anchor("in2").scale(2))
        d.add(lines.Line().at(or2.in1).right(d.unit*0.1).label('A', 'left'))
        d.add(lines.Line().at(or2.out).right(d.unit*0.1).label('F', 'top'))
        if filename:
            d.save(filename)


if __name__ == '__main__':
    # make_ram_bus_up(filename="RAM_w_bus_up.pdf")
    # cpu_for_ram(filename="images/RAM_8bit_expand.pdf")
    timing_schematic_1(filename="hazard_1.pdf")
