# Copyright (c) 2025 Kyle Lopin (Naresuan University) <kylelopin@gmail.com>

"""
Testing if I should make native Manim gates or import schemdraw objects.
"""

__author__ = "Kyle Vitautas Lopin"


from manim import *

# ---- Schemdraw constants ----
gateh = 1.0
gatel = 0.65
notbubble = 0.12


class LogicGateBase(VGroup):
    def __init__(
        self,
        leads=None,
        n_inputs=None,
        width=2.0,
        height=1.4,
        height_per_extra=0.45,
        lead_len=0.7,
        label_buff=0.15,
        gate_color=WHITE,
        stroke_width=3,
        add_output_stub=True,
        out_len=0.7,
        output_label=None,          # e.g. "F"
        output_label_dir=RIGHT,
        output_label_buff=0.1,
        output_label_scale=1.4,
        bubble=False,               # NAND/NOR
        bubble_radius=0.18,
        bubble_gap=0.02,
        label_scale = 1.4,
        label_kwargs=None,
        **kwargs
    ):
        super().__init__(**kwargs)
        label_kwargs = label_kwargs or {}

        if n_inputs is None:
            n_inputs = len(leads) if leads is not None else 2
        if leads is None:
            leads = [None] * n_inputs
        if len(leads) != n_inputs:
            raise ValueError("len(leads) must match n_inputs")

        self.n_inputs = n_inputs
        self.w = width
        self.h = height + max(0, n_inputs - 2) * height_per_extra
        self.stroke_width = stroke_width

        # Outline is gate-specific
        self.outline = (self._build_outline(self.w, self.h))
        self.outline.set_stroke(width=stroke_width, color=gate_color)
        self.add(self.outline)

        # Leads + labels
        self.lead_lines = VGroup()
        self.lead_labels = VGroup()
        for lead, p_in in zip(leads, self.input_anchors(), strict=False):
            p0 = p_in
            p1 = p_in + LEFT * lead_len
            line = Line(p1, p0).set_stroke(width=stroke_width)
            self.lead_lines.add(line)

            if lead is not None:
                lab = MathTex(str(lead), **label_kwargs).scale(label_scale)
                lab.next_to(p1, LEFT, buff=label_buff)
                self.lead_labels.add(lab)

        self.add(self.lead_lines, self.lead_labels)

        # Output (optional bubble + stub + label)
        self.bubble = None
        self.out_stub = None
        self.out_label = None

        out_point = self.output_anchor()

        if bubble:
            # bubble sits just outside the outline at the output
            self.bubble = Circle(radius=bubble_radius).set_stroke(width=stroke_width)
            self.bubble.move_to(out_point + RIGHT * (bubble_radius + bubble_gap))
            self.add(self.bubble)
            self.bubble.set_color(WHITE)  # IDK why this is needed.
            out_point = self.bubble.get_right()

        if add_output_stub:
            self.out_stub = Line(out_point, out_point + RIGHT * out_len).set_stroke(width=stroke_width)
            # self.out_stub.set_color(PURPLE)
            self.add(self.out_stub)
            out_point = self.out_stub.get_end()

        if output_label is not None:
            self.out_label = Tex(str(output_label), **label_kwargs).scale(output_label_scale)
            self.out_label.next_to(out_point, output_label_dir, buff=output_label_buff)
            self.add(self.out_label)

    # --- anchors ---
    def input_anchors(self, pin_spread=1.8):
        x = self.get_left()[0]
        ys = np.linspace(self.get_top()[1], self.get_bottom()[1], self.n_inputs + 2)[1:-1]
        yc = self.get_center()[1]
        ys = yc + (ys - yc) * pin_spread  # <-- spread them out
        return [np.array([x, y, 0]) for y in ys]

    def output_anchor(self):
        return self.get_right()

    def get_in(self, i): return self.input_anchors()[i]

    def get_out(self):
        # prefer stub end if present, else bubble right, else outline right
        if self.out_stub is not None:
            return self.out_stub.get_end()
        if self.bubble is not None:
            return self.bubble.get_right()
        return self.output_anchor()

    # --- gate-specific ---
    def _build_outline(self, w, h) -> VMobject:
        raise NotImplementedError


