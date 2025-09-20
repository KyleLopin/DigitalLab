# Copyright (c) 2025 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""

"""

__author__ = "Kyle Vitautas Lopin"

from manim import *

class KMap4Variables(VGroup):
    def __init__(self, variable_names=["A", "B", "C", "D"], cell_size=0.8, **kwargs):
        super().__init__(**kwargs)
        # Sanity check
        if len(variable_names) != 4:
            raise ValueError("variable_names must have 4 items (e.g., ['A','B','C','D'])")
        self.variable_names = variable_names
        self.cell_size = cell_size

        # Gray code order for 2 bits: 00, 01, 11, 10
        gray_labels = ["00", "01", "11", "10"]

        # Draw grid lines (4x4)
        grid = VGroup()
        for i in range(5):  # 4 cells => 5 lines
            # Horizontal lines
            y = (2 - i) * cell_size
            grid.add(Line([-2*cell_size, y, 0], [2*cell_size, y, 0], color=GRAY))
            # Vertical lines
            x = (-2 + i) * cell_size
            grid.add(Line([x, 2*cell_size, 0], [x, -2*cell_size, 0], color=GRAY))

        self.add(grid)

        # Draw Gray code labels
        label_buff = 0.25
        # Top labels (for columns, e.g. variables C and D)
        for i, label in enumerate(gray_labels):
            x = (-1.5 + i) * cell_size
            y = 2 * cell_size + label_buff
            code = MathTex(label, color=WHITE).scale(0.7).move_to([x, y, 0])
            self.add(code)
        # Side labels (for rows, e.g. variables A and B)
        for i, label in enumerate(gray_labels):
            x = -2 * cell_size - label_buff
            y = (1.5 - i) * cell_size
            code = MathTex(label, color=WHITE).scale(0.7).move_to([x, y, 0])
            self.add(code)

        # Coordinates of upper-left corner of the grid
        upper_left = np.array([-2 * cell_size, 2 * cell_size, 0])

        # Stack AB above CD, or put side by side
        column_label = MathTex(
            f"{variable_names[0]}{variable_names[1]}", color=WHITE
        ).scale(0.8)
        row_label = MathTex(
            f"{variable_names[2]}{variable_names[3]}", color=WHITE
        ).scale(0.8)

        # Arrange "AB" above "CD", with a little vertical spacing
        row_label.next_to(upper_left, UP, buff=0.45)
        column_label.next_to(upper_left, LEFT, buff=0.35)

        self.add(column_label, row_label)

        # Optionally, add a faint rectangle border for the whole map
        rect = Rectangle(
            width=4 * cell_size, height=4 * cell_size,
            color=GRAY, stroke_opacity=0.5
        )
        self.add(rect)

        # --- Add diagonal line from upper left (just inside) going down and right ---

        # Diagonal coordinates (just inside the upper left grid cell)
        # Offset from the actual grid corner for the diagonal marker (longer, more visible)
        diag_offset = cell_size * 0.7
        # Start: Above and to the left of upper left grid corner
        diag_start = upper_left + np.array([-diag_offset, diag_offset, 0])
        # End: Below and to the right of upper left grid corner
        diag_line = Line(diag_start, upper_left, color=WHITE, stroke_width=2)
        self.add(diag_line)

    # Optionally, add a method to fill a cell
    def fill_cell(self, row, col, color=YELLOW, opacity=0.6):
        """
        Fills a cell at (row, col) with color (row, col = 0..3).
        (0,0) is top-left.
        """
        x = (-0.9 + col) * self.cell_size
        y = (1.05 - row) * self.cell_size
        square = Square(
            side_length=self.cell_size,
            fill_color=color, fill_opacity=opacity, stroke_width=0
        ).move_to([x, y, 0])
        self.add(square)
        return square

    def draw_group_box(self, row_start, row_end, col_start, col_end, color=YELLOW, linewidth=4, corner_radius=0.25):
        """
        Draws a rounded rectangle box around the cells defined by (row_start, row_end, col_start, col_end).
        All indices inclusive, (0,0) is top-left.
        """
        # Compute center of group
        cx = ((col_start + col_end) / 2 - 1.5) * self.cell_size
        cy = ((1.5 - (row_start + row_end) / 2)) * self.cell_size

        # Compute box width and height
        width = (col_end - col_start + 1) * self.cell_size
        height = (row_end - row_start + 1) * self.cell_size

        box = RoundedRectangle(
            width=width + 0.15,    # slight padding
            height=height + 0.15,  # slight padding
            corner_radius=corner_radius,
            color=color,
            stroke_width=linewidth,
            fill_opacity=0        # no fill, just outline
        ).move_to([cx, cy, 0])

        self.add(box)
        return box


class TestKMapScene(Scene):
    def construct(self):
        kmap = KMap4Variables(["A", "B", "C", "D"])
        kmap.move_to(ORIGIN)
        self.add(kmap)
        # Optionally fill a cell (example: row 2, col 3)
        filled_cell = kmap.fill_cell(2, 3, color=YELLOW)
        self.play(FadeIn(filled_cell))
        group_box = kmap.draw_group_box(0, 1, 1, 2, color=GREEN, linewidth=6)
        self.play(Create(group_box))
