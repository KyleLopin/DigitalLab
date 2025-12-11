# Copyright (c) 2025 Kyle Lopin (Naresuan University) <kylelopin@gmail.com>

"""

"""

__author__ = "Kyle Vitautas Lopin"

# installed libraries


from manim import *


def gray_code(n_bits: int):
    """Return list of Gray-code bit strings of length n_bits."""
    if n_bits == 0:
        return [""]
    if n_bits == 1:
        return ["0", "1"]
    prev = gray_code(n_bits - 1)
    return ["0" + b for b in prev] + ["1" + b for b in reversed(prev)]


class KarnaughMap(VGroup):
    """
    A simple Karnaugh map mobject for 2–4 variables.

    Parameters
    ----------
    num_vars : int
        Number of boolean variables (2, 3, or 4).
    values : dict[int, int|str] | list[int|str]
        Mapping from minterm index -> value (0, 1, or 'X').
        If a list is given, index = minterm.
    var_names : list[str] | None
        Variable names in order of significance, e.g. ["A", "B", "C", "D"].
    cell_size : float
        Size of each K-map cell.
    """

    def __init__(
        self,
        num_vars: int,
        values,
        var_names=None,
        cell_size: float = 0.9,
        gray_fontsize = 28,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.gray_fontsize = gray_fontsize
        assert 2 <= num_vars <= 4, "KarnaughMap currently supports 2–4 variables."
        self.num_vars = num_vars
        self.cell_size = cell_size

        # Normalize values to dict[minterm] -> value
        if isinstance(values, dict):
            self.values = values
        else:
            # Assume it's a list-like
            self.values = {i: v for i, v in enumerate(values)}

        if var_names is None:
            self.var_names = [chr(ord("A") + i) for i in range(num_vars)]
        else:
            self.var_names = var_names

        # Split vars into row and column variables
        # Example:
        # 2 vars: row = 1, col = 1   -> 2x2
        # 3 vars: row = 1, col = 2   -> 2x4
        # 4 vars: row = 2, col = 2   -> 4x4
        self.n_col_vars = num_vars // 2
        self.n_row_vars = num_vars - self.n_col_vars

        self.n_rows = 2**self.n_row_vars
        self.n_cols = 2**self.n_col_vars

        self.row_gray = gray_code(self.n_row_vars)
        self.col_gray = gray_code(self.n_col_vars)

        # Internal storage
        self.cell_squares = {}  # (r, c) -> Square
        self.cell_texts = {}    # (r, c) -> Text
        self.minterm_to_rc = {} # minterm -> (r, c)

        # Build everything
        self._build_map()

    # ------------------------------------------------------------------
    # Construction helpers
    # ------------------------------------------------------------------

    def _build_map(self):
        cell_size = self.cell_size

        # Draw cells in a grid
        cells_group = VGroup()
        for r in range(self.n_rows):
            for c in range(self.n_cols):
                sq = Square(side_length=cell_size)
                # position: columns go +x, rows go -y
                sq.move_to(
                    np.array([
                        (c - (self.n_cols - 1) / 2) * cell_size,
                        - (r - (self.n_rows - 1) / 2) * cell_size,
                        0,
                    ])
                )
                sq.set_stroke(WHITE, 1)
                self.cell_squares[(r, c)] = sq
                cells_group.add(sq)

        # Map minterms -> (row, col) using Gray code ordering
        for m in range(2**self.num_vars):
            bits = f"{m:0{self.num_vars}b}"
            row_bits = bits[self.n_col_vars :]
            col_bits = bits[: self.n_col_vars]

            # Find row/col index from Gray code table
            r = self.row_gray.index(row_bits) if self.n_row_vars > 0 else 0
            c = self.col_gray.index(col_bits) if self.n_col_vars > 0 else 0
            self.minterm_to_rc[m] = (r, c)

            # If we have a value, put it in the corresponding cell
            val = self.values.get(m, None)
            if val is not None:
                txt = Text(str(val), font_size=32)
                txt.move_to(self.cell_squares[(r, c)].get_center())
                self.cell_texts[(r, c)] = txt

        # Row Gray labels (to the LEFT of the whole grid)
        row_label_group = VGroup()

        for r, bits in enumerate(self.row_gray):
            if bits == "":
                continue
            label = Text(bits, font_size=self.gray_fontsize)
            label.next_to(cells_group, LEFT, buff=0.2)
            row_center = self.cell_squares[(r, 0)].get_center()
            label.set_y(row_center[1])  # row_center is (x, y) so [1] for y
            row_label_group.add(label)

        # Column Gray labels
        col_label_group = VGroup()

        for c, bits in enumerate(self.col_gray):
            if bits == "":
                continue
            label = Text(bits, font_size=self.gray_fontsize)
            col_center = self.cell_squares[(0, c)].get_center()
            label.next_to(cells_group, UP, buff=0.2)
            label.set_x(col_center[0])  # row_center is (x, y) so [0] for x
            col_label_group.add(label)

        # Variable names (e.g. AB on rows, CD on cols)
        row_var_name = (
            "".join(self.var_names[self.n_col_vars :])
            if self.n_row_vars > 0
            else ""
        )
        col_var_name = (
            "".join(self.var_names[: self.n_col_vars])
            if self.n_col_vars > 0
            else ""
        )

        var_label_group = VGroup()
        if row_var_name:
            row_name_text = Text(row_var_name, font_size=28)
            # left of the row labels
            if len(row_label_group) > 0:
                row_name_text.next_to(row_label_group, LEFT, buff=0.3)
            else:
                # fallback: left of cells
                row_name_text.next_to(cells_group, LEFT, buff=0.6)
            var_label_group.add(row_name_text)

        if col_var_name:
            col_name_text = Text(col_var_name, font_size=28)
            # above the column labels
            if len(col_label_group) > 0:
                col_name_text.next_to(col_label_group, UP, buff=0.3)
            else:
                col_name_text.next_to(cells_group, UP, buff=0.6)
            var_label_group.add(col_name_text)

        # Add everything to this VGroup
        self.cells_group = cells_group
        self.row_label_group = row_label_group
        self.col_label_group = col_label_group
        self.var_label_group = var_label_group

        self.add(
            cells_group,
            row_label_group,
            col_label_group,
            *self.cell_texts.values(),
            var_label_group,
        )

    # ------------------------------------------------------------------
    # Animation helpers (similar flavor to your TruthTable class)
    # ------------------------------------------------------------------

    def write_all(self, run_time=1.0):
        """
        Reveal the entire map: cell grid, labels, and values.
        """
        anims = []
        # Cells and labels
        for mob in [
            self.cells_group,
            self.row_label_group,
            self.col_label_group,
            self.var_label_group,
        ]:
            if mob is not None and len(mob) > 0:
                anims.append(FadeIn(mob))
        # Values
        for txt in self.cell_texts.values():
            anims.append(Write(txt))

        return LaggedStart(*anims, lag_ratio=0.05, run_time=run_time)

    def write_cells(self, run_time=1.0):
        """
        Reveal only the cell values (assuming map outline already drawn).
        """
        anims = [Write(txt) for txt in self.cell_texts.values()]
        return LaggedStart(*anims, lag_ratio=0.05, run_time=run_time)

    # ------------------------------------------------------------------
    # Utility methods
    # ------------------------------------------------------------------

    def get_cell_from_minterm(self, m):
        """
        Return (square, text) for a given minterm index.
        """
        rc = self.minterm_to_rc.get(m, None)
        if rc is None:
            return None, None
        return self.cell_squares[rc], self.cell_texts.get(rc, None)

    def highlight_group(self, minterms, color=YELLOW,
                        buff=-0.10, stroke_width=3,
                        corner_radius=0.3):
        """
        Draw a rounded rectangle around a group of minterms and return it.

        This just computes and returns the implicant outline; it does NOT
        add it to the scene automatically. You use it like any other
        Manim mobject:

        Basic usage
        -----------
        >>> implicant = kmap.highlight_group([1, 3], color=RED)
        >>> self.play(Create(implicant))        # draw the implicant
        >>> self.wait()

        Change color / thickness
        ------------------------
        >>> self.play(
        ...     implicant.animate.set_stroke(color=YELLOW, width=5)
        ... )

        Remove implicant
        ----------------
        >>> self.play(FadeOut(implicant))

        Pulse highlight (grow + thicken then return)
        --------------------------------------------
        >>> implicant2 = kmap.highlight_group([1, 5], color=BLUE)
        >>> self.play(Create(implicant2))
        >>> implicant2.save_state()  # store original size & style
        >>> self.play(
        ...     implicant2.animate.scale(1.15).set_stroke(width=6),
        ...     run_time=0.2,
        ... )
        >>> self.play(
        ...     Restore(implicant2),
        ...     run_time=0.2,
        ... )

        Parameters
        ----------
        minterms : iterable[int]
            List of minterm indices to group (e.g. [1, 3, 5, 7]).
        color : Manim color
            Stroke color of the implicant outline.
        buff : float
            How far inside/outside the group of cells to draw the box.
            Negative values shrink the box slightly inside the cell edges.
        stroke_width : float
            Line thickness of the outline.
        corner_radius : float
            Radius of rounded corners.

        Returns
        -------
        Mobject
            A SurroundingRectangle (rounded) around the given group.
        """
        cells = []
        for m in minterms:
            sq, _ = self.get_cell_from_minterm(m)
            if sq is not None:
                cells.append(sq)

        if not cells:
            return VGroup()

        box = SurroundingRectangle(
            VGroup(*cells),
            buff=buff,
            color=color,
            stroke_width=stroke_width,
            corner_radius=corner_radius,
        )
        return box

class KMapDemo(Scene):
    def construct(self):
        # Example: 3-variable function f(A,B,C) with 1's at minterms 1, 3, 5, 7
        num_vars = 3
        ones = [1, 3, 5, 6, 7]
        values = {m: 1 for m in ones}
        # others default to 0
        for m in range(2**num_vars):
            values.setdefault(m, 0)

        kmap = KarnaughMap(num_vars, values, var_names=["A", "B", "C"])
        kmap.to_edge(LEFT)

        self.play(kmap.write_all(run_time=2.0))
        self.wait(1)

        # Highlight a group, e.g. minterms 1 and 3

        implicant = kmap.highlight_group([1, 3], color=RED)
        self.play(Create(implicant))
        self.wait(1)

        # change color
        self.play(implicant.animate.set_stroke(color=YELLOW))
        self.wait(2)

        # redraw implicant
        self.play(Create(implicant))
        self.wait(2)

        # remove implicant
        self.play(FadeOut(implicant))
        self.wait(2)
        # change implicant color
        implicant2 = kmap.highlight_group([1, 5], color=BLUE)
        self.play(Create(implicant2))
        self.wait(2)

        implicant2.save_state()
        self.play(
            implicant2.animate.scale(1.15).set_stroke(width=6),  # grow a bit
            run_time=0.2,
        )
        self.play(
            Restore(implicant2),  # shrink back to saved state
            run_time=0.2,
        )

        # Highlight a variable
        # === Highlight the variable A (column variable name) ===
        A_label = kmap.var_label_group[1]  # "A" for your 3-var layout

        # Option 1: change color
        self.play(A_label.animate.set_color(YELLOW), run_time=1)

        # Option 2: add a small box around it
        # A_box = SurroundingRectangle(A_label, buff=0.1, color=YELLOW)
        # self.play(Create(A_box), run_time=0.3)
        # self.wait(1)

        # Optional: pulse the label
        A_label.save_state()
        self.play(A_label.animate.scale(1.2), run_time=0.2)
        self.play(Restore(A_label), run_time=0.2)
        self.wait(1)