class AndGate(LogicGateBase):
    def _build_outline(self, w, h):
        r = h / 2
        left = Line((-w/2, -h/2, 0), (-w/2,  h/2, 0))
        top = Line((-w/2,  h/2, 0), (0,     h/2, 0))
        bottom = Line((-w/2, -h/2, 0), (0,   -h/2, 0))
        arc = Arc(radius=r, start_angle=-PI/2, angle=PI)
        return VGroup(left, top, bottom, arc)


class NandGate(AndGate):
    def __init__(self, *args, **kwargs):
        kwargs["bubble"] = True
        super().__init__(*args, **kwargs)


class NotGate(LogicGateBase):
    def __init__(self, leads=None, **kwargs):
        # NOT gate has exactly 1 input
        kwargs.setdefault("n_inputs", 1)

        # Inverter symbol includes a bubble by default
        kwargs.setdefault("bubble", True)

        # NOT gates are usually a bit smaller/tighter
        kwargs.setdefault("width", 1.4)
        kwargs.setdefault("height", 1.5)

        super().__init__(leads=leads, **kwargs)

    def _build_outline(self, w, h) -> VMobject:
        """
        Triangle pointing right.
        Base class bubble is placed at output_anchor() (rightmost point of outline).
        """
        left_x = -w / 2
        tip_x  =  w / 2

        tri = Polygon(
            np.array([left_x,  h/2, 0.0]),   # top-left
            np.array([left_x, -h/2, 0.0]),   # bottom-left
            np.array([tip_x,   0.0, 0.0]),   # tip
        )
        tri.set_fill(opacity=0)
        return tri

# Helper functions for making OR gate
def _polyline(points, stroke_width=3):
    """Polyline VMobject through given (x,y,0) points."""
    m = VMobject()
    m.set_points_as_corners(points)
    m.set_stroke(width=stroke_width)
    return m

def _closed_path(points, stroke_width=3):
    """Closed polyline (last point connects back to first)."""
    pts = list(points)
    if np.linalg.norm(np.array(pts[0]) - np.array(pts[-1])) > 1e-6:
        pts.append(pts[0])
    return _polyline(pts, stroke_width=stroke_width)


