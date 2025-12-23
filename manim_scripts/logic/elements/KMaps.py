# Copyright (c) 2025 Kyle Lopin (Naresuan University) <kylelopin@gmail.com>

"""

"""

__author__ = "Kyle Vitautas Lopin"

# installed libraries


from manim import *

config.font = "Menlo"
config.max_files_cached = 500


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
        num_vars: int, var_names=None, values=None,
        minterms=None, dont_cares=None,
        cell_size: float = 0.9, gray_fontsize = 28,
        value_fontsize = 32,
        stroke_width=2,
        default_zero: bool = True,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.gray_fontsize = gray_fontsize
        self.stroke_width = stroke_width
        assert 2 <= num_vars <= 4, "KarnaughMap currently supports 2–4 variables."
        self.num_vars = num_vars
        self.cell_size = cell_size
        n_cells = 2 ** num_vars
        # ---- Build values from minterms/dont_cares if provided ----
        if minterms is not None or dont_cares is not None:
            mset = set(minterms or [])
            dset = set(dont_cares or [])

            # start with all 0 (or None, if you prefer blanks)
            base = "0" if default_zero else ""
            self.values = {i: base for i in range(n_cells)}

            for i in mset:
                self.values[i] = "1"
            for i in dset:
                self.values[i] = "X"

        # ---- Otherwise, fall back to explicit values input ----
        else:
            if values is None:
                values = {}
                # raise ValueError("Provide either values=... or minterms=... (optionally dont_cares=...).")

            if isinstance(values, dict):
                self.values = values
            else:
                # list/tuple/etc
                if len(values) != n_cells:
                    raise ValueError(f"values must have length {n_cells} for num_vars={num_vars}")
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
                sq.set_stroke(WHITE, self.stroke_width)
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
                txt = Text(str(val), font_size=value_fontsize)
                txt.move_to(self.cell_squares[(r, c)].get_center())
                self.cell_texts[(r, c)] = txt
        print("cell text init: ", self.cell_texts)

        # Row Gray labels (to the LEFT of the whole grid)
        self.row_gray_digits = []  # list of VGroups, one per row
        self.row_label_group = VGroup()

        for r, bits in enumerate(self.row_gray):
            if bits == "":
                continue
            digits = VGroup(*[Text(ch, font_size=self.gray_fontsize)
                              for ch in bits])
            digits.arrange(RIGHT, buff=0.08)  # tight spacing
            anchor = self.cell_squares[(r, 0)].get_left()
            digits.next_to(anchor, LEFT, buff=0.2)  # or your outside-grid placement
            self.row_label_group.add(digits)
            self.row_gray_digits.append(digits)

        print("check: ", self.row_label_group)
        # Column Gray labels
        self.col_label_group = VGroup()
        self.col_gray_digits = []

        for c, bits in enumerate(self.col_gray):
            if bits == "":
                continue
            digits = VGroup(*[Text(ch, font_size=self.gray_fontsize) for ch in bits])
            digits.arrange(RIGHT, buff=0.02)  # tight spacing
            anchor = self.cell_squares[(0, c)].get_top()
            digits.next_to(anchor, UP, buff=0.2)  # or your outside-grid placement

            # col_center = self.cell_squares[(0, c)].get_center()
            # label.next_to(cells_group, UP, buff=0.2)
            # label.set_x(col_center[0])  # row_center is (x, y) so [0] for x
            self.col_label_group.add(digits)
            self.col_gray_digits.append(digits)

        # make some attributes to save to use in methods to get parts easier
        self.var_name_to_text = {}


        # Row variable names as individual letters (e.g. "B", "C")
        self.row_var_labels = VGroup()
        self.row_vars = self.var_names[self.n_col_vars:]  # e.g. ["B", "C"]

        for name in self.row_vars:
            label = Text(name, font_size=28)
            self.row_var_labels.add(label)
            self.var_name_to_text[name] = label

        if len(self.row_var_labels) > 0:
            # Put B and C NEXT TO EACH OTHER:  B   C
            self.row_var_labels.arrange(RIGHT, buff=0.1)

            # Put the whole stack to the LEFT of the row Gray labels
            if len(self.row_label_group) > 0:
                self.row_var_labels.next_to(self.row_label_group, LEFT, buff=0.3)
                self.row_var_labels.set_y(self.row_label_group.get_center()[1])
            else:
                self.row_var_labels.next_to(self.cells_group, LEFT, buff=0.6)
                self.row_var_labels.set_y(self.cells_group.get_center()[1])

        # Column variable names as individual letters
        self.col_var_labels = VGroup()
        self.col_vars = self.var_names[: self.n_col_vars]  # e.g. ["A"]

        # Build the labels
        for name in self.col_vars:
            label = Text(name, font_size=28)
            self.col_var_labels.add(label)
            self.var_name_to_text[name] = label

        for i, name in enumerate(self.col_vars):
            if len(self.col_label_group) > 0:
                self.col_var_labels.next_to(self.col_label_group, UP, buff=0.3)
            else:
                self.col_var_labels.next_to(self.cells_group, UP, buff=0.6)
        self.add(self.row_var_labels, self.col_var_labels)

        # Add everything to this VGroup
        self.cells_group = cells_group
        # self.var_label_group = var_label_group
        print("ddfr: ", self.row_var_labels)
        self.add(
            cells_group,
            self.row_label_group,
            self.col_label_group,
            *self.cell_texts.values(),
            self.row_var_labels,
            self.col_var_labels
        )

    # ------------------------------------------------------------------
    # Animation helpers (similar flavor to TruthTable class)
    # ------------------------------------------------------------------

    def write(self, items = "all", run_time=1.0):
        """
        Reveal the entire map: cell grid, labels, and values.
        """
        anims = []
        mobs = []
        if items == "all":
            mobs = [self.cells_group, self.row_label_group,
            self.col_label_group, self.row_var_labels,
            self.col_var_labels]
        elif items == "table":
            mobs = [self.cells_group]
        elif items == "vars":
            mobs = [self.row_var_labels, self.col_var_labels]
        elif items == "labels":
            mobs = [self.row_label_group, self.col_label_group]


        # Cells and labels
        for mob in mobs:
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
        print("cell texts: ", self.cell_texts)
        return LaggedStart(*anims, lag_ratio=0.05, run_time=run_time)

    def write_cell(self, row, col, value, run_time=0.4):
        """
        Ensure the cell (row,col) displays `value`.
        If the text isn't in the scene yet -> Write it.
        If it's already shown -> Transform it to new text.
        """
        key = (row, col)
        print("cell texts: ", self.cell_texts, self.cell_texts.values())
        old_txt = self.cell_texts[key]  # existing Tex/MathTex mobject

        new_txt = Tex(str(value))
        new_txt.match_style(old_txt)
        new_txt.move_to(old_txt)

        # If old_txt has been added to a Scene already, it will have a non-empty parents list.
        # This is a common, practical heuristic.
        is_on_screen = (len(old_txt.parents) > 0)

        if not is_on_screen:
            # Replace stored object so future updates target the visible one
            self.cell_texts[key] = new_txt
            # Also swap it into the group so later .add(self) includes the right object
            self.replace(old_txt, new_txt)
            return Write(new_txt, run_time=run_time)

        # Already visible: transform
        self.cell_texts[key] = new_txt
        self.replace(old_txt, new_txt)
        return Transform(old_txt, new_txt, run_time=run_time)

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
        print("rc: ", rc, self.cell_texts.get(rc, None), self.cell_texts)
        return self.cell_squares[rc], self.cell_texts.get(rc, None)

    def get_var_label(self, var: str) -> Mobject:
        return self.var_name_to_text[var]

    def get_var_digits(self, var: str, value: int) -> VGroup:
        """
            Return the Text objects for the bit corresponding to (var=value) in the Gray-code labels.

            Example:
                get_var_digits("B", 0) returns the '0' digit in the row labels "00" and "01"
                (assuming rows are BC and Gray-ordered).
            """
        bit = str(value)

        if var in self.col_vars:
            k = self.col_vars.index(var)  # which digit inside the column Gray strings
            hits = []
            for c, bits in enumerate(self.col_gray):
                if bits[k] == bit:
                    hits.append(self.col_gray_digits[c][k])  # digit object
            return VGroup(*hits)

        if var in self.row_vars:
            k = self.row_vars.index(var)  # which digit inside the row Gray strings
            hits = []
            for r, bits in enumerate(self.row_gray):
                if bits[k] == bit:
                    hits.append(self.row_gray_digits[r][k])
            return VGroup(*hits)

        return VGroup()

    def pulse_var_digits(
            self, var: str, value: int,
            scale_factor: float = 1.5, color=GREEN,
            about: str = "center",  # "center" or "bottom"
            run_time: float = 0.25,
    ):
        """
        Pulse the Gray-code digits corresponding to (var = value),
        scaling each digit independently so they don't shift.

        Returns (pulse_animation, digits_group_to_restore).

        Usage:
            pulse_anim, restore_target = kmap.pulse_var_digits_with_restore("B", 0)
            self.play(pulse_anim)
            self.play(Restore(restore_target))
        """

        digits = self.get_var_digits(var, value)

        digits.save_state()

        if digits is None or len(digits) == 0:
            return AnimationGroup()

        if about == "bottom":
            anims = [
                d.animate
                .scale(scale_factor, about_point=d.get_bottom())
                .set_color(color)
                for d in digits
            ]
        else:
            # default: anchor each digit to its own center
            anims = [
                d.animate
                .scale(scale_factor, about_point=d.get_center())
                .set_color(color)
                for d in digits
            ]

        return AnimationGroup(*anims, lag_ratio=0.0, run_time=run_time), digits

    def get_var_minterms(self, var: str, value: int) -> list[int]:
        """
        Return list of minterm indices where var == value.

        Assumes minterm bits are ordered like self.var_names:
            bits = f"{m:0{self.num_vars}b}" corresponds to ["A","B","C",...]
        """
        bit = str(value)
        i = self.var_names.index(var)

        out = []
        for m in range(2 ** self.num_vars):
            bits = f"{m:0{self.num_vars}b}"
            if bits[i] == bit:
                out.append(m)
        return out

    def get_var_cell_texts(self, var: str, value: int) -> VGroup:
        """
        Return a VGroup of the *cell value* Text objects for all minterms where var==value.
        Only returns cells that actually have a Text object (i.e., were created in _build_map).
        """
        mins = self.get_var_minterms(var, value)
        hits = []
        for m in mins:
            rc = self.minterm_to_rc.get(m, None)
            if rc is None:
                continue
            txt = self.cell_texts.get(rc, None)
            if txt is not None:
                hits.append(txt)
        return VGroup(*hits)

    def pulse_var_cells(
            self, var: str, value: int,
            scale_factor: float = 1.3,
            color=GREEN, run_time: float = 0.25):
        """
        Pulse the *cell numbers* (Text in cells) for all minterms where var==value.
        Scales each cell Text independently (no shifting weirdness).
        """
        texts = self.get_var_cell_texts(var, value)
        if texts is None or len(texts) == 0:
            return AnimationGroup()

        anims = [
            t.animate.scale(scale_factor, about_point=t.get_center()).set_color(color)
            for t in texts
        ]
        return AnimationGroup(*anims, lag_ratio=0.0, run_time=run_time)

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
        Text.set_default(font="Menlo")
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
        A_label = kmap.col_var_labels  # "A" for your 3-var layout
        A_label = kmap.get_var_label("A")
        # Option 1: change color
        self.play(A_label.animate.set_color(YELLOW), run_time=1)

        A_label = kmap.get_var_label("B")
        # Option 1: change color
        self.play(A_label.animate.set_color(BLUE), run_time=1)

        # Option 2: add a small box around it
        # A_box = SurroundingRectangle(A_label, buff=0.1, color=YELLOW)
        # self.play(Create(A_box), run_time=0.3)
        # self.wait(1)

        # Optional: pulse the label
        A_label.save_state()
        self.play(A_label.animate.scale(1.2), run_time=0.2)
        self.play(Restore(A_label), run_time=0.2)
        self.wait(1)
        A_nums = kmap.col_label_group

        A_nums = kmap.col_label_group  # VGroup of "0", "1" at the top

        A0 = A_nums[0]
        A1 = A_nums[1]

        # highlight A=1
        box = SurroundingRectangle(A1, buff=0.08, color=YELLOW)
        self.play(Create(box))
        self.play(A1.animate.set_color(YELLOW))

        self.wait(1)

        A1.save_state()
        self.play(A0.animate.scale(1.25).set_color(YELLOW), run_time=0.2)
        self.play(Restore(A1), run_time=0.2)

        # rows 0 and 1 are "00" and "01" in Gray order
        B_digit_in_00 = kmap.row_label_group[0][0]
        B_digit_in_01 = kmap.row_label_group[1][0]

        self.play(
            B_digit_in_00.animate.set_color(YELLOW),
            B_digit_in_01.animate.set_color(YELLOW),
        )

        # B0 = kmap.get_var_digits("B", 0)
        # self.play(
        #     B0.animate.scale(1.5,
        #                      about_point=B0.get_bottom()
        #                      ).set_color(GREEN),
        # )
        # self.play(
        #     B0.animate.scale(1.0).set_color(GREEN),
        # )

        pulse_anim, restore_target = kmap.pulse_var_digits("B", 0,
                                        scale_factor=2, color=YELLOW)
        self.play(pulse_anim, run_time=0.5)
        self.play(Restore(restore_target), run_time=0.2)

        # Save state (so Restore works)
        cells = kmap.get_var_cell_texts("B", 0)
        cells.save_state()

        # Pulse all cell values where B=0
        self.play(kmap.pulse_var_cells("B", 0, scale_factor=1.4, color=YELLOW, run_time=0.2))

        # Restore them
        self.play(Restore(cells), run_time=0.2)

        # change minTerm colors:
        cells = kmap.get_var_cell_texts("B", 1)

        # 1) color change (permanent)
        self.play(cells.animate.set_color(RED), run_time=0.2)
