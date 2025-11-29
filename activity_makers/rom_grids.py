# Copyright (c) 2025 Kyle Lopin (Naresuan University) <kylelopin@gmail.com>

"""
Add functions to create ROM tables with wordlines and grid lines to create assignment
and activity images for digital logic class
"""

__author__ = "Kyle Vitautas Lopin"

# installed libraries
import schemdraw as sd
from schemdraw.elements import Label, lines

# local files
from schematic_makers.ALU.base import Decoder3_8

def rom_grids_no_fill():
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
            d.add(lines.Line().down(d.unit*2).label(f"f{i}", loc="left"))
        d.save("ROM_grid_lines.svg")


def rom_grids_with_fill(bit_lines: int = 4,
        row_masks: list[int] | None = None,
        row_indices: list[list[int]] | None = None,
        filename = None,
    ):

    with sd.Drawing() as d:
        bit_lines = 4
        decoder = d.add(Decoder3_8(name="3-to-8\nDecoder"))
        # d.add(Label("3-to-8\nDecoder").at(decoder.top))
        pins = [decoder.D0, decoder.D1, decoder.D2, decoder.D3,
                decoder.D4, decoder.D5, decoder.D6, decoder.D7]
        word_lines = []
        for p in pins:
            w_l = d.add(lines.Line().at(p).right(d.unit * 2.5))
            word_lines.append(w_l)

        bit_lines_pos = []
        for i in range(bit_lines):
            x_pos = decoder.D0.x + d.unit * (2.5 * (i + 1) / (bit_lines))
            bit_lines_pos.append(x_pos)
            # d.add(lines.Line().at(decoder.D0).right(d.unit * (2.5 * (i + 1) / (bit_lines))))
            d.add(
                lines.Line()
                .at((x_pos, decoder.D0.y))
                .down(d.unit * 2).label(f"f{i}", loc="left")
            )

        # Now place X's based on either row_masks or row_indices
        n_rows = len(word_lines)

        if row_masks is not None:
            print("masks", word_lines)
            # Ensure we have a mask for each word line (or pad with 0)
            if len(row_masks) < n_rows:
                row_masks = list(row_masks) + [0] * (n_rows - len(row_masks))
            for row_idx, wl in enumerate(word_lines):
                print("row: ", row_idx)
                y = wl.start.y
                mask = row_masks[row_idx]
                print(row_idx, wl, mask, y)
                for bit_idx, x in enumerate(bit_lines_pos):
                    print("bit: ", bit_idx, x)
                    if mask & (1 << bit_idx):
                        print("check")
                        lbl = d.add(
                            Label("×", color='red', fontsize=30)
                            .at((x-.1, y+.1))
                        )

        elif row_indices is not None:
            # Ensure row_indices has a list for each row
            if len(row_indices) < n_rows:
                row_indices = list(row_indices) + [[] for _ in range(n_rows - len(row_indices))]
            for row_idx, wl in enumerate(word_lines):
                y = wl.start.y
                cols = row_indices[row_idx]
                for bit_idx in cols:
                    if 0 <= bit_idx < bit_lines:
                        x = bit_lines_pos[bit_idx]
                        d.Text((x, y), "×", color='red', fontsize=10)

        if filename:
            d.save(filename)
        else:
            d.show()


if __name__ == '__main__':
    rom_grids_no_fill()
    # row_masks = [
    #     0x1,  # row 0: 0001 → X at bit 0
    #     0x9,  # row 1: 1001 → X at bits 0 and 3
    #     0x0,  # row 2: no X
    #     0xF,  # row 3: 1111 → all four bits
    #     0x2,  # row 4: 0010 → bit 1
    #     0xB,  # row 5
    #     0x4,  # row 6: 0100 → bit 2
    #     0x8,  # row 7: 1000 → bit 3
    # ]
    # rom_grids_with_fill(row_masks=row_masks,
    #                     filename="ROM_grids_fill1.svg")