class OrGate(VGroup):
    """
    Schemdraw-style OR / XOR / NOR gate.

    Args:
        inputs: number of inputs
        nor: add output bubble
        xor: add extra back curve
        inputnots: list like [1,3] meaning invert those inputs (1-based)
        leadin/leadout: lengths like schemdraw
    """
    def __init__(
        self,
        inputs=2,
        nor=False,
        xor=False,
        inputnots=None,
        leadin=0.35,
        leadout=0.35,
        stroke_width=3,
        label_cls=MathTex,  # NEW
        label_scale=0.7,  # NEW
        label_buff=0.12,  # NEW
        label_kwargs={},  # NEW
        output_label_dir=UP,  # NEW
        output_label_buff=0.10,  # NEW
        **kwargs
    ):
        leads = kwargs.pop("leads", None)
        output_label = kwargs.pop("output_label", None)
        super().__init__(**kwargs)
        self.input_labels = VGroup()
        self.input_leads = VGroup()
        inputnots = set(inputnots or [])

        # If leads provided, override inputs
        if leads is not None:
            inputs = len(leads)
        else:
            leads = [None] * inputs

        # Pins that transform with the gate
        self._pins = {}

        def _pin(name, pos):
            p = VectorizedPoint(pos)
            self._pins[name] = p
            self.add(p)
            return p

        # ---- This block matches schemdraw’s math closely ----
        orflat = 0.5
        xorgap = 0.15

        xs = np.linspace(0, gatel + 0.05, 30)
        ys = xs**2
        ys = ys - np.max(ys)
        ys = np.concatenate([[np.min(ys)], ys])              # flat+parabola combine
        xs = np.concatenate([[0.0], xs + orflat])

        # Back/input side
        y2 = np.linspace(np.min(ys), -np.min(ys), 60)
        x2 = -(y2**2)
        back = np.min(x2)
        x2 = x2 - back

        # Offset for input leads
        xs = xs + leadin
        x2 = x2 + leadin

        tip = float(np.max(xs))
        orheight = abs(float(np.min(ys)))

        negy = -ys
        # Main OR outline path (closed)
        path_xy = list(zip(xs, ys)) + list(zip(xs[::-1], negy[::-1])) + list(zip(x2[::-1], y2[::-1]))
        outline_pts = [np.array([x, y, 0.0]) for x, y in path_xy]
        outline = _closed_path(outline_pts, stroke_width=stroke_width)
        self.add(outline)

        # XOR extra curve (a second back curve offset left)
        if xor:
            xxor = x2 - xorgap
            xor_pts = [np.array([x, y, 0.0]) for x, y in zip(xxor, y2)]
            self.add(_polyline(xor_pts, stroke_width=stroke_width))
            leadin_eff = leadin - xorgap
        else:
            leadin_eff = leadin

        # Output bubble for NOR
        if nor:
            bubble = Circle(radius=notbubble).set_stroke(width=stroke_width).set_color(WHITE)
            # place like schemdraw: center at (tip + notbubble, 0)
            bubble.move_to(np.array([tip + notbubble, 0.0, 0.0]))
            self.add(bubble)
            out_start = np.array([tip + notbubble * 2, 0.0, 0.0])
        else:
            out_start = np.array([tip, 0.0, 0.0])

        # ---- Input spacing dy (fit pins inside gate height) ----
        # Base dy preference
        if inputs == 2:
            dy_base = gateh * 0.5
        elif inputs == 3:
            dy_base = gateh * 0.33
        else:
            dy_base = gateh * 0.4
            backlen = dy_base * (inputs - 1)

        # Compute max allowed dy so top/bottom pins stay within the OR outline height.
        # Pin y positions are: y = (i + 1 - (inputs/2 + 0.5)) * dy
        # max |y| = ((inputs - 1)/2) * dy
        max_pin_y_allowed = orheight * 0.92  # keep a little margin inside the outline
        dy_max = max_pin_y_allowed / ((inputs - 1) / 2) if inputs > 1 else dy_base

        dy = min(dy_base, dy_max)

        # Input leads + optional input bubbles
        for i in range(inputs):
            y = (i + 1 - (inputs / 2 + 0.5)) * dy

            xback = leadin_eff - y**2 - back
            if inputs > 3 and ((y > orheight) or (y < -orheight)):
                xback = leadin_eff

            in_num = inputs - i  # schemdraw names them inN..in1 top->bottom-ish

            if in_num in inputnots:
                ib = Circle(radius=notbubble).set_stroke(width=stroke_width)
                ib.move_to(np.array([xback - notbubble, y, 0.0]))
                self.add(ib)
                lead = Line(np.array([0.0, y, 0.0]),
                            np.array([xback - notbubble * 2, y, 0.0])).set_stroke(width=stroke_width)
                # endpt = np.array([xback - notbubble * 2, y, 0.0])
            else:
                lead = Line(np.array([0.0, y, 0.0]),
                              np.array([xback, y, 0.0])).set_stroke(width=stroke_width)
                # endpt = np.array([xback, y, 0.0])
            self.input_leads.add(lead)
            self.add(lead)

            p_left = np.array([0.0, y, 0.0])  # back of lead (leftmost)
            # pin at the gate input point (x=0)
            _pin(f"in{in_num}", np.array([0.0, y, 0.0]))

            # label at the *left* end of the lead
            lead_text = leads[i]  # NOTE: leads list is top->bottom in your i loop
            if lead_text is not None:
                lab = label_cls(str(lead_text), **label_kwargs).scale(label_scale)
                lab.next_to(p_left, LEFT, buff=label_buff)
                self.add(lab)
                self.input_labels.add(lab)

        # Extended back for large number of inputs
        # if inputs > 3:
        #     # self.add(Line(np.array([leadin_eff, backlen/2 + dy/2, 0]),
        #     #               np.array([leadin_eff, orheight, 0])).set_stroke(width=stroke_width))
        #     # self.add(Line(np.array([leadin_eff, -backlen/2 - dy/2, 0]),
        #     #               np.array([leadin_eff, -orheight, 0])).set_stroke(width=stroke_width))
        #     extra_h_per_input = 0.45  # tweak
        #     target_h = self.height + (inputs - 3) * extra_h_per_input
        #     self.stretch_to_fit_height(target_h)
            # self.stretch(1.5, dim=0)
        _pin(f"in{in_num}", np.array([0.0, y, 0.0]))
        # Output lead
        out_end = out_start + RIGHT * leadout
        self.add(Line(out_start, out_end).set_stroke(width=stroke_width))
        _pin("out", out_end)

        # Output label at end of stub
        if output_label is not None:
            out_lab = label_cls(str(output_label), **label_kwargs).scale(label_scale)
            out_lab.next_to(out_end, output_label_dir, buff=output_label_buff)
            self.add(out_lab)

        self.inputs = inputs  # store for helpers

        # Handy anchor points (like schemdraw)
        self.anchors = {}
        self.anchors["out"] = out_end
        for i in range(inputs):
            y = (i + 1 - (inputs / 2 + 0.5)) * dy
            self.anchors[f"in{inputs - i}"] = np.array([0.0, y, 0.0])

    def get_in(self, i: int):
        """
        0-based, top-to-bottom.
        Your pins are named inN..in1 (top is inN).
        """
        if type(i) == str:
            raise ValueError("To get the input of the Or gate, pass in i as a "
                             "integer of the number it is of the input, not a string")
        name = f"in{self.inputs - i}"
        return self._pins[name].get_center()

    def input_anchors(self):
        return [self.get_in(i) for i in range(self.inputs)]

    def get_out(self):
        return self._pins["out"].get_center()

    def output_anchor(self):
        return self.get_out()

    def to_y(self, y: float):
        self.shift((y - self.get_center()[1]) * UP)
        return self


