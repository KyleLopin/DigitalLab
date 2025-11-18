# Copyright (c) 2025 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""

"""

__author__ = "Kyle Vitautas Lopin"
# standard libraries
import sys

# installed libraries
import schemdraw as sd
from schemdraw.logic import And, Not, Or, Xor
from schemdraw.elements import Arrow, intcircuits as ic, lines

# local files
from base import Decoder4, Decoder2to4, FullAdder, Mem, Mux2, Mux4, Mux8, Register

SCALE = 1.5
BIT_FIELD_FONTSIZE = 30
# with sd.Drawing() as d:
#     # region register_file
#     mux_rs1 = d.add(Mux4(s_pin_name="S").right())
#     d.add(lines.Line().down(d.unit * 0.2).at(mux_rs1.S).label("rs1"))
#     regs = []
#     reg_conns = []
#     mux_terms = [mux_rs1.I0, mux_rs1.I1, mux_rs1.I2, mux_rs1.I3]
#     l1 = [1.3, 1.5, 1.7, 1.9]
#     up1 = [.5, .2, .2, .5]
#     l2 = [.7, .5, .3, .1]
#     for i, reg in enumerate(["RA", "RD", "R8", "R9"]):
#         print("check")
#         mux_term = mux_terms[i]
#         print(mux_term)
#         d.add(lines.Line().at(mux_term).left(d.unit * l1[i]))
#         if i < 2:
#             d.add(lines.Line().up(d.unit * up1[i]).idot())
#         else:
#             d.add(lines.Line().down(d.unit * up1[i]).dot())
#         seg = d.add(lines.Line().left(d.unit * l2[i]))
#         reg_conns.append(seg.start)
#         reg = d.add(Register(reg).at(seg.end).anchor("Out").right())
#         p = reg.CLK  # anchor coordinate
#         # d.add(Arrow(headlength=0.18, headwidth=0.14)
#         #       .at((p[0] - 0.35, p[1]))  # start a bit to the left
#         #       .to(p))
#         # Two strokes forming a > into the pin
#         s = 0.1  # size of the notch
#         stub_len = .4
#         stub_back = .7
#         d.add(lines.Line().at((p[0] + s+stub_len, p[1] - s)).to((p[0]+stub_back, p[1])))
#         d.add(lines.Line().at((p[0] + s+stub_len, p[1] + s)).to((p[0]+stub_back, p[1])))
#         # d.add(sd.elements.Label("CLK"))
#         regs.append(reg)
#     for i, reg in enumerate(regs):
#         print(i, reg)
#         # d.add(lines.Line().at(reg.Out).right(d.unit * ((i + 1) / 5)).dot())
#         if i == 0:
#             d.add(lines.Line().at(reg_conns[i]).down(d.unit * 3.2))
#             # d.add(lines.Line().right(d.unit * 1.1))
#             d.add(lines.Line().tox(mux_rs1.I0))
#             mux_rs2 = d.add(Mux4(s_pin_name="S").anchor("I0"))
#             d.add(lines.Line().down(d.unit * 0.2).at(mux_rs2.S).label("rs2"))
#             mux2_ins = [mux_rs2.I0, mux_rs2.I1, mux_rs2.I2, mux_rs2.I3]
#         else:
#             d.add(lines.Line().at(reg_conns[i]).toy(mux2_ins[i]))
#             d.add(lines.Line().to(mux2_ins[i]))
#
#     # region clock
#     for i in range(3):
#         d.add(lines.Line().at(regs[i].CLK).to(regs[i+1].CLK).dot())
#     d.add(lines.Line().left(d.unit * 0.4).label("CLK", loc="left"))
#     # endregion clock
#
#     # region datain
#     for i in range(4):
#         if i < 3:
#             d.add(lines.Line().at(regs[i].In).left(d.unit*0.3).dot())
#         else:
#             seg = d.add(lines.Line().at(regs[i].In).left(d.unit * 0.3))
#
#     d.add(lines.Line().at(seg.end).up(d.unit * 2.5).label("Data In", loc="right"))
#     # endregion datain
#
#     # region enable
#     en_conns = []
#     for i in range(4):
#         conn = d.add(lines.Line().at(regs[i].pinEN).left(d.unit * 1.8))
#         en_conns.append(conn)
#     # endregion enable
#
#     for i, conn in enumerate(en_conns):
#         if i == 0:
#             d.add(lines.Line().at(conn.end).left(d.unit * 0.6))
#             decoder = d.add(Decoder4(s_pin_name="EN", addr_pin_name="rd").anchor('D0').right())
#         else:
#             d.add(lines.Line().at(conn.end).left(d.unit * (0.2*i)))
#             d.add(lines.Line().toy(decoder[f"D{i}"]))
#             d.add(lines.Line().to(decoder[f"D{i}"]))
#     # endregion register_file

    # d.save("register_file.png")


with sd.Drawing() as d:
    # region ALU
    # make mux
    mux_alu = d.add(Mux8(s_pin_name="S"))
    d.add(lines.Line().at(mux_alu.S).down(d.unit*0.1).label("funct3",
                                                            loc="left",
                                                            fontsize=BIT_FIELD_FONTSIZE))
    d.add(lines.Line().at(mux_alu.Q).right(d.unit * 0.1).label("ALU out", loc="right"))

    # region ADDER
    d.add(lines.Line().at(mux_alu.I0).left(d.unit * 1))
    d.add(lines.Line().up(d.unit * 0.5))
    d.add(lines.Line().left(d.unit * 0.5))
    adder = d.add(FullAdder().anchor("Sum").right())


    # region SUB
    a_line = d.add(lines.Line().at(adder.A).left(d.unit * 0.3).dot().color("blue"))
    seg = d.add(lines.Line().at(adder.B).left(d.unit * 0.5))
    sub_xor = d.add(Xor().anchor("out").right())
    b_line = d.add(lines.Line().at(sub_xor.in1).left(d.unit * 0.3).color("red").dot())

    # sub_not = d.add(Not().at(seg.end).anchor("out").reverse())
    # b_line = d.add(lines.Line().toy(sub_xor.I0).dot().color("red"))
    # d.add(lines.Line().tox(sub_xor.I0).color("red"))

    # add select line label
    # attach Cin to funct1
    d.add(lines.Line().at(adder.Cin).tox(sub_xor.in1).dot())
    ctrl_line = d.add(lines.Line().toy(sub_xor.in2).dot())
    # endregion SUB
    # endregion ADDER
    # region XOR
    seg = d.add(lines.Line().at(mux_alu.I4).left(d.unit * 1.5))
    xor = d.add(Xor().at(seg.end).right().anchor("out").scale(SCALE))
    d.add(lines.Line().at(xor.in1).tox(a_line.end).dot().color("blue"))
    d.add(lines.Line().to(a_line.end).color("blue"))
    d.add(lines.Line().up(d.unit * 0.5).color("blue"))
    # d.add(lines.Line().tox(b_line.end).color("blue"))
    # a_line_out = d.add(lines.Line().left(d.unit*1.5).color("blue"))
    a_line_out = d.add(lines.Line().left(d.unit * 1.5).color("blue"))

    d.add(lines.Line().at(xor.in2).tox(b_line.end).dot().color("red"))
    d.add(lines.Line().to(b_line.end).dot().color("red"))
    # endregion XOR

    # region OR
    seg = d.add(lines.Line().at(mux_alu.I6).left(d.unit * 0.8))
    or_ = d.add(Or().at(seg.end).right().anchor("out").scale(SCALE))
    d.add(lines.Line().at(or_.in1).tox(a_line.end).dot().color("blue"))
    d.add(lines.Line().toy(a_line.start).dot())
    d.add(lines.Line().at(or_.in2).tox(b_line.end).dot().color("red"))
    d.add(lines.Line().to(b_line.end).dot().color("red"))
    # endregion OR

    # region AND
    d.add(lines.Line().at(mux_alu.I7).left(d.unit * 0.4))
    d.add(lines.Line().down(d.unit * 0.5))
    seg = d.add(lines.Line().left(d.unit * 1.2))
    and_ = d.add(And().at(seg.end).right().anchor("out").scale(SCALE))
    d.add(lines.Line().at(and_.in1).tox(a_line.end).dot().color("blue"))
    d.add(lines.Line().toy(a_line.start).dot().color("blue"))
    d.add(lines.Line().at(and_.in2).tox(b_line.end).dot().color("red"))
    d.add(lines.Line().to(b_line.end).dot().color("red"))
    # add ctrl line down
    d.add(lines.Line().at(ctrl_line.end).toy(and_.in2))
    d.add(lines.Line().down(d.unit * 0.5).label("funct1", loc="left", fontsize=BIT_FIELD_FONTSIZE))
    # endregion AND
    # endregion ALU

    # region register_file
    mux_rs1 = d.add(Mux4(s_pin_name="S").at(a_line_out.end).anchor("Q").right())
    d.add(lines.Line().down(d.unit * 0.2).at(mux_rs1.S).label("rs1", fontsize=BIT_FIELD_FONTSIZE))
    regs = []
    reg_conns = []
    mux_terms = [mux_rs1.I0, mux_rs1.I1, mux_rs1.I2, mux_rs1.I3]
    l1 = [0.8, 1.0, 1.2, 1.4]
    up1 = [.5, .2, .2, .5]
    l2 = [.7, .5, .3, .1]
    for i, reg in enumerate(["RA", "RD", "R8", "R9"]):
        print("check")
        mux_term = mux_terms[i]
        print(mux_term)
        d.add(lines.Line().at(mux_term).left(d.unit * l1[i]))
        if i < 2:
            d.add(lines.Line().up(d.unit * up1[i]).idot())
        else:
            d.add(lines.Line().down(d.unit * up1[i]).dot())
        seg = d.add(lines.Line().left(d.unit * l2[i]))
        reg_conns.append(seg.start)
        reg = d.add(Register(reg).at(seg.end).anchor("Out").right())
        p = reg.CLK  # anchor coordinate
        # d.add(Arrow(headlength=0.18, headwidth=0.14)
        #       .at((p[0] - 0.35, p[1]))  # start a bit to the left
        #       .to(p))
        # Two strokes forming a > into the pin
        s = 0.1  # size of the notch
        stub_len = .4
        stub_back = .7
        d.add(lines.Line().at((p[0] + s+stub_len, p[1] - s)).to((p[0]+stub_back, p[1])))
        d.add(lines.Line().at((p[0] + s+stub_len, p[1] + s)).to((p[0]+stub_back, p[1])))
        # d.add(sd.elements.Label("CLK"))
        regs.append(reg)
    for i, reg in enumerate(regs):
        print(i, reg)
        # d.add(lines.Line().at(reg.Out).right(d.unit * ((i + 1) / 5)).dot())
        if i == 0:
            d.add(lines.Line().at(reg_conns[i]).down(d.unit * 3.2))
            # d.add(lines.Line().right(d.unit * 1.1))
            d.add(lines.Line().tox(mux_rs1.I0))
            mux_rs2 = d.add(Mux4(s_pin_name="S").anchor("I0"))
            d.add(lines.Line().down(d.unit * 0.2).at(mux_rs2.S).label("rs2", fontsize=BIT_FIELD_FONTSIZE))
            mux2_ins = [mux_rs2.I0, mux_rs2.I1, mux_rs2.I2, mux_rs2.I3]
        else:
            d.add(lines.Line().at(reg_conns[i]).toy(mux2_ins[i]))
            d.add(lines.Line().to(mux2_ins[i]))

    # region clock
    for i in range(3):
        d.add(lines.Line().at(regs[i].CLK).to(regs[i+1].CLK).dot())
    d.add(lines.Line().left(d.unit * 0.4).label("CLK", loc="left"))
    # endregion clock

    # region datain
    for i in range(4):
        if i < 3:
            d.add(lines.Line().at(regs[i].In).left(d.unit*0.3).dot())
        else:
            seg = d.add(lines.Line().at(regs[i].In).left(d.unit * 0.3))

    data_in = d.add(lines.Line().at(seg.end).up(d.unit * 2.5))
    # endregion datain

    # region enable
    en_conns = []
    for i in range(4):
        conn = d.add(lines.Line().at(regs[i].pinEN).left(d.unit * 1.1))
        en_conns.append(conn)
    # endregion enable

    for i, conn in enumerate(en_conns):
        if i == 0:
            d.add(lines.Line().at(conn.end).left(d.unit * 0.6))
            decoder = d.add(Decoder4(s_pin_name="EN", addr_pin_name="rd").anchor('D0').right())
        else:
            d.add(lines.Line().at(conn.end).left(d.unit * (0.2*i)))
            d.add(lines.Line().toy(decoder[f"D{i}"]))
            d.add(lines.Line().to(decoder[f"D{i}"]))
    d.add(lines.Line().at(decoder.rd).left(d.unit * 0.1).label(r"rd", loc="left", fontsize=BIT_FIELD_FONTSIZE))
    # endregion register_file

    # fix rs2 to B
    d.add(lines.Line().at(mux_rs2.Q).tox(b_line.end).color("red"))

    d.add(lines.Line().at(data_in.end).up(d.unit * 1.2))
    d.add(lines.Line().left(d.unit * 0.6).label("Data In", loc="right"))
    mux_mem = d.add(Mux2(s_pin_name="S").anchor("Q").right())

    d.add(lines.Line().at(mux_mem.S).down(d.unit * 0.05).label("MemToReg", loc="left", fontsize=BIT_FIELD_FONTSIZE))

    d.add(lines.Line().at(mux_alu.Q).toy(mux_mem.I0))
    d.add(lines.Line().up(d.unit * 0.8))
    d.add(lines.Line().tox(mux_mem.I0))
    d.add(lines.Line().to(mux_mem.I0))

    d.add(lines.Line().at(mux_mem.I1).left(d.unit * 0.5))
    memory = d.add(Mem(name="RAM\n\n").anchor("Out").right())

    d.add(lines.Line().at(mux_rs1.Q).toy(data_in.end).color("green"))
    # d.add(lines.Line().up(d.unit * 0.8).color("green"))
    d.add(lines.Line().tox(memory.Addr).color("green"))
    d.add(lines.Line().to(memory.Addr).color("green"))

    d.save("ALU_reg_mem.pdf")
    d.show()
