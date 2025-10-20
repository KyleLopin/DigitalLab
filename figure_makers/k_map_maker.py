# Copyright (c) 2025 Kyle Lopin (Naresuan University / University of Wisconsin Platteville) <kylel@nu.ac.th>

"""

"""

__author__ = "Kyle Vitautas Lopin"

# standard libraries
import re

# installed libraries
import matplotlib.pyplot as plt
from sympy import symbols
from sympy.logic.boolalg import simplify_logic


# look up tables to map numbers to K-map grids
LUT_2x2 = {
    0:(0,0), 1:(0, 1),
    2:(1, 0), 3:(1,1)
}

LUT_4x2 = {
    0:(0,0), 1:(1, 0),
    2:(0,1), 3:(1,1),
    4:(2, 0), 5:(1,2),
    6:(3, 0), 7:(1,3)
}

LUT_2x4 = {
    0: (0, 0), 1: (1, 0), 3: (2, 0), 2: (3, 0),
    4: (0, 1), 5: (1, 1), 7: (2, 1), 6: (3, 1)
}

LUT_4x4 = {
    0:(0, 0), 1:(1, 0), 3:(2, 0), 2:(3, 0),
    4:(0, 1), 5:(1,1),  7:(2, 1), 6:(3, 1),
    12:(0, 2),13:(1, 2),15:(2,2), 14:(3, 2),
    8:(0, 3), 9:(1, 3), 11:(2, 3),10:(3,3)
}

def gray_sequence(n_bits):
    """Return Gray-code list of bitstrings length 2^n_bits, MSB..LSB.
       ie ['00','01','11','10'] for n_bits=2, etc."""
    return [format(i ^ (i >> 1), f"0{n_bits}b") for i in range(1 << n_bits)]
    # seq = []
    # for i in range(1 << n_bits):
    #     g = i ^ (i >> 1)
    #     seq.append(f"{g:0{n_bits}b}")
    # return seq

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


def equation_to_minterms(expr_str, variables=("A", "B", "C", "D")):
    """
    Convert a Boolean equation string into a list of minterm indices.

    Parameters
    ----------
    expr_str : str
        Boolean expression in classroom style, e.g. "A'B + C D'".
        - A' = NOT A
        - adjacency or * = AND
        - + = OR
    variables : tuple of str
        Variable names in MSB..LSB order for minterm numbering.

    Returns
    -------
    list of int
        List of minterm indices (0..2^n - 1) where expression evaluates True.
    """
    # --- Normalize classroom syntax to Python/Sympy ---
    s = expr_str.strip().replace(" ", "")
    s = re.sub(r"([A-Za-z])'", r"~\1", s)  # A' → ~A
    s = s.replace("+", "|")  # + → OR
    s = s.replace("*", "&")  # * → AND
    s = re.sub(r"([A-Za-z\)])(?=[A-Za-z\(~])", r"\1&", s)  # implicit AND

    # --- Make sympy symbols ---
    syms = symbols(" ".join(variables))
    var_map = dict(zip(variables, syms))

    # --- Parse string into sympy expr ---
    expr = eval(s, {"__builtins__": {}}, var_map)

    # --- Optionally simplify ---
    expr = simplify_logic(expr, form="dnf")

    # --- Collect minterms ---
    n = len(variables)
    minterms = []
    for m in range(1 << n):
        bits = [(m >> k) & 1 for k in reversed(range(n))]  # MSB..LSB
        env = {sym: bool(bit) for sym, bit in zip(syms, bits)}
        if bool(expr.xreplace(env)):
            minterms.append(m)

    return minterms