class NorGateSD(OrGate):
    def __init__(self, *args, **kwargs):
        kwargs["nor"] = True
        super().__init__(*args, **kwargs)


class AndGate_Pre(VGroup):
    def __init__(self,
                 leads=None,  # e.g. ["A", "B"] or ["A", "B", "C"]
                 n_inputs=None,  # if None, inferred from leads; default 2
                 width=2.0, height=1.4,
                 height_per_extra=0.45,  # extra height per input above 2
                 lead_len=0.7, label_buff=0.15,
                 stroke_width=4, label_kwargs=None,
                 **kwargs):
        super().__init__(**kwargs)
        label_kwargs = label_kwargs or {}

        # Infer number of inputs
        if n_inputs is None:
            n_inputs = len(leads) if leads is not None else 2
        if leads is None:
            leads = [None] * n_inputs
        if len(leads) != n_inputs:
            raise ValueError("len(leads) must match n_inputs")

        h = height + max(0, n_inputs - 2) * height_per_extra
        w = width
        r = h / 2

        # Outline (schemdraw-style AND: flat left + semicircle right)
        left = Line((-w / 2, -h / 2, 0), (-w / 2, h / 2, 0))
        top = Line((-w / 2, h / 2, 0), (0, h / 2, 0))
        bottom = Line((-w / 2, -h / 2, 0), (0, -h / 2, 0))
        arc = Arc(radius=r, start_angle=-PI / 2, angle=PI).shift((0, 0, 0))

        self.outline = VGroup(left, top, bottom, arc).set_stroke(width=stroke_width)

        self.add(self.outline)

        # Anchors
        self._n_inputs = n_inputs
        self._w, self._h = w, h

        # Leads + labels
        self.lead_lines = VGroup()
        self.lead_labels = VGroup()

        for i, anchor in enumerate(self.input_anchors()):
            p0 = anchor
            p1 = anchor + LEFT * lead_len
            line = Line(p1, p0).set_stroke(width=stroke_width)
            self.lead_lines.add(line)

            if leads[i] is not None:
                lab = Tex(str(leads[i]), **label_kwargs).scale(0.7)
                lab.next_to(p1, LEFT, buff=label_buff)
                self.lead_labels.add(lab)

        self.add(self.lead_lines, self.lead_labels)

    def input_anchors(self, n=2):
        """Evenly spaced input anchor points on the left face."""
        x = self.get_left()[0]
        top_y = self.get_top()[1]
        bot_y = self.get_bottom()[1]
        ys = np.linspace(top_y, bot_y, self._n_inputs + 2)[1:-1]  # avoid edges
        return [np.array([x, y, 0]) for y in ys]

    def get_in(self, i: int):
        """Anchor point for input i (0-based)."""
        return self.input_anchors()[i]

    def get_out(self):
        return self.output_anchor()

    def output_anchor(self):
        return self.get_right()


class Demo(Scene):
    def construct(self):
        builder = CircuitBuilder(var_order=("A", "B", "C"))

        sop = [
            [("A", 1), ("B", 0), ("C", 1)],   # A B' C
            [("A", 0), ("B", 1), ("C", 1)],   # A' B C
            # [("A", 1), ("B", 1)],  # A B
            [("C", 0)],  # C'
            # [("A", 1), ("C", 0)],  # A C'
            # [("A", 1), ("C", 0)]
        ]
        sop_circ = builder.build_sop(sop, output_label="F").to_corner(UL, buff=0.6).scale(0.9)

        # pos = [
        #     [("A", 1), ("B", 0), ("C", 1)],   # (A + B' + C)
        #     [("A", 0), ("B", 1), ("C", 0)],   # (A' + B + C')
        # ]
        # pos_circ = builder.build_pos(pos, output_label="F").to_corner(UR, buff=0.6).scale(0.9)

        self.play(Create(sop_circ), run_time=2.0)
        # self.play(Create(pos_circ), run_time=2.0)
        self.wait(1)

