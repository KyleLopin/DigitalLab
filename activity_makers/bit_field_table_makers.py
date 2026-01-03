# Copyright (c) 2025 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""

"""

__author__ = "Kyle Vitautas Lopin"


# standard libraries
from dataclasses import dataclass

# installed libraries
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

@dataclass
class Field:
    name: str
    width: int


def draw_bit_grid(bit_fields: [list],
    rows: int = 10,
    cell_size: [float, float] = [.8, 0.5],
    font_size = 12,
    left_column = ["Mnemonic", 1.5],
    right_column = ["Hex Code", 1.3],
    top_buffers=[-0.3, -0.3, -0.3],
    left_texts=(),
    right_texts=(),
    savefig=""):
    # top_columns = ["Mnemonic", "Bit Fields", "Hex Code"]

    cell_w, cell_h = cell_size
    bit_field_names = []
    total_bits = 0
    for name, w, *rest in bit_fields:

        bit_field_names.append(name)
        total_bits += w
    fig_width = total_bits * cell_w
    if left_column:
        fig_width += left_column[1]
    if right_column:
        fig_width += right_column[1]
    print(f"{total_bits} bits total")

    height = (rows * cell_h)
    print(f"size: {fig_width}, {height}")
    fig, ax = plt.subplots(figsize=(fig_width, height))
    ax.axis("off")

    left_w_in = float(left_column[1]) if left_column else 0.0
    right_w_in = float(right_column[1]) if right_column else 0.0

    # draw rows
    for r in range(rows + 1):
        y = r * cell_h
        if r == rows-1:
            ax.plot([0, fig_width], [y, y], color="black", lw=2.5)
        else:
            ax.plot([0, fig_width], [y, y], color="black", lw=0.6)

    if left_column:
        title = str(left_column[0])
        # box
        ax.add_patch(Rectangle((0, 0), left_w_in, height, fill=False, lw=1.2))
        # row lines
        # header
        ax.text(left_w_in / 2, height + top_buffers[2], title, ha="center", va="bottom",
                fontsize=font_size, fontweight="bold")
    if right_column:
        title = str(right_column[0])
        # box
        ax.add_patch(Rectangle((fig_width-right_column[1], 0),
                               right_column[1], height,
                               fill=False, lw=1.2))
        # row lines
        # header
        ax.text(fig_width - (right_w_in / 2),
                height + top_buffers[2], title,
                ha="center", va="bottom",
                fontsize=font_size, fontweight="bold")

    # draw lines for bit fields
    x = left_w_in
    for c in range(total_bits):
        x += cell_w
        plt.plot([x, x], [0, height-cell_h], color="black", lw=0.6)
    print(f"left_w_in: {left_w_in}")
    start = left_w_in
    buff_i = 0
    plt.plot([start, start], [0, height], color="black", lw=2.2)

    for bit_name, bit_field_width, *rest in bit_fields:
        end = start + cell_w * bit_field_width
        print(f"start: {start}, end: {end}, {(end+start)/2}")
        top_buffer = top_buffers[buff_i]
        if not rest:
            ax.text((end+start)/2, height+top_buffer, bit_name,
                    fontsize=font_size, ha="center", va="bottom")
        else:
            ax.text((end + start) / 2, height, bit_name,
                    fontsize=font_size, ha="center", va="bottom")
        start = end
        buff_i = (buff_i + 1) % 2
        plt.plot([end, end], [0, height],
                 color="black", lw=2.5, linestyle="--")

    # because you make the nibble lines from left to right, first calculate
    # how many columns to go right at the start
    bits_over = (total_bits%4)
    print(f"total_bits: {total_bits}")
    if total_bits % 4 == 0:  # if multiple of 4 don't need to make line on the far right
        start = left_w_in + 4 * cell_w
    else:
        start = left_w_in + (total_bits%4)*cell_w

    print(f"pp: ", bits_over, total_bits, start)
    while 0 < bits_over < total_bits:
        print(f"start == : {start}")
        plt.plot([start, start], [0, height-cell_h], color="black", lw=6, solid_capstyle='butt')
        ax.plot([start, start], [0, height-cell_h], color="white", lw=2, solid_capstyle='butt')
        start += 4 * cell_w
        bits_over += 4

    top = height - 2*cell_h
    for text in left_texts:
        plt.text(.1, top, text, ha="left", va="bottom",
                     fontsize=font_size)
        top -= cell_h

    top = height - 2 * cell_h
    for text in right_texts:
        # print(f"text: {text}")
        plt.text(fig_width-right_w_in+0.1, top, text,
                 fontsize=font_size, ha="left", va="bottom")
        top -= cell_h

    if savefig:
        plt.savefig(savefig, dpi=300, bbox_inches="tight")
    plt.show()


# def truth_table(inputs: int | [str],
#                 fill: bool = True):
#     if isinstance(inputs, int) and fill:
#         n = inputs
#         if n < 0:
#             raise ValueError("inputs (n) must be non-negative")
#         rows = []
#         for i in range(2 ** n):
#             # MSB-first ordering: for n=2 -> 00,01,10,11
#             bits = [str((i >> (n - 1 - j)) & 1) for j in range(n)]
#             rows.append(bits)


if __name__ == '__main__':
    # truth_table(3)
    # _bit_fields = [["funct1", 1], ["funct3", 3]]
    # _left_texts = ["A+B", "A|B", "A&B", "A-B", r"A$\oplus$B"]
    # _right_texts = ["", "", "", "", "", "0xF", "0x8", ]
    # draw_bit_grid(_bit_fields, rows=8,
    #               left_texts=_left_texts,
    #               right_texts=_right_texts,
    #               savefig="bit_field_alu.pdf")

    # _bit_fields = [["funct", 1], ["logicSel", 2],
    #                ["ALUSel", 2]]
    # _left_texts = ["A-B", "A|B", "srl(A, B)", "A+B",
    #                "", ""]
    # _right_texts = ["", "", "", "", "0x01", "0x09"]
    # draw_bit_grid(_bit_fields, rows=7,
    #               left_texts=_left_texts,
    #               right_texts=_right_texts,
    #               savefig="bit_field_rocket_chip.svg")

    _bit_fields = [["MemToReg", 1, True], ["rs1", 3],
                   ["Addr", 3]]
    _left_texts = ["t1=RA", "S1=LD(RD)", "a0=t0", "RD=LD(t1)",
                   "RA=s0", "s0=LD(s1)", "", "", "", ""]
    _right_texts = ["0x03", "0x4D", "", "", "", "", "",
                    "0x02", "0x4E", "0x77", "0x08"]
    draw_bit_grid(_bit_fields, rows=7,
                  left_texts=_left_texts,
                  right_texts=_right_texts,
                  savefig="risc_reg_file.svg")

    # _bit_fields = [["funct1", 1], ["rs2", 2],
    #                ["rs1", 2], ["funct3", 3], ["rd", 2], ["MemToReg", 1, True]]
    # _left_texts = ["RA=RA|R8", "RD=RA&RD", "R8=R8+RA",
    #                "R9=LD(RD)", "RA=R8+R9", "RD=R9-R8", "R8=LD(R9)", "", "", "", "", ""]
    # _right_texts = ["", "", "", "", "", "", "", "0x3A2",
    #                 "0x500", "0x37C", "0x065", "0x202"]
    # draw_bit_grid(_bit_fields, rows=13,
    #               left_texts=_left_texts,
    #               right_texts=_right_texts,
    #               # savefig=False)
    #               savefig="bit_field_table_review_1.svg")
