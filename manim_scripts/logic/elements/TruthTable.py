# Copyright (c) 2025 Kyle Lopin (Naresuan University) <kylelopin@gmail.com>

"""

"""

__author__ = "Kyle Vitautas Lopin"

# installed libraries
from manim import *


class TruthTable(VGroup):
    """
    A simple truth table generator.

    Parameters
    ----------
    inputs : list[str]
        Names of input variables, e.g. ["A", "B", "C"].
    outputs : list[str]
        Names of output variables, e.g. ["F"] or ["x"].
        (Right now we assume one output and use `minterms` for that.)
    minterms : list[int] | None
        Integer indices (0..2^n - 1) where the *first* output is 1.
        If None, outputs are left blank.
    dont_cares : list[int] | None
        Optional: indices that should be shown as "X" instead of 0/1.
    table_config : dict
        Extra kwargs passed to manim.Table (e.g., h_buff, v_buff, etc.).
    """

    def __init__(
        self,
        inputs, outputs,
        minterms=None,
        dont_cares=None,
        table_config=None,
        scale = 1,
        font_size=58,
        **kwargs,
    ):
        super().__init__(**kwargs)

        if table_config is None:
            table_config = dict(h_buff=0.4, v_buff=0.2)

        self.inputs = list(inputs)
        self.outputs = list(outputs)
        # this works for 1 output
        # self.minterms = set(minterms or [])
        # self.dont_cares = set(dont_cares or [])

        # ---- normalize minterms for multi-output ----
        # One output: minterms = [1,3,4]
        # Multi-output: minterms = [[...], [...], ...]
        n_outputs = len(self.outputs)
        print(n_outputs)
        if n_outputs == 1:
            minterm_lists = [minterms or []]
        else:
            # ensure we have a list per output
            minterm_lists = minterms or [[] for _ in range(n_outputs)]
        print(minterm_lists)
        self.minterm_sets = [set(lst) for lst in minterm_lists]
        if dont_cares is None:
            dont_care_lists = [[] for _ in range(n_outputs)]
        elif n_outputs == 1:
            dont_care_lists = [dont_cares]
        else:
            dont_care_lists = dont_cares
        self.dont_care_sets = [set(lst) for lst in dont_care_lists]

        n_inputs = len(self.inputs)
        num_rows = 2 ** n_inputs

        # Build rows: each row = input bits + output bits (as strings)
        body_rows = []

        for i in range(num_rows):
            # binary representation of the input combination
            input_bits = list(f"{i:0{n_inputs}b}")

            # output bits for each output column
            out_vals = []
            for j in range(n_outputs):
                if i in self.dont_care_sets[j]:
                    out_vals.append("X")
                elif i in self.minterm_sets[j]:
                    out_vals.append("1")
                else:
                    out_vals.append("0")

            body_rows.append(input_bits + out_vals)

        headers = self.inputs + self.outputs
        col_labels = [Text(h) for h in headers]

        # --- store label lookup ---
        self.headers = headers
        self.col_labels = col_labels

        self.col_index = {name: i for i, name in enumerate(headers)}  # "A" -> 0, "B" -> 1, ...
        self.label_by_name = {name: lbl for name, lbl in zip(headers, col_labels)}  # "A" -> Text("A")

        # Create the actual manim Table
        table = Table(
            body_rows,
            col_labels=col_labels,
            element_to_mobject=lambda x: Text(str(x)),
            include_outer_lines=False,
            **table_config,
        )

        # Center it nicely by default (you can still shift/scale it later)
        scale = scale*0.6  # 0.6 fills the window
        table.scale(scale)

        self.table = table
        self.add(table)

        # ---- store col labels as inputs vs outputs ----
        self.input_labels = col_labels[:n_inputs]
        print("self.input_labels: ", self.input_labels)
        self.output_labels = col_labels[n_inputs:]

        self.rows = table.get_rows()
        self.header_rows = self.rows[0]
        self.body_rows = self.rows[1:]

        # header visible, body hidden initially
        for r in self.rows:
            r.set_opacity(0)

        # Save the lines below variables and between input and outputs
        horizontal_lines = table.get_horizontal_lines()
        vertical_lines = table.get_vertical_lines()

        # make ALL lines invisible first
        for line in horizontal_lines:
            line.set_opacity(0)
        for line in vertical_lines:
            line.set_opacity(0)

        # safety checks in case manim internals differ a bit
        header_line_index = 0  # underline under labels
        sep_line_index = n_inputs - 1  # between inputs and outputs

        self.header_line = None
        self.sep_line = None

        # print("test lens: ", len(horizontal_lines), len(vertical_lines))
        # print(f"header_line_index: {header_line_index}; sep_line_index: {sep_line_index}")
        if len(horizontal_lines) > header_line_index:
            self.header_line = horizontal_lines[header_line_index]
            self.header_line.set_stroke(width=5)
            self.header_line.set_opacity(0)

        if len(vertical_lines) > sep_line_index:
            self.sep_line = vertical_lines[sep_line_index]
            self.sep_line.set_stroke(width=5)
            self.sep_line.set_opacity(0)

    def get_label(self, name: str) -> Text:
        """Return the header Text mobject for 'A', 'B', 'F', etc."""
        if name not in self.label_by_name:
            raise ValueError(f"Unknown label {name!r}. Valid: {list(self.label_by_name)}")
        return self.label_by_name[name]

    def get_var_label(self, name: str) -> Text:
        """
        Return the header label Text for an *input* variable.

        Parameters
        ----------
        name : str
            Input variable name (must be in `self.inputs`), e.g. "A", "B", "C".

        Returns
        -------
        Text
            The header Text mobject for that input variable.

        Raises
        ------
        ValueError
            If `name` is not one of the configured input names.
        """
        if name not in self.inputs:
            raise ValueError(f"{name!r} not in inputs {self.inputs}")
        return self.get_label(name)

    def get_var_digits(self, row: int, col: int | str) -> Mobject:
        """
        Convenience alias for `get_cell()` when you want an input-bit cell.

        This returns the body cell mobject at (row, col). `col` may be an integer
        column index or a header name (e.g. "A").

        Parameters
        ----------
        row : int
            0-based index into the body (does not include the header row).
        col : int | str
            Column index or column name.

        Returns
        -------
        Mobject
            The cell mobject (typically a VGroup containing the cell background and text).
        """
        return self.get_cell(row=row, col=col)

    def get_output_label(self, name: str) -> Text:
        """
        Return the header label Text for an *output* variable.

        Parameters
        ----------
        name : str
            Output variable name (must be in `self.outputs`), e.g. "F", "x", "y".

        Returns
        -------
        Text
            The header Text mobject for that output variable.

        Raises
        ------
        ValueError
            If `name` is not one of the configured output names.
        """
        if name not in self.outputs:
            raise ValueError(f"{name!r} not in outputs {self.outputs}")
        return self.get_label(name)

    def get_cell(self, row: int, col: int | str) -> Mobject:
        """
            Return the header label Text for an *output* variable.

            Parameters
            ----------
            name : str
                Output variable name (must be in `self.outputs`), e.g. "F", "x", "y".

            Returns
            -------
            Text
                The header Text mobject for that output variable.

            Raises
            ------
            ValueError
                If `name` is not one of the configured output names.
            """
        if name not in self.outputs:
            raise ValueError(f"{name!r} not in outputs {self.outputs}")
        return self.get_label(name)

    def get_cell(self, row: int, col: int | str) -> Mobject:
        """
        Return a body cell mobject at (row, col).

        Notes
        -----
        - `row` is indexed into the table body (header row is not included).
        - `col` can be either a 0-based integer index or a column header name
          like "A", "B", "x", etc.

        Parameters
        ----------
        row : int
            0-based body row index.
        col : int | str
            0-based column index or a column header name.

        Returns
        -------
        Mobject
            The cell mobject (often a VGroup containing the background + Text).

        Raises
        ------
        ValueError
            If `col` is a string that is not a valid column header.
        IndexError
            If `row` or integer `col` is out of range.
        """
        if isinstance(col, str):
            col = self.get_col(col)
        return self.body_rows[row][col]

    def get_body_size(self)->int:
        """
        Return the body dimensions as a string formatted like "rows x cols".

        Returns
        -------
        str
            Size of the body (not including the header), e.g. "8x5" for 8 body rows
            and 5 columns total.
        """
        return f"{len(self.body_rows)}x{len(self.body_rows[0])}"

    def get_col(self, name: str) -> int:
        """0-based column index for a header name."""
        if name not in self.col_index:
            raise ValueError(
                f"Unknown column {name!r}. "
                f"Valid columns: {list(self.col_index.keys())}"
            )
        return self.col_index[name]

    # ========== animation helper methods ==========

    def draw_lines(self, run_time=0.5) -> Animation:
        """
        Animate the underline beneath the header and the vertical separator line.

        Parameters
        ----------
        run_time : float
            Duration of the animation in seconds.

        Returns
        -------
        AnimationGroup
            Animation that fades in the header underline and the input/output separator
            (if they exist for this table).
        """
        anims = []
        print(self.header_line, self.sep_line)
        if self.header_line is not None:
            anims.append(self.header_line.animate.set_opacity(1))
        if self.sep_line is not None:
            anims.append(self.sep_line.animate.set_opacity(1))
        return AnimationGroup(*anims, run_time=run_time)

    def write_inputs(self, run_time=0.5) -> Animation:
        """Animations to write input variable labels (A, B, C, ...)."""
        anims = [lbl.animate.set_opacity(1) for lbl in self.input_labels]
        print("write: ", anims)
        return AnimationGroup(*anims, lag_ratio=0.1, run_time=run_time)

    def write_outputs(self, run_time=0.5) -> Animation:
        """Animations to write output variable labels (F, x, ...)."""
        anims = [lbl.animate.set_opacity(1) for lbl in self.output_labels]
        return AnimationGroup(*anims, lag_ratio=0.1, run_time=run_time)

    def write_body(self, run_time=1.0) -> Animation:
        """Animations to reveal the rows of the truth table."""
        anims = [r.animate.set_opacity(1) for r in self.body_rows]
        print(self.body_rows)
        # LaggedStart = row-by-row reveal
        return LaggedStart(*anims, lag_ratio=0.15, run_time=run_time)

    def write_all(self, run_time=1.0) -> Animation:
        """Animations to reveal the rows of the truth table."""
        anims = []
        if self.header_line is not None:
            anims.append(self.header_line.animate.set_opacity(1))
        if self.sep_line is not None:
            anims.append(self.sep_line.animate.set_opacity(1))
        anims.extend([r.animate.set_opacity(1) for r in self.rows])

        # LaggedStart = row-by-row reveal
        return LaggedStart(*anims, lag_ratio=0.15, run_time=run_time)