# helper functions to make compound circuits:
def manhattan_wire(p1, p2, x_mid=None, y_mid=None, stroke_width=3):
    """
    Returns a VGroup of 2 or 3 Line segments connecting p1->p2 with right angles.
    Provide x_mid for H-V-H routing, or y_mid for V-H-V routing.
    """
    p1 = np.array(p1, dtype=float)
    p2 = np.array(p2, dtype=float)

    if x_mid is not None:
        a = np.array([x_mid, p1[1], 0.0])
        b = np.array([x_mid, p2[1], 0.0])
        segs = [Line(p1, a), Line(a, b), Line(b, p2)]
    elif y_mid is not None:
        a = np.array([p1[0], y_mid, 0.0])
        b = np.array([p2[0], y_mid, 0.0])
        segs = [Line(p1, a), Line(a, b), Line(b, p2)]
    else:
        # Default: go horizontal then vertical (2 segments)
        corner = np.array([p2[0], p1[1], 0.0])
        segs = [Line(p1, corner), Line(corner, p2)]

    wire = VGroup(*segs)
    wire.set_stroke(width=stroke_width)
    return wire


class DegenerateTerm(VGroup):
    """
    A 1-literal 'term' that skips an inner gate.
    Draws a label and a short stub; exposes get_out() like your gates.
    """
    def __init__(self, literal_tex: str, stub_len=0.7,
                 stroke_width=3, label_scale=1.2, label_buff=0.15, **kwargs):
        super().__init__(**kwargs)

        self.label = MathTex(literal_tex).scale(label_scale)

        # short output stub to the right
        self.stub = Line(ORIGIN, RIGHT * stub_len).set_stroke(width=stroke_width)

        # arrange label + stub as a small block
        self.label.next_to(self.stub, LEFT, buff=label_buff)
        self.add(self.label, self.stub)

        # live output pin so it moves with transforms
        self._out_pin = VectorizedPoint(self.stub.get_end())
        self.add(self._out_pin)

    def get_out(self):
        return self._out_pin.get_center()

    # optional: so it behaves similarly if you ever want input anchors
    def input_anchors(self):
        return []


