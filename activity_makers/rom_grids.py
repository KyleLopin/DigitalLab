# Copyright (c) 2025 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""

"""

__author__ = "Kyle Vitautas Lopin"

# installed libraries
import schemdraw as sd
from schemdraw.elements import Label, lines

# local files
from schematic_makers.base import Decoder3_8

with sd.Drawing() as d:
    bit_lines = 4
    decoder = d.add(Decoder3_8(name="3-to-8\nDecoder"))
    # d.add(Label("3-to-8\nDecoder").at(decoder.top))
    pins = [decoder.D0, decoder.D1, decoder.D2, decoder.D3,
            decoder.D4, decoder.D5, decoder.D6, decoder.D7]
    word_lines = []
    for p in pins:
        print(p)
        print("check")
        w_l = d.add(lines.Line().at(p).right(d.unit*2.5))
        word_lines.append(w_l)

    for i in range(bit_lines):
        d.add(lines.Line().at(decoder.D0).right(d.unit*(2.5*(i+1)/(bit_lines))))
        d.add(lines.Line().down(d.unit*3))
    d.save("ROM_grid_lines.pdf")
