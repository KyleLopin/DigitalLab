# Copyright (c) 2025 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""

"""

__author__ = "Kyle Vitautas Lopin"

# standard libraries
import sys

# installed libraries
import schemdraw as sd
from schemdraw.logic import And, Not, Or, Xor
from schemdraw.elements import intcircuits as ic, lines

# local files
from base import Register

SCALE = 1.5
class Mux4(ic.Multiplexer):
    def __init__(self, s_pin_name: str = "S", **kwargs):
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
            pinspacing=1,
            size=(1.8, 2.5),
            **kwargs
        )


class Mux8(ic.Multiplexer):
    def __init__(self, s_pin_name: str = "S", **kwargs):
        super().__init__(
            pins=[
                ic.IcPin(name='I7', side='L'),
                ic.IcPin(name='I6', side='L'),
                ic.IcPin(name='I5', side='L'),
                ic.IcPin(name='I4', side='L'),
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
            pinspacing=0.7,
            size=(2.8, 4.5),
            **kwargs
        )


class Mux2(ic.Multiplexer):
    def __init__(self, s_pin_name: str = "S", **kwargs):
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
            size=(1.2, 2.0),
            **kwargs
        )


class FullAdder(ic.Ic):
    def __init__(self, name: str = "Full Adder", **kwargs):
        super().__init__(
            pins=[
                ic.IcPin(name=r'Cin', side='L'),
                ic.IcPin(name='B', side='L'),
                ic.IcPin(name='A', side='L'),
                ic.IcPin(name=r'$C_{out}$', side='R'),
                ic.IcPin(name='Sum', side='R'),
            ],
            size=(3, 3),
            label = name,
            pinspacing=1,
            edgepadH=1,
            **kwargs
        )


# class Register(ic.Ic):
#     def __init__(self, name, **kwargs):
#         super().__init__(
#             pins=[
#                 ic.IcPin(name='Out', side='R'),
#             ],
#             size=(3.5, .8),
#             label = name,
#             pinspacing=1,
#             edgepadH=1,
#             **kwargs
#         )

# region make basic alu
# with sd.Drawing() as d:
#     mux1 = d.add(Mux4(s_pin_name="S"))
#     d.add(lines.Line().down(d.unit*0.2).at(mux1.S).label("rs1"))
#     regs = []
#     for reg, mux_term in [("RA", mux1.I0), ("RD", mux1.I1),
#                           ("R8", mux1.I2), ("R9", mux1.I3)]:
#         seg = d.add(lines.Line().at(mux_term).left(d.unit*1.2))
#         box = d.add(Register(reg).at(seg.end).anchor("Out").right())
#         regs.append(box)
#
#     for i, reg in enumerate(regs):
#         print(i, reg)
#         d.add(lines.Line().at(reg.Out).right(d.unit * ((i+1)/5)).dot())
#         if i == 0:
#             d.add(lines.Line().down(d.unit * 2.2))
#             # d.add(lines.Line().right(d.unit * 1.1))
#             d.add(lines.Line().tox(mux1.I0))
#             mux2 = d.add(Mux4(s_pin_name="S").anchor("I0"))
#             d.add(lines.Line().down(d.unit * 0.2).at(mux2.S).label("rs2"))
#             mux2_ins = [mux2.I0, mux2.I1, mux2.I2, mux2.I3]
#         else:
#             print(i)
#             d.add(lines.Line().toy(mux2_ins[i]))
#             d.add(lines.Line().to(mux2_ins[i]))
#
#     # make ALU
#     d.add(lines.Line().right(d.unit * 1.8).at(mux1.Q).dot())
#     d.push()
#     d.add(lines.Line().right(d.unit * 0.3))
#     and1 = d.add(And().right().anchor("in1").scale(SCALE))
#     d.pop()
#     d.add(lines.Line().down(d.unit * 1).dot())
#
#     d.push()
#     d.add(lines.Line().right(d.unit * 0.3))
#     or1 = d.add(Or().right().anchor("in1").scale(SCALE))
#     d.pop()
#     d.add(lines.Line().down(d.unit * 1).dot())
#     d.push()
#     d.add(lines.Line().right(d.unit * 0.3))
#     # d.add(Register())
#     adder = d.add(FullAdder().anchor("A"))
#     d.pop()
#     d.add(lines.Line().down(d.unit * 2))
#     d.add(lines.Line().right(d.unit * 0.3))
#     xor = d.add(Xor().anchor("in1").scale(SCALE))
#     seg = d.add(lines.Line().at(adder.B).left(d.unit * 0.4))
#     mux3 = d.add(Mux2(s_pin_name="S").anchor("Q").right())
#     d.add(lines.Line().down(d.unit * 0.2).at(mux3.S).label("funct1"))
#
#     # connect rs2 to subtract mux
#     # b_seg = d.add(lines.Line().right(d.unit * 0.2).dot())
#     d.add(lines.Line().toy(mux3.I0).at(mux2.Q))
#     b_seg = d.add(lines.Line().right(d.unit * 0.2).dot())
#     d.add(lines.Line().to(mux3.I0))
#     d.add(lines.Line().toy(mux3.I1).at(mux2.Q).idot())
#     d.add(lines.Line().right(d.unit * 0.4))
#     d.add(Not().anchor("in1").scale(SCALE/2))
#     d.add(lines.Line().to(mux3.I1))
#
#     d.add(lines.Line().at(mux3.S).tox(adder.A))
#     d.add(lines.Line().toy(adder.Cin))
#
#     # connect B to all other gates
#     d.add(lines.Line().at(b_seg.end).toy(and1.in2))
#     d.add(lines.Line().to(and1.in2))
#     d.add(lines.Line().at(or1.in2).tox(b_seg.end).dot())
#     d.add(lines.Line().at(xor.in2).tox(b_seg.end))
#     d.add(lines.Line().to(b_seg.end))
#
#     # add mux and then attach
#     d.add(lines.Line().at(adder.Sum).right(d.unit * 0.6))
#     mux_funct3 = d.add(Mux4(s_pin_name="S").anchor("I2"))
#     d.add(lines.Line().at(mux_funct3.S).down(d.unit * 0.1).label("funct2"))
#     d.add(lines.Line().at(xor.out).tox(mux_funct3.I3))
#     d.add(lines.Line().to(mux_funct3.I3))
#     d.add(lines.Line().at(and1.out).tox(mux_funct3.I3))
#     d.add(lines.Line().to(mux_funct3.I0))
#
#     d.add(lines.Line().at(or1.out).right(d.unit * 0.4))
#     d.add(lines.Line().toy(mux_funct3.I1))
#     d.add(lines.Line().tox(mux_funct3.I1))
#
#     d.add(lines.Line().at(mux_funct3.Q).right(d.unit * 0.1).label("Out"))
#
#     d.save('alu_1.pdf')
# endregion make basic alu

SAVE_AT = "REG_ALU"  # choose ALU
FUNCT1 = False
# mimic RISC-V
with sd.Drawing() as d:
    # region ALU
    # make mux
    mux_alu = d.add(Mux8(s_pin_name="S"))
    d.add(lines.Line().at(mux_alu.S).down(d.unit*0.1).label("funct3", loc="left"))
    d.add(lines.Line().at(mux_alu.Q).right(d.unit * 0.1).label("ALU out", loc="right"))

    # region ADDER
    d.add(lines.Line().at(mux_alu.I0).left(d.unit * 1))
    d.add(lines.Line().up(d.unit * 0.5))
    d.add(lines.Line().left(d.unit * 0.5))
    adder = d.add(FullAdder().anchor("Sum").right())


    # region SUB
    a_line = d.add(lines.Line().at(adder.A).left(d.unit * 0.3).dot().color("blue"))

    if FUNCT1:
        seg = d.add(lines.Line().at(adder.B).left(d.unit * 0.5))
        sub_xor = d.add(Xor().anchor("out").right())
        b_line = d.add(lines.Line().at(sub_xor.in1).left(d.unit * 0.3).color("red").dot())
    else:
        b_line = d.add(lines.Line().at(adder.B).left(d.unit * 0.6).color("red").dot())
        # sub_xor = d.add(lines.Line().at(adder.A).left(d.unit * 1.3).color("blue"))
        # sub_xor.in2 = sub_xor.end

    # sub_not = d.add(Not().at(seg.end).anchor("out").reverse())
    # b_line = d.add(lines.Line().toy(sub_xor.I0).dot().color("red"))
    # d.add(lines.Line().tox(sub_xor.I0).color("red"))

    # add select line label
    # attach Cin to funct1
    if FUNCT1:
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
    a_line_out = d.add(lines.Line().left(d.unit*1.0).color("blue").label("A", loc="left"))
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
    d.add(lines.Line().left(d.unit*0.4).color("red").label("B", loc="left"))
    d.save("ALU_simple.svg")
    d.show()
    # add ctrl line down
    d.add(lines.Line().at(ctrl_line.end).toy(and_.in2))
    d.add(lines.Line().down(d.unit * 0.5).label("funct1", loc="left"))

    # endregion AND
    # endregion ALU
    if SAVE_AT == "ALU":
        # d.save('ALU_exercise_opCodes.png')
        sys.exit()

    # region register_file
    mux_rs1 = d.add(Mux4(s_pin_name="S").right().at(a_line_out.end).anchor("Q"))
    d.add(lines.Line().down(d.unit * 0.2).at(mux_rs1.S).label("rs1"))
    regs = []
    for reg, mux_term in [("RA", mux_rs1.I0), ("RD", mux_rs1.I1),
                          ("R8", mux_rs1.I2), ("R9", mux_rs1.I3)]:
            seg = d.add(lines.Line().at(mux_term).left(d.unit*1.2))
            box = d.add(Register(reg).at(seg.end).anchor("Out").right())
            regs.append(box)

    for i, reg in enumerate(regs):
        print(i, reg)
        d.add(lines.Line().at(reg.Out).right(d.unit * ((i+1)/5)).dot())
        if i == 0:
            d.add(lines.Line().down(d.unit * 2.2))
            # d.add(lines.Line().right(d.unit * 1.1))
            d.add(lines.Line().tox(mux_rs1.I0))
            mux_rs2 = d.add(Mux4(s_pin_name="S").anchor("I0"))
            d.add(lines.Line().down(d.unit * 0.2).at(mux_rs2.S).label("rs2"))
            mux2_ins = [mux_rs2.I0, mux_rs2.I1, mux_rs2.I2, mux_rs2.I3]
        else:
            print(i)
            d.add(lines.Line().toy(mux2_ins[i]))
            d.add(lines.Line().to(mux2_ins[i]))

    d.add(lines.Line().at(mux_rs2.Q).tox(b_line.end).color("red").dot())

    # d.add(lines.Line().at(mux_alu.Q).toy(mux_rs1.I0))
    # d.add(lines.Line().up(d.unit * 1))
    # d.add(lines.Line())


    # if SAVE_AT == "REG_ALU":
    #     d.save('ALU_reg_exercise_opCodes.png')
    #     sys.exit()


SAVE_AT = "Final"  # choose ALU

# mimic RISC-V - with mux sub
# with sd.Drawing() as d:
#     # region ALU
#     # make mux
#     mux_alu = d.add(Mux8(s_pin_name="S"))
#     d.add(lines.Line().at(mux_alu.S).down(d.unit*0.1).label("funct3", loc="left"))
#     d.add(lines.Line().at(mux_alu.Q).right(d.unit * 0.1).label("ALU out", loc="right"))
#
#     # region ADDER
#     d.add(lines.Line().at(mux_alu.I0).left(d.unit * 1))
#     d.add(lines.Line().up(d.unit * 0.5))
#     d.add(lines.Line().left(d.unit * 0.5))
#     adder = d.add(FullAdder().anchor("Sum").right())
#
#
#     # region SUB
#     a_line = d.add(lines.Line().at(adder.A).left(d.unit * 0.3).dot().color("blue"))
#     seg = d.add(lines.Line().at(adder.B).left(d.unit * 0.5))
#     sub_mux = d.add(Mux2(s_pin_name="S").anchor("Q").right())
#     seg = d.add(lines.Line().at(sub_mux.I1).left(d.unit * 0.3))
#     sub_not = d.add(Not().at(seg.end).anchor("out").reverse())
#     b_line = d.add(lines.Line().toy(sub_mux.I0).dot().color("red"))
#     d.add(lines.Line().tox(sub_mux.I0).color("red"))
#
#     # add select line label
#     seg = d.add(lines.Line().at(sub_mux.S).down(d.unit * 0.2).label("funct1", loc="left"))
#     # attach Cin to funct1
#     d.add(lines.Line().at(adder.Cin).down(d.unit * 0.3))
#     d.add(lines.Line().tox(seg.end).dot())
#     # endregion SUB
#     # endregion ADDER
#
#     # region XOR
#     seg = d.add(lines.Line().at(mux_alu.I4).left(d.unit * 1.5))
#     xor = d.add(Xor().at(seg.end).right().anchor("out").scale(SCALE))
#     d.add(lines.Line().at(xor.in1).tox(a_line.end).dot().color("blue"))
#     d.add(lines.Line().to(a_line.end).color("blue"))
#     d.add(lines.Line().up(d.unit * 0.5).color("blue"))
#     d.add(lines.Line().tox(b_line.end).color("blue"))
#     a_line_out = d.add(lines.Line().left(d.unit*1).color("blue"))
#     d.add(lines.Line().at(xor.in2).tox(b_line.end).dot().color("red"))
#     d.add(lines.Line().to(b_line.start).dot().color("red"))
#     # endregion XOR
#
#     # region OR
#     seg = d.add(lines.Line().at(mux_alu.I6).left(d.unit * 0.8))
#     or_ = d.add(Or().at(seg.end).right().anchor("out").scale(SCALE))
#     d.add(lines.Line().at(or_.in1).tox(a_line.end).dot().color("blue"))
#     d.add(lines.Line().toy(a_line.start).dot())
#     d.add(lines.Line().at(or_.in2).tox(b_line.end).dot().color("red"))
#     d.add(lines.Line().to(b_line.start).dot().color("red"))
#     # endregion OR
#
#     # region AND
#     d.add(lines.Line().at(mux_alu.I7).left(d.unit * 0.4))
#     d.add(lines.Line().down(d.unit * 0.5))
#     seg = d.add(lines.Line().left(d.unit * 1.2))
#     and_ = d.add(And().at(seg.end).right().anchor("out").scale(SCALE))
#     d.add(lines.Line().at(and_.in1).tox(a_line.end).dot().color("blue"))
#     d.add(lines.Line().toy(a_line.start).dot().color("blue"))
#     d.add(lines.Line().at(and_.in2).tox(b_line.end).dot().color("red"))
#     d.add(lines.Line().to(b_line.start).dot().color("red"))
#     # endregion AND
#     # endregion ALU
#     if SAVE_AT == "ALU":
#         d.save('ALU_exercise_opCodes.png')
#         print("check", SAVE_AT)
#         sys.exit()
#
#     # region register_file
#     mux_rs1 = d.add(Mux4(s_pin_name="S").right().at(a_line_out.end).anchor("Q"))
#     d.add(lines.Line().down(d.unit * 0.2).at(mux_rs1.S).label("rs1"))
#     regs = []
#     for reg, mux_term in [("RA", mux_rs1.I0), ("RD", mux_rs1.I1),
#                           ("R8", mux_rs1.I2), ("R9", mux_rs1.I3)]:
#             seg = d.add(lines.Line().at(mux_term).left(d.unit*1.2))
#             box = d.add(Register(reg).at(seg.end).anchor("Out").right())
#             regs.append(box)
#
#     for i, reg in enumerate(regs):
#         print(i, reg)
#         d.add(lines.Line().at(reg.Out).right(d.unit * ((i+1)/5)).dot())
#         if i == 0:
#             d.add(lines.Line().down(d.unit * 2.2))
#             # d.add(lines.Line().right(d.unit * 1.1))
#             d.add(lines.Line().tox(mux_rs1.I0))
#             mux_rs2 = d.add(Mux4(s_pin_name="S").anchor("I0"))
#             d.add(lines.Line().down(d.unit * 0.2).at(mux_rs2.S).label("rs2"))
#             mux2_ins = [mux_rs2.I0, mux_rs2.I1, mux_rs2.I2, mux_rs2.I3]
#         else:
#             print(i)
#             d.add(lines.Line().toy(mux2_ins[i]))
#             d.add(lines.Line().to(mux2_ins[i]))
#
#     d.add(lines.Line().at(mux_rs2.Q).tox(b_line.end).color("red").dot())
#     # if SAVE_AT == "REG_ALU":
#     #     d.save('ALU_reg_exercise_opCodes.png')
#     #     sys.exit()