class CircuitBuilder:
    def __init__(
        self,
        var_order=("A", "B", "C"),
        gate_scale=0.7,
        stroke_width=3,
        x_in=-5.5,
        x_term=-1.5,
        x_out=1.5,
        y_top=2.5,
        term_vgap=2.4,
        in_vgap=0.3,
        degenerate_stub_len=0.25,  # shorter wires when term has 1 literal
        degenerate_gap=0.15,
    ):
        self.var_order = list(var_order)
        self.gate_scale = gate_scale
        self.stroke_width = stroke_width
        self.x_in = x_in
        self.x_term = x_term
        self.x_out = x_out
        self.y_top = y_top
        self.term_vgap = term_vgap
        self.in_vgap = in_vgap
        self.degenerate_stub_len = degenerate_stub_len
        self.degenerate_gap = degenerate_gap

    def _literal_tex(self, var, val):
        # val==1 -> A, val==0 -> \overline{A}
        return var if val == 1 else rf"\overline{{{var}}}"

    def _make_inputs(self):
        """Input labels and anchor points (just points in space)."""
        inputs = VGroup()
        anchors = {}  # var -> position
        for i, v in enumerate(self.var_order):
            y = self.y_top - i * self.in_vgap
            t = MathTex(v).scale(1.1).move_to([self.x_in, y, 0])
            inputs.add(t)
            anchors[v] = t.get_right()
        return inputs, anchors

    def build_sop(self, sop_terms, output_label="F",
                  *,
                  degenerate_stub_len=0.35,
                  degenerate_label_buff=0.10, **kwargs):
        """
        sop_terms: list of terms, each term is list of (var, val) where val 1=non-inverted, 0=inverted.
        Builds: OR of AND terms.
        """
        return self._build(two_level_terms=sop_terms, inner="AND", outer="OR", output_label=output_label)

    def build_pos(self, pos_terms, output_label="F"):
        """
        pos_terms: list of sums, each sum is list of (var, val)
        Builds: AND of OR terms.
        """
        return self._build(two_level_terms=pos_terms, inner="OR", outer="AND", output_label=output_label)

    @staticmethod
    def _midline_y(points_top_to_bottom):
        ys = [p[1] for p in points_top_to_bottom]
        n = len(ys)
        if n == 0:
            return 0.0
        if n % 2 == 1:
            return ys[n // 2]
        # even: average the two middle
        return 0.5 * (ys[n // 2 - 1] + ys[n // 2])

    def _build(self, two_level_terms, inner, outer, output_label="F",
               degenerate_stub_len=0.35,
               degenerate_label_buff=0.10, **kwargs
               ):
        group = VGroup()

        gate_map = {}  # e.g. "t0" -> gate/term mob
        wire_map = {}  # e.g. "t0" -> wire from term -> final
        term_mobs = VGroup()

        for idx, term in enumerate(two_level_terms):
            # y = self.y_top - t_i * self.term_vgap
            leads = [self._literal_tex(v, val) for v, val in term]

            # Choose gate type for inner level
            if len(term) == 1:  # degenerate: single literal, skip inner gate
                term_mob = DegenerateTerm(
                    literal_tex=leads[0],
                    stub_len=degenerate_stub_len,
                    label_buff=degenerate_label_buff,
                    stroke_width=self.stroke_width,
                    label_scale=1.2,
                )
            else:
                if inner == "AND":
                    term_mob = AndGate(leads=leads)
                else:
                    term_mob = OrGate(leads=leads)

            term_mob.scale(self.gate_scale)
            gate_map[idx] = term_mob
            term_mobs.add(term_mob)
        group.add(term_mobs)

        # arrange/position the column
        term_mobs.arrange(DOWN, buff=0.6, aligned_edge=LEFT)
        term_mobs.to_edge(UP, buff=0.6)
        term_mobs.set_x(self.x_term)

        # outputs AFTER positioning
        term_outputs = [m.get_out() for m in term_mobs]

        # Final gate (combiner)
        if outer == "OR":
            final_gate = OrGate(leads=[None] * len(two_level_terms),
                                output_label=output_label).scale(2.4*self.gate_scale)
        else:
            final_gate = AndGate(leads=[None] * len(two_level_terms), output_label=output_label)

        final_gate.scale(self.gate_scale)
        final_gate.move_to([self.x_out, self.y_top - (len(two_level_terms)-1)*self.term_vgap/2, 0])
        final_gate.set_y(term_mobs[1].get_center()[1])
        group.add(final_gate)

        # --- Wiring ---
        wires = VGroup()
        # Wire term outputs into final gate inputs
        final_ins = final_gate.input_anchors()
        # final_ins = list(reversed(final_ins))
        x_mid = (self.x_term + self.x_out) / 2
        colors = [RED, BLUE, GREEN]
        # i=0
        term_outputs_sorted = sorted(term_outputs, key=lambda p: p[1], reverse=True)
        final_ins_sorted = sorted(final_gate.input_anchors(), key=lambda p: p[1], reverse=True)

        mid_term_y = self._midline_y(term_outputs_sorted)
        mid_pin_y = self._midline_y(final_ins_sorted)

        final_gate.shift(UP * (mid_term_y - mid_pin_y))
        # final_ins = final_gate.input_anchors()
        final_ins_sorted = sorted(final_gate.input_anchors(), key=lambda p: p[1], reverse=True)
        idx = 0
        for t_out, f_in in zip(term_outputs_sorted, final_ins_sorted, strict=False):
            p1 = np.array(t_out, dtype=float)
            p2 = np.array(f_in, dtype=float)
            wire = manhattan_wire(p1, p2, x_mid=x_mid, stroke_width=self.stroke_width)
            # wire.set_color(colors[i])
            wire_map[idx] = wire
            idx += 1
            wires.add(wire)
        group.add(wires)

        # test dots to understand geometry
        # dbg_in_dots = VGroup(*[
        #     Dot(p, radius=0.05) for p in final_ins
        # ]).set_color(YELLOW)
        # group.add(dbg_in_dots)

        # Helpful handles
        group.gates = gate_map
        group.wires = wire_map
        group.final_gate = final_gate

        return group
