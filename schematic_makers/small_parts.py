# Copyright (c) 2025 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""

"""

__author__ = "Kyle Vitautas Lopin"

# installed libaries
import schemdraw as sd
import schemdraw.elements as elm
from schemdraw.elements import lines

# local files
from base import CPU_L, Mem, RAM


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


if __name__ == '__main__':
    # make_ram_bus_up(filename="RAM_w_bus_up.pdf")
    cpu_for_ram(filename="images/RAM_8bit_expand.pdf")
