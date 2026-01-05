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


def _pt_key(p, nd=5):
    return tuple(np.round(p[:2], nd))  # 2D key


def polygon_signed_area(pts2):
    """Signed area; >0 means CCW."""
    x = pts2[:, 0]
    y = pts2[:, 1]
    return 0.5 * np.sum(x[:-1] * y[1:] - x[1:] * y[:-1])

def offset_rectilinear_polygon(pts, d):
    """
    Offset a CLOSED rectilinear polygon outward by distance d.
    pts: (N,3) array, first point == last point.
    Returns (N,3) array closed.
    """
    pts = np.array(pts, dtype=float)
    if np.linalg.norm(pts[0] - pts[-1]) > 1e-6:
        pts = np.vstack([pts, pts[0]])

    p2 = pts[:, :2]
    ccw = polygon_signed_area(p2) > 0

    # For CCW polygons, outward normal is rotate(dir) by -90°.
    # For CW polygons, outward normal is rotate(dir) by +90°.
    def outward_normal(dir2):
        dx, dy = dir2
        if ccw:
            return np.array([dy, -dx])   # -90
        else:
            return np.array([-dy, dx])   # +90

    # Build offset lines for each edge, then intersect consecutive lines.
    out_pts = []
    n = len(pts) - 1  # last is duplicate
    for i in range(n):
        p0 = p2[i]
        p1 = p2[i + 1]
        dir2 = p1 - p0
        # normalize to unit axis direction
        if abs(dir2[0]) > abs(dir2[1]):
            dir2 = np.array([np.sign(dir2[0]), 0.0])
        else:
            dir2 = np.array([0.0, np.sign(dir2[1])])

        nrm = outward_normal(dir2)

        # line i: through p0+p_nrm*d, direction dir2
        # represent as (point, dir)
        out_pts.append((p0 + nrm * d, dir2))

    # Intersect consecutive offset lines
    new_p2 = []
    for i in range(n):
        (a0, adir) = out_pts[i - 1]      # previous edge line
        (b0, bdir) = out_pts[i]          # current edge line

        # Lines are axis-aligned; intersection is easy.
        # If adir is horizontal => y fixed; if vertical => x fixed.
        if abs(adir[0]) > 0:  # a horizontal => y = a0.y
            y = a0[1]
            x = b0[0] if abs(bdir[1]) > 0 else b0[0]  # b vertical => x = b0.x (also fine if horizontal)
            if abs(bdir[1]) > 0:
                x = b0[0]
            else:
                # both horizontal: keep vertex x from b0
                x = b0[0]
        else:  # a vertical => x = a0.x
            x = a0[0]
            if abs(bdir[0]) > 0:
                y = b0[1]
            else:
                # both vertical: keep vertex y from b0
                y = b0[1]

        new_p2.append([x, y])

    new_p2.append(new_p2[0])  # close
    new_pts = np.column_stack([np.array(new_p2), np.zeros(len(new_p2))])
    return new_pts


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
        self.value_fontsize = value_fontsize
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
                txt = Text(str(val), font_size=self.value_fontsize)
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

    def write(self, items = "all", return_mobjects=False, run_time=1.0):
        """
        Create animations to reveal parts of the Karnaugh map.

        This method fades in selected structural components (grid and labels) and
        writes the cell values. By default it returns a single `LaggedStart`
        animation; optionally it can return the raw animation list and the
        mobjects that were targeted.

        Args:
            items (str): Which components to reveal. Supported values:
                - "all": grid + row/col labels + variable labels (default)
                - "table": grid only
                - "vars": variable labels only
                - "labels": row/col Gray-code labels only
            return_mobjects (bool): If True, return `(anims, mobs)` instead of a
                `LaggedStart`, where `anims` is the list of animations and `mobs`
                is the list of structural mobjects that were faded in.
            run_time (float): Total runtime for the returned `LaggedStart`.

        Returns:
            Animation | tuple[list[Animation], list[Mobject]]:
                If `return_mobjects` is False, returns a `LaggedStart` animation
                that reveals the requested components. If True, returns `(anims, mobs)`.
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

        if return_mobjects:
            return anims, mobs
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

        elif var in self.row_vars:
            k = self.row_vars.index(var)  # which digit inside the row Gray strings
            hits = []
            for r, bits in enumerate(self.row_gray):
                if bits[k] == bit:
                    hits.append(self.row_gray_digits[r][k])
            return VGroup(*hits)
        elif len(var) == 2 :  # if asking for a combination, go here
            # this is going to be dirty, but whatever, the gray code is 0 1 3 2 so
            gray_map = {0: 0, 1: 1, 2: 3, 3: 2}
            num = int(value)
            print(num, var, var[0], self.row_gray_digits, self.col_gray_digits)
            if var[0] in self.row_vars:
                return VGroup(self.row_gray_digits[gray_map[num]])
            elif var[0] in self.col_vars:
                return VGroup(self.col_gray_digits[gray_map[num]])
            else:  # this part is put together pretty dirty
                raise ValueError("Something is broke in here, this parts needs work still")

        else:  # don't fail silently
            raise KeyError(f"var: {var} not found, valid entries are column vars: "
                           f"{self.col_vars} and row vars: {self.row_vars}")

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

    def outline_cells(self, minterms, color=RED, stroke_width=4, buff=0.0) -> VMobject:
        """
        Return an outline around the union of the selected cells.
        Unlike SurroundingRectangle, this can make non-rectangular outlines (e.g., L-shapes).

        Args:
            minterms: iterable of minterm indices to include.
            color: stroke color for outline.
            stroke_width: outline thickness.
            buff: optional outward offset (keep 0.0 to start).

        Returns:
            VMobject polyline outline.
        """
        # 1) Gather cell rectangles
        rects = []
        for m in minterms:
            sq, _ = self.get_cell_from_minterm(m)
            if sq is not None:
                rects.append(sq)

        if not rects:
            return VMobject()

        # 2) Build a multiset of edges; internal shared edges cancel out
        # Each rect contributes 4 directed edges between its corners.
        edge_counts = {}  # (a,b) undirected key -> count, plus store a->b direction later
        directed_edges = []

        for r in rects:
            # corners in screen coordinates (Manim returns 3D points)
            c = r.get_corner
            p_ul = c(UL);
            p_ur = c(UR);
            p_dr = c(DR);
            p_dl = c(DL)

            corners = [p_ul, p_ur, p_dr, p_dl]
            segs = [(corners[i], corners[(i + 1) % 4]) for i in range(4)]

            for a, b in segs:
                ak, bk = _pt_key(a), _pt_key(b)
                und = tuple(sorted([ak, bk]))
                edge_counts[und] = edge_counts.get(und, 0) + 1
                directed_edges.append((ak, bk))

        # Keep only boundary edges (appear once)
        boundary = [(a, b) for (a, b) in directed_edges
                    if edge_counts[tuple(sorted([a, b]))] == 1]

        if not boundary:
            return VMobject()

        # 3) Stitch boundary edges into a continuous loop
        # Build adjacency from start->end
        next_map = {}
        for a, b in boundary:
            next_map.setdefault(a, []).append(b)

        # Pick a starting point (leftmost, then highest)
        start = sorted(next_map.keys(), key=lambda k: (k[0], -k[1]))[0]

        path = [start]
        cur = start
        prev = None

        # Follow edges until we return to start
        for _ in range(10000):
            options = next_map.get(cur, [])
            if not options:
                break
            # Choose next; if two options, avoid going back to prev
            if prev is not None and len(options) > 1:
                nxt = options[0] if options[0] != prev else options[1]
            else:
                nxt = options[0]
            path.append(nxt)
            prev, cur = cur, nxt
            if cur == start:
                break

        # Convert keys back to 3D points
        pts = [np.array([x, y, 0.0]) for (x, y) in path]

        outline = VMobject()
        outline.set_points_as_corners(pts)

        if buff != 0.0:
            pts = offset_rectilinear_polygon(pts, buff)

        outline = VMobject()
        outline.set_points_as_corners(pts)
        outline.set_stroke(color=color, width=stroke_width)
        outline.set_fill(opacity=0)
        return outline

    def term_to_minterms(self, term: str) -> list[int]:
        """
        Convert a product term like "AB", "A'B'", "AB'C" into the list of minterms it covers.
        Unspecified variables are treated as don't-cares.

        Doctests
        --------
        >>> class _Dummy:
        ...     num_vars = 3
        ...     var_names = ["A", "B", "C"]
        ...     term_to_minterms = KarnaughMap.term_to_minterms
        ...
        >>> d = _Dummy()
        >>> d.term_to_minterms("AB")
        [6, 7]
        >>> d.term_to_minterms("A'B'")
        [0, 1]
        >>> d.term_to_minterms("B")
        [2, 3, 6, 7]
        >>> d.term_to_minterms("B'")
        [0, 1, 4, 5]
        >>> d.term_to_minterms("C")
        [1, 3, 5, 7]
        >>> d.term_to_minterms("AB'C")
        [5]

        Invalid terms
        >>> d.term_to_minterms("Z")
        Traceback (most recent call last):
        ...
        ValueError: Unknown variable 'Z' in term 'Z'. Valid: ['A', 'B', 'C']
        """
        t = term.replace(" ", "")
        if not t:
            raise ValueError("term cannot be empty")

        constraints: dict[str, int] = {}
        i = 0
        while i < len(t):
            ch = t[i]
            if not ch.isalpha():
                raise ValueError(f"Invalid term {term!r}: unexpected character {ch!r}")

            var = ch
            if var not in self.var_names:
                raise ValueError(f"Unknown variable {var!r} in term {term!r}. Valid: {self.var_names}")

            val = 1
            if i + 1 < len(t) and t[i + 1] == "'":
                val = 0
                i += 1  # consume apostrophe

            if var in constraints and constraints[var] != val:
                raise ValueError(f"Conflicting literals for {var!r} in term {term!r}")
            constraints[var] = val
            i += 1

        mins: list[int] = []
        for m in range(2 ** self.num_vars):
            bits = f"{m:0{self.num_vars}b}"
            ok = True
            for var, desired in constraints.items():
                idx = self.var_names.index(var)
                if int(bits[idx]) != desired:
                    ok = False
                    break
            if ok:
                mins.append(m)
        return mins

    def get_label(self, *args, **kwargs):
        """
        Guard method: KarnaughMap does not use `get_label()`.

        Use:
          - get_var_label(var)   -> the variable name Text (e.g. "A")
          - get_var_digits(var, value) -> the Gray-code digit Text objects for var=value
        """
        valid_vars = ", ".join(self.var_names)
        raise AttributeError(
            "KarnaughMap has no `get_label()` method.\n"
            "Use `get_var_label(var)` for the variable name label (e.g. 'A').\n"
            "Use `get_var_digits(var, value)` for Gray-code digits where var=value.\n"
            f"Valid variables: {valid_vars}"
        )


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

        kmap = KarnaughMap(num_vars, values=values, var_names=["A", "B", "C"])
        kmap.to_edge(LEFT)

        self.play(kmap.write("all", run_time=2.0))
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


class KMapCheatSheet(Scene):
    """ Make a cheat sheet for easy reference for the Manim KarnaughMap Class"""
    def construct(self):
        Text.set_default(font="Menlo")

        num_vars = 3
        ones = [1, 3, 5, 6, 7]
        values = {m: 1 for m in ones}
        for m in range(2**num_vars):
            values.setdefault(m, 0)

        kmap = KarnaughMap(num_vars, values=values, var_names=["A", "B", "C"])

        self.play(kmap.write("all", run_time=1.5))
        self.wait(0.3)

        # ------------------------------------------------------------
        # Helper for consistent callout boxes + labels
        # ------------------------------------------------------------
        def callout(mob: Mobject, text: str, direction=RIGHT, color=YELLOW, rt=0.5):
            # box = SurroundingRectangle(mob, buff=0.08, color=color, stroke_width=3)
            mob.set_color(color)
            tag = Text(text, font_size=22).set_color(color)
            tag.next_to(mob, direction, buff=0.25)
            self.play(FadeIn(tag), run_time=rt)
            self.wait(0.4)

        def callout_group(mob: Mobject, text: str, direction=RIGHT, color=YELLOW, rt=0.5):
            # For VGroups that might be empty
            if mob is None or len(mob) == 0:
                tag = Text(text + " -> (empty)", font_size=22).set_color(color)
                tag.to_corner(DR)
                self.play(FadeIn(tag), run_time=0.3)
                self.wait(0.6)
            callout(mob, text, direction=direction, color=color, rt=rt)

        # ============================================================
        # 1) get_cell_from_minterm(m) -> (square, text)
        # ============================================================
        m = 6
        sq, txt = kmap.get_cell_from_minterm(m)
        sq.set_stroke(color=RED, width=6)
        txt.set_color(BLUE)
        tag = Text(f"sq, txt =\nget_cell_from_minterm({m})",
                   font_size=22, t2c={"sq": RED, "txt": BLUE},)
        tag.next_to(sq if sq is not None else txt, RIGHT, buff=0.25)
        # tag.set_color(YELLOW)
        self.add(tag)
        # if sq is not None:
        #     callout(sq, f"kmap.get_cell_from_minterm({m}) -> square", direction=UP, color=RED)
        # if txt is not None:
        #     callout(txt, f"kmap.get_cell_from_minterm({m}) -> text", direction=DOWN, color=BLUE)
        # ============================================================
        # 2) get_var_label(var) -> Text
        # ============================================================
        A = kmap.get_var_label("A")
        self.play(A.animate.set_color(YELLOW), run_time=0.3)
        callout(A, 'kmap.get_var_label("A")', direction=UP, color=YELLOW)

        # ============================================================
        # 3) get_var_digits(var, value) -> VGroup of digits
        # ============================================================
        b0_digits = kmap.get_var_digits("B", 0)
        # Box the *group* (surrounding rectangle uses the group's bounds)
        callout_group(b0_digits, 'kmap.get_var_digits("B", 0)', direction=LEFT, color=GREEN)

        # ============================================================
        # 4) pulse_var_digits(var, value) -> (AnimationGroup, digits_to_restore)
        # ============================================================
        pulse_anim, restore_target = kmap.pulse_var_digits("B", 1, scale_factor=1.8, color=YELLOW, run_time=0.25)
        # Show which digits are pulsing with a callout first (optional)
        callout_group(restore_target, 'kmap.pulse_var_digits("B", 0) -> anim + restore state\nself.play(anim)', direction=DOWN, color=YELLOW,
                      rt=0.35)
        self.play(pulse_anim)
        # self.play(Restore(restore_target), run_time=0.2)

        # ============================================================
        # 5) get_var_minterms(var, value) -> list[int]
        # ============================================================
        mins = kmap.get_var_minterms("B", 0)
        mins_label = Text(f'kmap.get_var_minterms("B", 0) -> {mins}', font_size=22)
        mins_label.to_corner(DR)
        self.play(FadeIn(mins_label), run_time=0.3)
        self.wait(0.9)

        # ============================================================
        # 6) get_var_cell_texts(var, value) -> VGroup of cell Text mobjects
        # ============================================================
        b0_cells = kmap.get_var_cell_texts("B", 0)
        b0_cells.save_state()
        self.play(b0_cells.animate.set_color(PURPLE).scale(1.15), run_time=0.25)
        callout_group(b0_cells, 'kmap.get_var_cell_texts("B", 0)\nkmap.pulse_var_cells("B", 0)',
                      direction=RIGHT, color=PURPLE)
        # self.play(Restore(b0_cells), run_time=0.2)

        # ============================================================
        # 7) pulse_var_cells(var, value) -> AnimationGroup
        # ============================================================
        # b1_cells = kmap.get_var_cell_texts("B", 1)
        # b1_cells.save_state()
        # callout_group(b1_cells, 'kmap.pulse_var_cells("B", 1)', direction=RIGHT, color=RED, rt=0.35)
        # self.play(kmap.pulse_var_cells("B", 1, scale_factor=1.4, color=RED, run_time=0.25))
        # self.play(Restore(b1_cells), run_time=0.2)
        #
        # ============================================================
        # 8) highlight_group(minterms, ...) -> SurroundingRectangle (implicant box)
        # ============================================================
        imp = kmap.highlight_group([2, 3], color=PURE_BLUE)
        self.play(Create(imp), run_time=0.4)
        callout(imp, "kmap.highlight_group([2, 3])", direction=LEFT, color=PURE_BLUE)
        # self.play(FadeOut(imp), run_time=0.3)
        #
        # ============================================================
        # 9) outline_cells(minterms, ...) -> VMobject outline (non-rect possible)
        # ============================================================
        outline = kmap.outline_cells([1, 3, 7], color=PURE_GREEN, stroke_width=5, buff=-0.2)
        self.play(Create(outline), run_time=0.4)
        callout(outline, "kmap.outline_cells([1, 3, 7],\nbuff=-0.2)", direction=RIGHT, color=PURE_GREEN)
        # self.play(FadeOut(outline), run_time=0.3)
        #
        # # ============================================================
        # # OPTIONAL: write_cells + write_cell (comment out if you want)
        # # ============================================================
        # # self.play(kmap.write_cells(run_time=0.8))
        # # self.wait(0.2)
        # # self.play(kmap.write_cell(0, 0, value="X", run_time=0.4))
        # # self.wait(0.2)
        #
        # # Final frame: tint headers so screenshot looks nicer (optional)
        # for v, c in [("A", YELLOW), ("B", GREEN), ("C", ORANGE)]:
        #     kmap.get_var_label(v).set_color(c)
        #
        # self.wait(2)

if __name__ == '__main__':
    kmap = KarnaughMap(num_vars=3, var_names=["A", "B", "C"],
                       stroke_width=4)
    print(kmap.col_gray_digits)
    print(kmap.row_gray_digits)
    print(kmap.col_vars)
    print(kmap.row_vars)
    print(kmap.get_var_digits("BC", "01"))
