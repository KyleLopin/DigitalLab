# Copyright (c) 2025 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""

"""

__author__ = "Kyle Vitautas Lopin"

# installed libraries
from schemdraw.elements import intcircuits as ic
from schemdraw import elements as elm


class Mux4(ic.Multiplexer):
    def __init__(self, s_pin_name: str = "S", size=(1.8, 4.5),
                 pin_spacing=1.25, **kwargs):
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
            pinspacing=pin_spacing,
            size=size,
            **kwargs
        )


class Mux16(ic.Multiplexer):
    def __init__(self, s_pin_name: str = "S", **kwargs):
        _pins = []
        for i in range(15, -1, -1):
            _pins.append(ic.IcPin(name=f"I{i}", side='L'))
        _pins.append(ic.IcPin(name='Q',  side='R'))
        _pins.append(ic.IcPin(name=s_pin_name, side='B'))
        super().__init__(
            pins=_pins,
            edgepadH=0,
            pinspacing=0.5,
            size=(2.8, 7.5),
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
            edgepadH=0,
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
            edgepadH=0,
            pinspacing=1,
            size=(1.4, 2.4),
            **kwargs
        )


class Decoder4(ic.Multiplexer):
    def __init__(self, s_pin_name: str = "S",
                 addr_pin_name="Addr",**kwargs):
        super().__init__(
            pins=[
                ic.IcPin(name='D3', side='R'),
                ic.IcPin(name='D2', side='R'),
                ic.IcPin(name='D1', side='R'),
                ic.IcPin(name='D0', side='R'),
                ic.IcPin(name=addr_pin_name,  side='L'),
                # ic.IcPin(name=s_pin_name, side='B'),
                # ic.IcPin(name='S1', side='B'),
                # ic.IcPin(name='EN', side='T', invert=True),
            ],
            edgepadH=-2,
            demux=True,
            pinspacing=1.25,
            size=(1.8, 4.5),
            **kwargs
        )


class Decoder8(ic.Multiplexer):
    def __init__(self, s_pin_name: str = "S",
                 addr_pin_name="Addr",**kwargs):
        super().__init__(
            pins=[
                ic.IcPin(name='D7', side='R'),
                ic.IcPin(name='D6', side='R'),
                ic.IcPin(name='D5', side='R'),
                ic.IcPin(name='D4', side='R'),
                ic.IcPin(name='D3', side='R'),
                ic.IcPin(name='D2', side='R'),
                ic.IcPin(name='D1', side='R'),
                ic.IcPin(name='D0', side='R'),
                ic.IcPin(name=addr_pin_name,  side='L'),
                # ic.IcPin(name=s_pin_name, side='B'),
                # ic.IcPin(name='S1', side='B'),
                # ic.IcPin(name='EN', side='T', invert=True),
            ],
            edgepadH=-2,
            demux=True,
            pinspacing=0.8,
            size=(2.1, 6.5),
            **kwargs
        )


class Shifter(ic.Ic):
    def __init__(self, name: str = "Shifter\n", **kwargs):
        super().__init__(
            pins=[
                ic.IcPin(name='B', side='L'),
                ic.IcPin(name='A', side='L'),
                ic.IcPin(name="out", side='R'),
            ],
            size=(3, 2),
            label = name,
            pinspacing=1,
            edgepadH=1,
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


class Decoder3_8(ic.Ic):
    def __init__(self, name: str = "3-to-8\nDecoder", **kwargs):
        super().__init__(
            pins=[
                # inputs on the left
                ic.IcPin(name='A0', side='L'),
                ic.IcPin(name='A1', side='L'),
                ic.IcPin(name='A2', side='L'),
                # outputs on the right
                ic.IcPin(name='D7', side='R'),
                ic.IcPin(name='D6', side='R'),
                ic.IcPin(name='D5', side='R'),
                ic.IcPin(name='D4', side='R'),
                ic.IcPin(name='D3', side='R'),
                ic.IcPin(name='D2', side='R'),
                ic.IcPin(name='D1', side='R'),
                ic.IcPin(name='D0', side='R'),
            ],
            size=(3, 6),  # a bit taller for 8 outputs
            label=name,
            pinspacing=0.6,
            edgepadH=0.6,
            **kwargs
        )


class Register(ic.Ic):
    def __init__(self, name, **kwargs):
        super().__init__(
            pins=[
                ic.IcPin(name='Out', side='R'),
                ic.IcPin(pin='EN', side='B', pos=0.2),
                elm.IcPin(name='CLK', side='L'),
                ic.IcPin(name='In', side='L'),
            ],
            size=(3.5, 1.2),
            label = name,
            pinspacing=0.5,
            edgepadH=.1,
            **kwargs
        )


class Mem(ic.Ic):
    def __init__(self, name, **kwargs):
        super().__init__(
            pins=[
                ic.IcPin(name='Out', side='R'),
                # elm.IcPin(name='CLK', side='L'),
                ic.IcPin(name='Addr', side='L'),
            ],
            size=(3.5, 3.5),
            label = name,
            pinspacing=1.4,
            edgepadH=.1,
            **kwargs
        )


class RAM(ic.Ic):
    def __init__(self, name, size=(3.5, 3.5), **kwargs):
        super().__init__(
            pins=[
                ic.IcPin(name='Data Out', side='R'),
                ic.IcPin(name='Addr', side='L'),
                elm.IcPin(name='Data In', side='L'),

                ic.IcPin(name='WE#', side='B'),
                ic.IcPin(name='OE#', side='B'),
                ic.IcPin(name='CE#', side='B'),
            ],
            size=size,
            label = name,
            pinspacing=1.1,
            edgepadH=.1,
            **kwargs
        )


class RAMDown(ic.Ic):
    def __init__(self, name, size=(2.5, 2.5), **kwargs):
        super().__init__(
            pins=[
                ic.IcPin(name='Data Out', side='B'),
                ic.IcPin(name='Addr', side='T'),
                elm.IcPin(name='Data In', side='B'),

                # ic.IcPin(name='WE#', side='R'),
                # ic.IcPin(name='OE#', side='R'),
                ic.IcPin(name='CE', side='R'),
            ],
            size=size,
            label = name,
            pinspacing=2.1,
            edgepadH=.1,
            **kwargs
        )


class CPU_L(ic.Ic):
    def __init__(self, name="CPU       ", size=(5, 5), **kwargs):
        super().__init__(
            pins=[
                # ic.IcPin(name="DQ[7:0]", side='L'),
                ic.IcPin(name='WE#', side='L'),
                ic.IcPin(name='OE#', side='L'),
                ic.IcPin(name="DQ[3:0]", side='R'),

                ic.IcPin(name="DQ[7:4]", side='R'),
                ic.IcPin(name="DQ[11:8]", side='R'),
                ic.IcPin(name="DQ[15:12]", side='R'),
                ic.IcPin(name='Addr', side='L'),
                # ic.IcPin(name='Addr [17:16]', side='L'),
                ic.IcPin(name='CE#', side='L'),
            ],
            size=size,
            label = name,
            pinspacing=.6,
            edgepadH=.1,
            **kwargs
        )


class CPU_1Bus(ic.Ic):
    def __init__(self, name="Memory\nController\n\n\n", size=(3, 5), **kwargs):
        super().__init__(
            pins=[
                ic.IcPin(name="DQ", side='L'),
                ic.IcPin(name="Write", side='L'),
                ic.IcPin(name='Addr', side='L'),
            ],
            size=size,
            label = name,
            pinspacing=1.3,
            edgepadH=.1,
            **kwargs
        )


class Decoder2to4(ic.Ic):
    def __init__(self, name='DEC 2→4', en=True, active_low_en=False, **kw):
        pins = [
            ic.IcPin(name='S', side='L', pin='A'),
            ic.IcPin(name='S', side='L', pin='B'),
        ]
        if en:
            pins.append(ic.IcPin(name='', side='B', pin='EN', invert=active_low_en))
        pins += [
            ic.IcPin(name='D0', side='R', pin='Y0'),
            ic.IcPin(name='D1', side='R', pin='Y1'),
            ic.IcPin(name='D2', side='R', pin='Y2'),
            ic.IcPin(name='D3', side='R', pin='Y3'),
        ]
        super().__init__(pins=pins, size=(3.2, 2.2), pinspacing=0.6, edgepadH=-.3, **kw)
        self.label(name)