class TruthTableExample(Scene):
    def construct(self):
        tt = TruthTable(
            inputs=["A", "B", "C"],
            outputs=["x", "y"],
            minterms=[[1, 3, 4], [0, 2, 5, 6]],
            dont_cares=[[2], [1]]
        )
        tt.to_edge(UP)

        # 1) draw the two lines
        self.play(tt.draw_lines(run_time=1))
        self.wait(1)

        # 2) write input labels (A, B, C)
        self.play(tt.write_inputs(run_time=2))
        self.wait(1)

        # 3) write output labels (x)
        self.play(tt.write_outputs(run_time=2))
        self.wait(1)
        #
        # 4) fill in the table rows
        self.play(tt.write_body(run_time=2))
        self.wait(1)

        self.play(tt.write_all())
        self.wait(1)

        # ==========================================================
        # Cheat-sheet demo: call ALL non-write methods with visuals
        # ==========================================================

        def highlight(mob, label_text, direction=RIGHT, color=YELLOW):
            """Draw a box around mob and show a tiny callout label next to it."""
            # box = SurroundingRectangle(mob, buff=0.08, color=color, stroke_width=4)
            tag = Text(label_text, font_size=22).next_to(mob, direction, buff=0.25)
            tag.set_fill(color)
            self.play(FadeIn(tag), run_time=0.6)
            self.wait()
            return tag

        # 1) get_body_size()
        size_str = tt.get_body_size()
        size_label = Text(f"tt.get_body_size() -> {size_str}", font_size=24)
        size_label.next_to(tt, DOWN, buff=0.6)
        self.play(FadeIn(size_label), run_time=0.5)
        self.wait(0.8)

        # 2) get_label(name) and 3) get_var_label(name)
        #    (both return the header Text mobject)
        lbl_A = tt.get_label("A")
        lbl_A.set_color(YELLOW)
        highlight(lbl_A, 'tt.get_label("A")', direction=LEFT, color=YELLOW)

        lbl_B = tt.get_var_label("B")
        lbl_B.set_color(GREEN)
        highlight(lbl_B, 'tt.get_var_label("B")', direction=UP, color=GREEN)

        # 4) get_output_label(name)
        lbl_y = tt.get_output_label("y")
        lbl_y.set_color(PURPLE)
        highlight(lbl_y, 'tt.get_output_label("y")', direction=RIGHT, color=PURPLE)

        # 5) get_col(name) (show the index textually, then highlight that column's header)
        col_idx_c = tt.get_col("C")
        idx_label = Text(f'tt.get_col("C") -> {col_idx_c}', font_size=24)
        idx_label.next_to(size_label, DOWN, buff=0.6)
        self.play(FadeIn(idx_label), run_time=0.4)
        self.wait(0.8)

        # 6) get_cell(row, col) (body cell) + 7) get_var_digits(row, col)
        # Pick a body row and a couple columns to show.
        r = 2  # 0-based in body (not counting header)
        cA = tt.get_col("A")
        cX = tt.get_col("x")

        cell_A = tt.get_cell(row=r, col=cA)
        cell_A.set_color(ORANGE)
        highlight(cell_A, f"tt.get_cell(row={r}, col={cA})",
                  direction=LEFT, color=ORANGE)

        cell_x = tt.get_cell(row=r, col=cX)
        cell_x.set_color(PINK)
        lbl = highlight(cell_x, f"tt.get_cell(row={r}, col={cX})",
                        direction=RIGHT, color=PINK)
        lbl.shift(0.3 * RIGHT)

        r = 5
        cell_x = tt.get_cell(row=r, col="y")
        cell_x.set_color(MAROON_C)
        lbl = highlight(cell_x, f"tt.get_cell(row={r}, col='y')",
                        direction=RIGHT, color=MAROON_C)
        # lbl.shift(0.3 * RIGHT)

        # get_var_digits is just an alias for get_cell
        r = 4
        cell_A2 = tt.get_var_digits(row=r, col=cA)
        cell_A2.set_color(GREEN)
        highlight(cell_A2, f"tt.get_var_digits(row={r}, col={cA})", direction=LEFT, color=GREEN)

        # cell_x = tt.get_cell(row=r, col=cX)
        # cell_x.set_color(BLUE)
        # lbl = highlight(cell_x, f"tt.get_cell(row={r}, col={cX})", direction=RIGHT, color=BLUE)
        # lbl.shift(0.3 * RIGHT)
