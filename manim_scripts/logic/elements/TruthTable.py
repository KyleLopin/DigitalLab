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
        inputs,
        outputs,
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

        print("test lens: ", len(horizontal_lines), len(vertical_lines))
        print(f"header_line_index: {header_line_index}; sep_line_index: {sep_line_index}")
        if len(horizontal_lines) > header_line_index:
            self.header_line = horizontal_lines[header_line_index]
            self.header_line.set_stroke(width=5)
            self.header_line.set_opacity(0)

        if len(vertical_lines) > sep_line_index:
            self.sep_line = vertical_lines[sep_line_index]
            self.sep_line.set_stroke(width=5)
            self.sep_line.set_opacity(0)

    # ========== animation helper methods ==========

    def draw_lines(self, run_time=0.5):
        """Animations to draw the two lines."""
        anims = []
        print(self.header_line, self.sep_line)
        if self.header_line is not None:
            anims.append(self.header_line.animate.set_opacity(1))
        if self.sep_line is not None:
            anims.append(self.sep_line.animate.set_opacity(1))
        return AnimationGroup(*anims, run_time=run_time)

    def write_inputs(self, run_time=0.5):
        """Animations to write input variable labels (A, B, C, ...)."""
        anims = [lbl.animate.set_opacity(1) for lbl in self.input_labels]
        print("write: ", anims)
        return AnimationGroup(*anims, lag_ratio=0.1, run_time=run_time)

    def write_outputs(self, run_time=0.5):
        """Animations to write output variable labels (F, x, ...)."""
        anims = [lbl.animate.set_opacity(1) for lbl in self.output_labels]
        return AnimationGroup(*anims, lag_ratio=0.1, run_time=run_time)

    def write_body(self, run_time=1.0):
        """Animations to reveal the rows of the truth table."""
        anims = [r.animate.set_opacity(1) for r in self.body_rows]
        print(self.body_rows)
        # LaggedStart = row-by-row reveal
        return LaggedStart(*anims, lag_ratio=0.15, run_time=run_time)

    def write_all(self, run_time=1.0):
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
        )
        tt.to_edge(UP)

        # 1) draw the two lines
        # self.play(tt.draw_lines(run_time=1))
        # self.wait(1)
        #
        # # 2) write input labels (A, B, C)
        # self.play(tt.write_inputs(run_time=2))
        # self.wait(1)
        #
        # # 3) write output labels (x)
        # self.play(tt.write_outputs(run_time=2))
        # self.wait(1)
        # #
        # # 4) fill in the table rows
        # self.play(tt.write_body(run_time=2))
        # self.wait(1)

        self.play(tt.write_all())
        self.wait()