def draw_kmap(
    grid,
    x_vars=("A","B"),
    y_vars=("C","D"),
    data_set=None,  # TODO: fuully impliment
    scale=0.5,
    save_fig=False
):
    """
    Draw a blank Karnaugh map with variable-flexible axes.
    - grid: rows x cols list of strings
    - x_vars: variables on columns (e.g., ("A","B") -> 4 columns in Gray order)
    - y_vars: variables on rows    (e.g., ("C","D") -> 4 rows in Gray order)
    - data_set: if empty/None => leave cells blank; otherwise fill each cell.
        Accepts either:
          * dict with (r,c) -> "1"/"0"/"X"/""      # rows=0..rows-1, cols=0..cols-1   # <<< NEW
          * 2D list/tuple of same shape as grid with strings per cell               # <<< NEW
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
    # check data_set is correct form
    if data_set is not None:
        if isinstance(data_set, (list, tuple)):
            if len(data_set) != rows or len(data_set[0]) != cols:
                raise ValueError("data_set 2D shape must match grid.")

    # Gray labels
    col_bits = gray_sequence(n_x)  # left->right
    row_bits = gray_sequence(n_y)  # top->bottom

    # Figure size proportional to grid
    fig_w = max(3, (cols + 2))
    fig_h = max(3, (rows + 2))
    fig = plt.figure(figsize=(fig_w, fig_h), dpi=160)
    ax = plt.gca()
    ax.set_aspect("equal")
    ax.axis("off")

    # Axis labels, e.g., "AB" and "CD"
    ax.text(cols / 2 + 0.0, rows + 0.7, " ".join(x_vars),
            ha="center", va="center",
            fontsize=32*scale, fontweight="bold")
    ax.text(-0.6, rows / 2, " ".join(y_vars), ha="center",
            va="center", rotation=90,
            fontsize=32*scale, fontweight="bold")

    # Column Gray-code labels
    for c, bits in enumerate(col_bits):
        ax.text(c + 0.5, rows + 0.2, bits, ha="center", va="bottom",
                fontsize=32*scale)
    # Row Gray-code labels
    for r, bits in enumerate(row_bits):
        ax.text(-0.1, rows - 0.5 - r, bits, ha="right", va="center",
                fontsize=32*scale)

    # Draw grid rectangles; place cell (r,c) with top-left at (c, rows-1-r)
    for r in range(rows):
        for c in range(cols):
            rect = plt.Rectangle((c, rows - 1 - r),
                                 1, 1, fill=False, linewidth=1.0)
            ax.add_patch(rect)
            if data_set:
                if isinstance(data_set, (list, tuple)):
                    val = data_set[r][c]
                elif isinstance(data_set, dict):
                    val = data_set.get((r, c), "")
            else:
                val = grid[r][c]

            if val:
                ax.text((c + 0.5), (rows - 1 - r + 0.6),
                        val, ha="center", va="center",
                        fontsize=32*scale)

    # Range with a little margin
    ax.set_xlim(-0.7, (cols + 0.7))
    ax.set_ylim(-0.7, (rows + 1.0))

    if isinstance(save_fig, str):
        plt.savefig(save_fig, bbox_inches="tight")
        plt.close(fig)
        print(f"K-map saved to {save_fig}")
    else:
        plt.show()


def make_data_set(x_vars=("A","B"), y_vars=("C","D"),
                  minterms=None, maxterms=None, dont_cares=None):
    """
    Build a 2D data_set grid for draw_kmap from minterms/maxterms.
    - x_vars, y_vars: variable split (decides shape: 2x2, 2x4, 4x4)
    - minterms, maxterms, dont_cares: sets/lists of minterm integers.
    - Empty cells are None.
    """
    # Use your existing helper to get a blank grid of correct size
    grid = blank_kmap_by_vars(x_vars, y_vars)

    size = (len(grid), len(grid[0]))  # (rows, cols)

    def minterm_to_rc(m):
        if size == (2, 2):
            return LUT_2x2[m]
        elif size == (2, 4):
            return LUT_2x4[m]
        elif size == (4, 2):
            return LUT_2x4[m]
        elif size == (4, 4):
            return LUT_4x4[m]
        else:
            raise ValueError("Unsupported size (only 2x2, 2x4, 4x4 allowed)")

    print(minterms)
    if minterms:
        for m in minterms:
            r, c = minterm_to_rc(m)
            print("00: ", r, c, m)
            grid[r][c] = "1"

    if maxterms:
        for m in maxterms:
            r, c = minterm_to_rc(m)
            grid[r][c] = "0"

    if dont_cares:
        for m in dont_cares:
            r, c = minterm_to_rc(m)
            grid[r][c] = "X"

    return grid


if __name__ == "__main__":
    # 2-variable K-map (2x2). Example split: A on columns, B on rows.
    g2 = blank_kmap_by_vars(x_vars=("A",), y_vars=("B",))
    # draw_kmap(g2, x_vars=("A",), y_vars=("B",), save_fig=False)


    # 3-variable K-map (2x4). Common split: AB on columns, C on rows.
    data2d = [["", "1", "", ""],
              ["", "", "", "X"]]
    data_dict = {(0, 1): "1", (1, 1): "X", (2, 1): "0"}
    g3 = blank_kmap_by_vars(x_vars=("A"), y_vars=("B", "C"))
    g3_f = make_data_set(
        x_vars=("A"), y_vars=("B", "C"),
        minterms={0, 1, 3}, dont_cares={4, 5},
        maxterms={2, 6, 7}
    )
    # draw_kmap(g3, x_vars=("A"), y_vars=("B" ,"C"),
    #           data_set=g3_f, save_fig="TestBench_video_exercise.png")

    # 4-variable K-map (4x4). Common split: AB on columns, CD on rows.
    g4 = blank_kmap_by_vars(x_vars=("A","B"), y_vars=("C","D"))
    # Save to file example:
    draw_kmap(g4, x_vars=("A","B"), y_vars=("C","D"), save_fig="kmap_4var.png")
    # draw_kmap(g4, x_vars=("A","B"), y_vars=("C","D"), save_fig=False)


    g4 = make_data_set(
        x_vars=("A", "B"), y_vars=("C", "D"),
        minterms={0, 2, 5, 10}, dont_cares={3, 6, 9, 13, 14, 15}
    )
    # eqn = "A'CD + B'C + AD'"
    # mins = equation_to_minterms(eqn, variables=("A", "B", "C", "D"))
    # mins = [1, 4, 8, 9, 12, 14]
    # print("Minterms:", mins)
    # dont_cares = {3, 7, 11, 15}
    # g4 = make_data_set(
    #     x_vars=("A", "B"), y_vars=("C", "D"),
    #     minterms=mins, dont_cares=dont_cares
    # )
    print(g4)
    # draw_kmap(g4, x_vars=("A", "B"), y_vars=("C", "D"), data_set=g4,
    #           save_fig="4-var.png")
    # eqn = "xy + yz′ + x'z'"
    eqn = "xy+yz'+x'z'"
    mins = equation_to_minterms(eqn, variables=("x", "y", "z"))

    print("Minterms:", mins)
    # dont_cares = {3, 7, 11, 15}
    # g4 = make_data_set(
    #     x_vars=("x"), y_vars=("y", "z"),
    #     minterms=mins
    # )
    # print(g4)
    draw_kmap(g4, x_vars=("A", "B"), y_vars=("C", "D"), data_set=g4,
              save_fig="3-var.png")
