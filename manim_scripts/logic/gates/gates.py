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
        output_label_scale=2.4,
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
            bubble = Circle(radius=notbubble).set_stroke(width=stroke_width)
            # place like schemdraw: center at (tip + notbubble, 0)
            bubble.move_to(np.array([tip + notbubble, 0.0, 0.0]))
            self.add(bubble)
            out_start = np.array([tip + notbubble * 2, 0.0, 0.0])
        else:
            out_start = np.array([tip, 0.0, 0.0])

        # Input spacing dy (schemdraw rules)
        if inputs == 2:
            dy = gateh * 0.5
        elif inputs == 3:
            dy = gateh * 0.33
        else:
            dy = gateh * 0.4
            backlen = dy * (inputs - 1)

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
                self.add(Line(np.array([0.0, y, 0.0]),
                              np.array([xback - notbubble * 2, y, 0.0])).set_stroke(width=stroke_width))
                # endpt = np.array([xback - notbubble * 2, y, 0.0])
            else:
                self.add(Line(np.array([0.0, y, 0.0]),
                              np.array([xback, y, 0.0])).set_stroke(width=stroke_width))
                # endpt = np.array([xback, y, 0.0])
            p_left = np.array([0.0, y, 0.0])  # back of lead (leftmost)
            # pin at the gate input point (x=0)
            pin = _pin(f"in{in_num}", np.array([0.0, y, 0.0]))

            # label at the *left* end of the lead
            lead_text = leads[i]  # NOTE: leads list is top->bottom in your i loop
            if lead_text is not None:
                lab = label_cls(str(lead_text), **label_kwargs).scale(label_scale)
                lab.next_to(p_left, LEFT, buff=label_buff)
                self.add(lab)

        # Extended back for large number of inputs
        if inputs > 3:
            self.add(Line(np.array([leadin_eff, backlen/2 + dy/2, 0]),
                          np.array([leadin_eff, orheight, 0])).set_stroke(width=stroke_width))
            self.add(Line(np.array([leadin_eff, -backlen/2 - dy/2, 0]),
                          np.array([leadin_eff, -orheight, 0])).set_stroke(width=stroke_width))

        # Output lead
        out_end = out_start + RIGHT * leadout
        self.add(Line(out_start, out_end).set_stroke(width=stroke_width))

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
        # i is 0-based: 0,1,2...
        return np.array(self.anchors[f"in{i + 1}"], dtype=float)

    def get_out(self):
        return np.array(self.anchors["out"], dtype=float)

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
        gate = AndGate().to_edge(RIGHT)
        self.play(Create(gate))

        ins = gate.input_anchors(2)
        out = gate.output_anchor()

        a = Tex("A").next_to(ins[0], LEFT)
        b = Tex("B").next_to(ins[1], LEFT)

        wa = Line(a.get_right(), ins[0])
        wb = Line(b.get_right(), ins[1])
        wo = Line(out, out + RIGHT*1.5)

        self.play(Write(a), Write(b))
        self.play(Create(wa), Create(wb), Create(wo))
