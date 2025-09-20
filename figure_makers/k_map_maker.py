# Copyright (c) 2025 Kyle Lopin (Naresuan University / University of Wisconsin Platteville) <kylel@nu.ac.th>

"""

"""

__author__ = "Kyle Vitautas Lopin"


import matplotlib.pyplot as plt
from math import log2

def gray_sequence(n_bits):
    """Return Gray-code list of bitstrings length 2^n_bits, MSB..LSB."""
    seq = []
    for i in range(1 << n_bits):
        g = i ^ (i >> 1)
        seq.append(f"{g:0{n_bits}b}")
    return seq

def blank_kmap_by_vars(x_vars=("A","B"), y_vars=("C","D")):
    """
    Create a blank grid sized by the number of row/col variables.
    - x_vars: tuple/list of variables on columns (0-2 vars)
    - y_vars: tuple/list of variables on rows   (0-2 vars)
    Total variables must be 2..4, and len(x_vars)+len(y_vars)=total.
    """
    x_vars = tuple(x_vars)
    y_vars = tuple(y_vars)
    n_x = len(x_vars)
    n_y = len(y_vars)
    total = n_x + n_y
    if total < 2 or total > 4:
        raise ValueError("Total number of variables must be 2, 3, or 4.")
    if n_x < 1 or n_y < 1:
        raise ValueError("Put at least 1 variable on columns and 1 on rows.")
    cols = 1 << n_x
    rows = 1 << n_y
    return [["" for _ in range(cols)] for _ in range(rows)]

def draw_kmap(
    grid,
    x_vars=("A","B"),
    y_vars=("C","D"),
    scale=1.0,
    save_fig=False
):
    """
    Draw a blank Karnaugh map with variable-flexible axes.
    - grid: rows x cols list of strings
    - x_vars: variables on columns (e.g., ("A","B") -> 4 columns in Gray order)
    - y_vars: variables on rows    (e.g., ("C","D") -> 4 rows in Gray order)
    - save_fig: False to show interactively; or a string path to save.
    """
    x_vars = tuple(x_vars)
    y_vars = tuple(y_vars)
    n_x = len(x_vars)
    n_y = len(y_vars)
    rows = len(grid)
    cols = len(grid[0]) if rows else 0

    # Validate dims match vars
    if rows != (1 << n_y) or cols != (1 << n_x):
        raise ValueError(
            f"Grid size {rows}x{cols} does not match vars: "
            f"{len(y_vars)} row var(s) => {1<<n_y} rows, "
            f"{len(x_vars)} col var(s) => {1<<n_x} cols."
        )

    # Gray labels
    col_bits = gray_sequence(n_x)  # left->right
    row_bits = gray_sequence(n_y)  # top->bottom

    # Figure size proportional to grid
    fig_w = max(4.5, 1.2 * cols + 2.0)
    fig_h = max(4.0, 1.2 * rows + 2.0)
    fig = plt.figure(figsize=(fig_w, fig_h), dpi=160)
    ax = plt.gca()
    ax.set_aspect("equal")
    ax.axis("off")

    # Axis labels, e.g., "AB" and "CD"
    ax.text(cols / 2 + 0.0, rows + 0.7, " ".join(x_vars),
            ha="center", va="center",
            fontsize=16, fontweight="bold")
    ax.text(-0.6, rows / 2, " ".join(y_vars), ha="center",
            va="center", rotation=90,
            fontsize=16, fontweight="bold")

    # Column Gray-code labels
    for c, bits in enumerate(col_bits):
        ax.text(c + 0.5, rows + 0.2, bits, ha="center", va="bottom")
    # Row Gray-code labels
    for r, bits in enumerate(row_bits):
        ax.text(-0.1, rows - 0.5 - r, bits, ha="right", va="center")

    # Draw grid rectangles; place cell (r,c) with top-left at (c, rows-1-r)
    for r in range(rows):
        for c in range(cols):
            rect = plt.Rectangle((c*scale, (rows - 1 - r)*scale),
                                 scale, scale, fill=False, linewidth=1.0)
            ax.add_patch(rect)
            val = grid[r][c]
            if val:
                ax.text((c + 0.5)*scale, (rows - 1 - r + 0.6)*scale,
                        val, ha="center", va="center")

    # Range with a little margin
    ax.set_xlim(-0.7* scale, (cols + 0.7))
    ax.set_ylim(-0.7* scale, (rows + 1.0))

    if isinstance(save_fig, str):
        plt.savefig(save_fig, bbox_inches="tight")
        plt.close(fig)
        print(f"K-map saved to {save_fig}")
    else:
        plt.show()

# ---- Quick demos ----
if __name__ == "__main__":
    # 2-variable K-map (2x2). Example split: A on columns, B on rows.
    # g2 = blank_kmap_by_vars(x_vars=("A",), y_vars=("B",))
    # draw_kmap(g2, x_vars=("A",), y_vars=("B",), save_fig=False)

    # 3-variable K-map (2x4). Common split: AB on columns, C on rows.
    # g3 = blank_kmap_by_vars(x_vars=("A","B"), y_vars=("C",))
    # draw_kmap(g3, x_vars=("A","B"), y_vars=("C",), save_fig=False)

    # 4-variable K-map (4x4). Common split: AB on columns, CD on rows.
    g4 = blank_kmap_by_vars(x_vars=("A","B"), y_vars=("C","D"))
    # Save to file example:
    # draw_kmap(g4, x_vars=("A","B"), y_vars=("C","D"), save_fig="kmap_4var.png")
    draw_kmap(g4, x_vars=("A","B"), y_vars=("C","D"), save_fig=False)