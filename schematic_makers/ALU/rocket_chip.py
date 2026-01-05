# Copyright (c) 2025 Kyle Lopin (Naresuan University) <kylelopin@gmail.com>

"""
Rocket Chip–style ALU drawing utilities.

This module uses Schemdraw to construct a simplified, introductory version of a
Rocket Chip–inspired ALU datapath.

The add_rocket_chip_half_alu implements:
    * An arithmetic path (FullAdder + XOR for add/sub)
    * A small logic unit (AND / OR / XOR selected by a 4:1 mux)
    * A shift unit (simple SRL-style shifter)
    * A top-level ALU result mux

The goal is to provide a clean, teaching-friendly schematic that can be reused
in lecture notes and assignments.

Future extensions:
* Full-width ALU slices and tiling helpers
* Additional operations (SLT/SLTU, SRA, etc.)
* Integration with register file and pipeline-stage drawings

Those more complete Rocket Chip–style diagrams will live in additional helper
functions in this module or in companion modules when completed.
"""

__author__ = "Kyle Vitautas Lopin"


# installed libraries
import schemdraw
from schemdraw import elements as elm
from schemdraw.elements import intcircuits as ic, lines
from schemdraw.logic import And, Or, Xor


# local files
from base import FullAdder, Mux4, Shifter

LABEL_FONT_SIZE = 20


def add_rocket_chip_half_alu(d: schemdraw.Drawing,
                             basic=False):
    """
    Add a partial Rocket Chip–style to an existing Drawing.

    This helper builds an ALU datapath consisting of:
      - A 4:1 mux selecting between adder, logic unit, and shifter outputs
      - An arithmetic path (FullAdder + XOR)
      - A small logic unit (AND / OR / XOR behind a 4:1 mux)
      - A simple shift unit

    The function mutates the provided Schemdraw Drawing in place and returns
    convenient connection points for the A bus, B bus, and ALU result output
    so that the caller can wire this slice into a larger datapath diagram.

    Parameters
    ----------
    d : schemdraw.Drawing
        The Drawing to which the ALU slice will be appended.

    Returns
    -------
    dict[str, tuple[float, float]]
        A mapping with the following keys:
        - "A":  (x, y) coordinate of the shared A-input bus
        - "B":  (x, y) coordinate of the shared B-input bus
        - "ALUout": (x, y) coordinate of the ALU result output
    """
    mux_alu = d.add(Mux4(s_pin_name="S"))
    d.add(lines.Line().at(mux_alu.S).down(d.unit * 0.1).label("ALUSel", loc="left", fontsize=LABEL_FONT_SIZE))
    alu_out_line = d.add(lines.Line().at(mux_alu.Q).right(d.unit * 0.1).label("ALUout", loc="right", fontsize=LABEL_FONT_SIZE))

    # region add adder
    d.add(lines.Line().at(mux_alu.I0).left(d.unit*.2))
    d.add(lines.Line().up(d.unit*1.4))
    d.add(lines.Line().left(d.unit*0.2))
    adder = d.add(FullAdder().anchor("Sum").right())
    d.add(lines.Line().at(adder.B).left(d.unit*.2))
    if basic:
        adder_b = d.add(lines.Line().at(adder.B).left(d.unit*.6).color("blue"))
    if not basic:
        adder_xor = d.add(Xor().anchor("out").right())
    # endregion add adder
    # region logic unit
    d.add(lines.Line().at(mux_alu.I1).left(d.unit * .6))
    d.add(lines.Line().up(d.unit * 0.2))
    d.add(lines.Line().left(d.unit * 0.2))
    logic_mux = d.add(Mux4(s_pin_name="S", size=(1, 2.8),
                           pin_spacing=0.6).anchor("Q").right())
    d.add(lines.Line().down(d.unit*0.01).at(logic_mux.S).label("logicSel", loc="left", fontsize=LABEL_FONT_SIZE))
    d.add(lines.Line().at(logic_mux.I0).left(d.unit * 0.6))
    d.add(lines.Line().up(d.unit * 0.2))
    and_ = d.add(And().anchor("out").right())

    d.add(lines.Line().at(logic_mux.I1).left(d.unit * 0.6))
    or_ = d.add(Or().anchor("out").right())

    d.add(lines.Line().at(logic_mux.I2).left(d.unit * 0.6))
    d.add(lines.Line().down(d.unit * 0.2))
    xor = d.add(Xor().anchor("out").right())
    # endregion logic unit

    # region shifter
    d.add(lines.Line().at(mux_alu.I2).left(d.unit * 0.2))
    d.add(lines.Line().down(d.unit * 0.6))
    d.add(lines.Line().left(d.unit * 1.2))
    shifter = d.add(Shifter(name="Shifter\n(srl)").anchor("out").right())
    # endregion shifter

    # region A/B-lines
    d.add(lines.Line().at(shifter.A).left(d.unit * 0.2).color("red"))
    d.add(lines.Line().toy(adder.A).color("red"))
    d.add(lines.Line().up(d.unit * 0.5).color("red"))
    a_line = d.add(lines.Line().left(d.unit*0.5).color("red").label("A", loc="left", fontsize=LABEL_FONT_SIZE))
    for node in [adder.A, and_.in1, or_.in1, xor.in1]:
        d.add(lines.Line().at(node).tox(a_line.start).color("red").dot())

    d.add(lines.Line().at(shifter.B).left(d.unit * 0.5).color("blue"))
    b_nodes = [None, and_.in2, or_.in2, xor.in2]
    if basic:
        seg = d.add(lines.Line().toy(adder_b.end).color("blue"))
        b_nodes[0] = seg.end
        d.add(lines.Line().at(adder_b.end).to(seg.end).color("blue").dot())
    else:
        b_nodes[0] = adder_xor.in1
        d.add(lines.Line().toy(adder_xor.in1).color("blue"))
    b_line = d.add(lines.Line().tox(a_line.end).color("blue").label("B", loc="left", fontsize=LABEL_FONT_SIZE))

    for node in b_nodes:
        d.add(lines.Line().at(node).tox(b_line.start).color("blue").dot())

    # endregion A/B-lines

    # region add funct1
    if not basic:
        d.add(lines.Line().at(adder_xor.in2).left(d.unit*0.3).color("green"))
        d.add(lines.Line().down(d.unit*3.2).color("green").label("funct1", loc="left", fontsize=LABEL_FONT_SIZE))

    # endregion add funct1

    # Return useful connection points for higher-level wiring
    return {
        "A": a_line.start,  # A bus connection point
        "B": b_line.start,  # B bus connection point
        "ALUout": alu_out_line.end,  # ALU result connection point
    }


if __name__ == '__main__':
    with schemdraw.Drawing() as d:
        add_rocket_chip_half_alu(d, basic=True)
        d.save("rocket_chip_schematic_alu_funct_3.svg")
        d.show()
