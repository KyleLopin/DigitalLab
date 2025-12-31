# Copyright (c) 2025 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""

"""

__author__ = "Kyle Vitautas Lopin"

# standard libraries
from typing import Iterable

# installed libraries
import matplotlib.pyplot as plt


def draw_riscv_reg_table(filename: str | None = None):
    """
    Draw a RISC-V register table with columns:
    Name (ABI), Register (xN), Data (blank for students).

    Parameters
    ----------
    filename : str | None
        If provided, save the figure to this filename.
        If None, just show it.
    """
    # RISC-V integer register ABI names (RV32I/RV64I)
    # (index, ABI name)
    regs = [
        (0,  "zero"),
        (1,  "ra"),
        (2,  "sp"),
        (3,  "gp"),
        (4,  "tp"),
        (5,  "t0"),
        (6,  "t1"),
        (7,  "t2"),
        (8,  "s0/fp"),
        (9,  "s1"),
        (10, "a0"),
        (11, "a1"),
        (12, "a2"),
        (13, "a3"),
        (14, "a4"),
        (15, "a5"),
        (16, "a6"),
        (17, "a7"),
        (18, "s2"),
        (19, "s3"),
        (20, "s4"),
        (21, "s5"),
        (22, "s6"),
        (23, "s7"),
        (24, "s8"),
        (25, "s9"),
        (26, "s10"),
        (27, "s11"),
        (28, "t3"),
        (29, "t4"),
        (30, "t5"),
        (31, "t6"),
    ]

    # Header row
    table_data: list[list[str]] = [["Name", "Register", "Data"]]

    # Fill rows: ABI name, xN, blank data
    for idx, name in regs:
        reg_str = f"x{idx}"
        table_data.append([name, reg_str, ""])

    n_rows = len(table_data) - 1
    fig_height = max(4, n_rows * 0.3)
    fig, ax = plt.subplots(figsize=(5.5, fig_height))

    # Slightly wider last column for student writing
    col_widths = [0.25, 0.2, 0.55]

    table = ax.table(
        cellText=table_data,
        colLabels=None,
        loc="center",
        cellLoc="center",
        colWidths=col_widths,
    )

    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 1.2)

    # Style header row
    for col in range(3):
        cell = table[0, col]
        cell.set_text_props(weight="bold")
        cell.set_facecolor("#DDDDDD")

    ax.axis("off")
    plt.tight_layout()

    if filename is not None:
        fig.savefig(filename, bbox_inches="tight")
        plt.close(fig)
    else:
        plt.show()

    return fig, ax


def draw_ram_table(start_addr: int, n_rows: int, filename: str | None = None):
    """
    Draw a simple RAM table (Address, Data) using matplotlib.

    Parameters
    ----------
    start_addr : int
        Starting address (integer). Will be shown in binary.
    n_rows : int
        Number of rows (memory locations).
    filename : str | None, default=None
        If provided, save the figure to this filename. If None, just show it.

    Returns
    -------
    fig, ax : matplotlib Figure and Axes
    """
    # Compute address bit-width based on highest address
    max_addr = start_addr + n_rows - 1
    # Number of hex digits needed (at least 1)
    hex_digits = max(1, (max_addr.bit_length() + 3) // 4)
    addr_bits = max(1, max_addr.bit_length())  # enough bits to represent highest address

    # Build table data: header + rows
    table_data = [["Address", "Data"]]  # header row

    for i in range(n_rows):
        addr = start_addr + i
        addr_str = f"0x{addr:0{hex_digits}X}"  # hex with leading zeros, uppercase
        table_data.append([addr_str, ""])          # empty data cell for students to fill in

    # Figure size roughly proportional to row count
    fig_height = max(2, n_rows * 0.4)
    fig, ax = plt.subplots(figsize=(4, fig_height))

    # Create table
    table = ax.table(
        cellText=table_data,
        colLabels=None,     # header already in first row of cellText
        loc="center",
        cellLoc="center",
    )

    # Style tweaks
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 1.2)

    # Make header row bold / shaded
    header_cells = table[0, 0], table[0, 1]
    for cell in header_cells:
        cell.set_text_props(weight="bold")
        cell.set_facecolor("#DDDDDD")

    # Hide the axes
    ax.axis("off")

    # Tight layout so nothing gets cut off
    plt.tight_layout()

    # Save or show
    if filename is not None:
        fig.savefig(filename, bbox_inches="tight")
        plt.show()
    else:
        plt.show()

    return fig, ax


def draw_ram_io_table(inputs: Iterable[tuple[int, int, int]],
    outputs: Iterable[int | str] | None = None,
    extra_columns: dict[str, Iterable[str]] | None = None,
    col_widths = [0.12, 0.18, 0.08, 0.18],  # base 4
    filename: str | None = None):
    """
        Draw a RAM I/O table with columns:
        Addr, Data In, WE#, Data Out, and optional extra columns.

        Parameters
        ----------
        inputs : iterable of (addr, data_in, we)
            Each element is a tuple:
              addr     : int, address (displayed in hex)
              data_in  : int, data to write (hex)
              we       : int or bool, write enable (0/1)
        outputs : iterable of str, optional
            Partial list of Data Out values as strings
            (e.g. "0x00", "unknown", "Hi-Z", "X").
            If shorter than `inputs`, remaining cells are blank.
        extra_columns : dict[str, Iterable[str]] | None
            Extra columns to append. Keys are column titles,
            values are row entries (strings).
            If a column list is shorter than the number of rows,
            remaining cells are blank.
            Example:
                {
                    "Assembly": ["", "", "sw x5, 0(x1)", ""]
                }
        filename : str | None, default=None
            If provided, save the figure to this filename.
            If None, just show it.
        """
    outputs_list: list[int | str] = list(outputs) if outputs is not None else []
    extra_columns = extra_columns or {}

    # Compute hex widths based on max addr / data seen
    max_addr = max(addr for addr, _, _ in inputs if isinstance(addr, int))
    max_data_in = max(data_in for _, data_in, _ in inputs if isinstance(data_in, int))
    numeric_outs = [o for o in outputs_list if isinstance(o, int)]
    max_data_out = max(numeric_outs) if numeric_outs else 0

    max_data = max(max_data_in, max_data_out)

    # At least 1 hex digit
    addr_hex_digits = max(1, (max_addr.bit_length() + 3) // 4)
    data_hex_digits = max(1, (max_data.bit_length() + 3) // 4)

    # Base headers
    base_headers = ["Addr", "Data In", "WE#", "Data Out"]
    extra_headers = list(extra_columns.keys())
    headers = base_headers + extra_headers
    # Build table data: header + rows
    table_data: list[list[str]] = [headers]  # header row

    # Materialize extra column data as lists
    extra_lists: dict[str, list[str]] = {
        name: list(values) for name, values in extra_columns.items()
    }

    for i, (addr, data_in, we) in enumerate(inputs):
        if isinstance(addr, int):
            addr_str = f"0x{addr:0{addr_hex_digits}X}"
        else:
            addr_str = addr
        if isinstance(data_in, int):
            data_in_str = f"0x{data_in:0{data_hex_digits}X}"
        else:
            data_in_str = data_in
        if isinstance(we, int):
            we_str = str(int(we))
        else:
            we_str = we

        if i < len(outputs_list):
            out_val = outputs_list[i]
            if isinstance(out_val, int):
                data_out_str = f"0x{out_val:0{data_hex_digits}X}"
            else:
                data_out_str = str(out_val)
        else:
            data_out_str = ""

        row: list[str] = [addr_str, data_in_str, we_str, data_out_str]

        # Extra columns per row
        for name in extra_headers:
            col_vals = extra_lists.get(name, [])
            if i < len(col_vals):
                row.append(col_vals[i])
            else:
                row.append("")  # blank for student

        table_data.append(row)
    print("check")
    n_rows = len(table_data) - 1
    fig_height = max(2, n_rows * 0.4)
    fig, ax = plt.subplots(figsize=(6, fig_height))

    n_cols = len(headers)
    if n_cols > 4:
        extra = n_cols - 4
        # share remaining space among extra columns, or just dump into last one
        col_widths += [0.34 / extra] * extra

    table = ax.table(
        cellText=table_data,
        colLabels=None,  # header already in first row
        loc="center",
        cellLoc="center",
        colWidths=col_widths,
    )

    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 1.2)

    # Style header row
    for col in range(len(table_data[0])):
        cell = table[0, col]
        cell.set_text_props(weight="bold")
        cell.set_facecolor("#DDDDDD")

    ax.axis("off")
    plt.tight_layout()
    plt.show()
    if filename is not None:
        fig.savefig(filename, bbox_inches="tight")
        plt.close(fig)



if __name__ == "__main__":
    # Example: start at address 0, 8 rows, and save to a PDF
    # draw_ram_table(start_addr=160, n_rows=8, filename="ram_table_0_8.pdf")
    # ham
    # Example: another table starting at address 8, 8 rows, just show on screen
    # draw_ram_table(start_addr=8, n_rows=8)
    # Example usage:
    ops = [
        (0xA0, 0x12, 0),
        (0xA1, "unknown", 1),
        ("", "", ""),
        (0xA2, 0x34, 1),
        (0xA4, 0x56, 0),
        (0xA4, 0xA3, 1),
        (0xA3, 0x23, 0),
        (0xA4, 0x12, 0),
        (0xA4, "", 0),
        (0xA4, 0xFF, 1),
        (0xA2, 0xFF, 0),
        (0xA3, 0xFF, 0),
    ]

    outs = [""] * len(ops)
    outs[0] = 0x12
    outs[1] = "unknown"
    outs[9] = "0xBB"

    # code_column = ["lw                (0xA00)"]*len(ops)
    code_column = [""] * len(ops)
    code_column[0] = "sw s2, 0(sp)"
    code_column[1] = "lw s4, 1(sp)"
    code_column[2] = "sw x1, 2(x2)"

    # make 6th row
    ops[7] = ("", "", "")
    code_column[7] = "sw 0x23, 3(0xA00)"

    assembly = {"Assembly code:\nlw value, offset(base)": code_column}
    draw_ram_io_table(ops, outs, extra_columns=assembly)# , filename="ram_io_table_simple.pdf")
