# Copyright (c) 2025 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""

"""

__author__ = "Kyle Vitautas Lopin"


import matplotlib.pyplot as plt

def plot_binary_arithmetic(a: int, b: int, bits: int = 4,
                           show_result: bool = False,
                           title: str = None,
                           save_fig: str = None):
    """
    Make a pyplot figure of A - B using two's complement addition for a fixed bit-width.
    Renders two rows by default:
        row 1: A (in binary, right-aligned to `bits`)
        row 2: + two's complement of B (i.e., -B in two's complement)

    Parameters
    ----------
    a : int
        Minuend (the first number).
    b : int
        Subtrahend (the second number).
    bits : int
        Bit-width to represent values (two's complement wrap/overflow follows this width).
    show_result : bool
        If True, also shows a horizontal line and the (A + (-B)) result row.
    title : str
        Optional figure title.
    save_fig : str or None
        If not None, path/filename where the figure will be saved.
        Example: "binary_subtraction.png"
    """
    if bits < 1:
        raise ValueError("bits must be >= 1")

    mask = (1 << bits) - 1

    # Strings, right-aligned to bit width (keep leading zeros to preserve alignment)
    a_str     = format(a & mask, f'0{bits}b')

    # Second number
    if b >= 0:
        b_str = format(b & mask, f'0{bits}b')
        prefix = "+ "
    else:
        b_str = format(b & mask, f'0{bits}b')  # already in two's complement form
        prefix = "- "  # show a minus sign in front

    rows = [f"  {a_str}", f"{prefix}{b_str}"]

    # Optional result
    result = (a + b) & mask
    result_str = format(result, f'0{bits}b')

    if show_result:
        # rows.append("- " + "-" * bits)
        rows.append("  " + result_str)

    # Figure layout
    fig_size = [min(1, 0.2*bits + 2), 0.5 + 0.2*len(rows)]
    if show_result:
        fig_size[1] += .2
    fig, ax = plt.subplots(figsize=fig_size)
    ax.axis('off')

    # Title
    if title :
        ax.set_title(title, pad=12)

    # Render text lines (monospace helps alignment)
    y0 = 0.9
    dy = 0.3
    for i, line in enumerate(rows):
        ax.text(0.02, y0 - i*dy, line, family="Courier New",
                fontsize=16, transform=ax.transAxes)

    y_line = y0 - 1.5 * dy + .1  # adjust so it sits between row 2 and result
    # ADJUST BOTTOM LINE TO FIX LENGHT OF EQUAL LINE, IS WORKING A LITTLE BUT COULD BE OFF
    ax.hlines(y_line, 0.05, .95, transform=ax.transAxes, colors='black', linewidth=1)
    plt.tight_layout()
    if save_fig:
        fig.savefig(save_fig, dpi=300, bbox_inches="tight")

    return fig, ax


if __name__ == '__main__':
    # Example: 5 - 8 with 4 bits → shows "0101" and "+ 1000" on two rows
    # fig, ax = plot_binary_arithmetic(5, 8, bits=4, show_result=False)
    # plt.show()

    # If you also want the result row:
    fig, ax = plot_binary_arithmetic(5, 8, bits=6, show_result=False,
                                     save_fig="bin_exam_a.png")
    plt.show()
