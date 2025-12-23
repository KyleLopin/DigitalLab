# Copyright (c) 2025 Kyle Lopin (Naresuan University) <kylelopin@gmail.com>

"""
Make the intro scene for a Manim video on KMaps, this starts with a 2x2 map
built from a truth table and goes through 3 scenes with the following:
minTerm 2,
minTerm 2, 4
minTerm 0, 2, 4
"""

__author__ = "Kyle Vitautas Lopin"

# installed libraries
from manim import *
from manim_studio import LiveScene

# for manim-studio
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

# local files
import context
from helpers.anim_helpers import (pulse)
from elements.TruthTable import TruthTable
from elements.KMaps import KarnaughMap
from gates.gates import *
# There will be a slide with main points that gets built up
# during video, it is stored in IntermissionSlides
from helpers.base import IntermissionSlides, KMapBase  # is a Scene with watermark
from helpers.timing_helpers import TimingHelpers

numbers_font = "Menlo"
# text_font = "Felix Titling"
text_font = "Monaco"
fancy_font = "Noteworthy"
header1_size = 38
header2_size = 32
SET_CUE = True

mono = TexTemplate()
mono.add_to_preamble(r"\usepackage{inconsolata}")  # nice mono font


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


def circuit_two_ands_into_or(
    *,
    and1_leads=(r"A", r"\bar{B}"),
    and2_leads=(r"A", r"B"),
    out_label=r"F",
    scale=1,
    stroke=3,
    bus_offset=0.4,
    gate_shift=LEFT*1.5,
    out_shift=ORIGIN,
):
    # Gates
    and1 = AndGate(leads=list(and1_leads)).scale(scale * 0.7)
    and2 = AndGate(leads=list(and2_leads)).scale(scale * 0.7)
    or_g = OrGate(leads=[None, None], output_label="F").scale(scale*1)

    and1.shift(UP*0.8 + gate_shift)
    and2.shift(DOWN*0.8 + gate_shift)
    or_g.shift(out_shift)

    y_mid = (and1.get_out()[1] + and2.get_out()[1]) / 2
    or_g.to_y(y_mid)

    # Wires (orthogonal)
    x_bus = or_g.get_left()[0] - bus_offset
    wires = VGroup(
        manhattan_wire(and1.get_out(), or_g.get_in(0), x_mid=x_bus, stroke_width=stroke),
        manhattan_wire(and2.get_out(), or_g.get_in(1), x_mid=x_bus, stroke_width=stroke),
    )

    circuit = VGroup(and1, and2, or_g, wires)
    # handy handles if you want to animate later:
    circuit.and1 = and1
    circuit.and2 = and2
    circuit.or_g = or_g
    circuit.wires = wires
    return circuit


TIMES = {"start": 0,  # to build the cue slides so i can pass ._cue to exclude on Intermissin slides
         "intro_subheader2": 3,
         "end_intro": 6,
         "example 1": 8,
         "tt_intro": 10,
         # "tt_end": 25,
         "KMap1_start": 15,
         "kmap_vars": 20,
         "kmap_labels": 25,
         "add AB00": 30,
         "move_minterms": [33, 36, 39, 42],
         # "explain_implicants": 66,
         "explain_implicants": [55, 58, 61, 64, 67, 70, 83, 86],
         "implicants": [72],
         "circuit minTerm 1": 76,
         # "implicant ab 1 start": 25,
         "intermissions": [82, 110, 140, 170, 200],
         "intermission ends": [92, 122, 135, 182, 210],

         "add minTerm3": 95,

         # "explain ab' 10": 89,

         "implicant ab 1 end": 92,

         "add implicant 2": 98,
         "fade out implicant 2": 110,
         "show non prime eqn": 104,
         "show non prime circuit": 105,
         "prime implicant1 label": 107,
         "simplify 1": [110, 115, 118, 121],

         "video plug1": 138,
         "larger implicant": 139,

         "pulse ab'": 158,
         "pulse ab": 160,
         "pulse x=a1": 162,
         "pulse x=a": 165,

         "pulse b0": 168,
         "pulse b1": 169,

         "pulse (b+b')": 178,

         "add minterm 0":190,
         "add implicant m0": 192,

         "add implicant a'b'": 194,

         "add prime implicant 2": 196,

         "pulse B 0": 200,
         "pulse A 01": 204,
         "explain prime implicants 2": 198,
         "explain implicant expansion": 202,
         "explain prime implicant 2-2": 206,
         "add back implicant A": 210,
         "add full eqn": 215,
         "highlight OR point": 218,
         "add full circuit": 220,
         }

TEXT_SCALE = 32
PULSE_SCALE = 1.5
EQ_FONTSIZE = 64

KMAP_POINTS = [  # used for IntermissionsSlide
    "Rule 1)|Each implicant becomes an AND term",
    "Rule 2)|The final Boolean function is the OR of all required implicants\n(Sum-of-Products, SOP)",
    "Rule 3)|Implicant sizes are powers of 2, e.g.:\n1×1, 1×2, 2×1, 2×2, 2×4, 4×2, 4×4, etc.",
    "Rule 4)|Prime implicants are the largest possible valid implicants",
    "Rule 5)|A single 1 can be grouped into multiple implicants",
]


# class IntermissionSlides:
#     """
#     Reusable intermission “points slide” controller.
#
#     Call `.show(scene, content)` repeatedly; each call reveals one additional bullet.
#     The helper stores its internal slide and counter.
#     The slide it shows is built in _build_slide()
#     """
#     title: str
#     bullets: list[str]
#
#     # Objects that should NOT be faded out (e.g., watermark, cue label)
#     exclude: list[Mobject] = field(default_factory=list)
#
#     # Styling knobs (override if you want)
#     title_size: int = 46
#     text_size: int = 34
#     width: float = 11.0
#     slide_buff: float = 0.45
#     bullet_buff: float = 0.25
#
#     TITLE_FONT = "Avenir Next"
#     TEXT_FONT = "Avenir Next"
#
#     # Internal state
#     # _slide is the slide this Class shows
#     _slide: VGroup | None = field(default=None, init=False, repr=False)
#     # _i keeps track of which bullet points are shown
#     _i: int = field(default=0, init=False, repr=False)
#
#     def _build_slide(self) -> VGroup:
#         """Create the slide and hide all bullets initially."""
#         print(f"Building slide {self.title}")
#         t = Text(self.title, font_size=self.title_size, weight=BOLD,
#                  font=self.TITLE_FONT)
#         # self.items = VGroup(*[Text(p, font_size=self.text_size, weight=BOLD,
#         #                       font=self.TEXT_FONT) for p in self.bullets])
#         self.items = VGroup(*[
#             self.make_hanging_item(p, font=self.TEXT_FONT,
#                                    label_size=int(self.text_size*0.95),
#                                    body_size=self.text_size,
#                                    ) for p in self.bullets
#                               ])
#
#         # IMPORTANT: arrange them so they don't overlap
#         self.items.arrange(DOWN, aligned_edge=LEFT, buff=self.bullet_buff)
#
#         # Align all bodies to the same left x (hanging indent)
#         bodies = VGroup(*[
#             it[1] for it in self.items
#             if isinstance(it, VGroup) and len(it) >= 2
#         ])
#         if len(bodies) > 0:
#             target_left_x = bodies[0].get_left()[0]
#             for b in bodies:
#                 b.shift(RIGHT * (target_left_x - b.get_left()[0]))
#
#         _slide = VGroup(t, self.items
#                         ).arrange(DOWN, buff=self.slide_buff, aligned_edge=LEFT
#                                   ).move_to(ORIGIN)
#         _slide.set_width(self.width)
#         # hide all bullets initially
#         for item in self.items:
#             item.set_opacity(0)
#
#         # Make an all black slide to hide the orignal slide to project new intermission slide on
#         self.cover = Rectangle(width=config.frame_width,
#                           height=0.8 * config.frame_height
#                           ).set_fill(BLACK, 1).set_stroke(
#             width=0).set_z_index(1000)
#
#         return _slide
#
#     def reset(self) -> None:
#         """Reset bullet reveal progression back to the start."""
#         self._i = 0
#         if self._slide is not None:
#             bl: BulletedList = self._slide[1]
#             for item in bl:
#                 item.set_opacity(0)
#
#     def split_label_body(self, s: str, sep: str = "|") -> tuple[str | None, str]:
#         """Split 'LABEL|BODY'. If no sep, returns (None, s)."""
#         if sep in s:
#             left, right = s.split(sep, 1)
#             return left.strip(), right.strip()
#         return None, s
#
#     def make_hanging_item(self, s: str,
#             *,
#             sep: str = "|",
#             font: str = "Avenir Next",
#             label_size: int = 36,
#             body_size: int = 36,
#             label_buff: float = 0.25,
#             line_spacing: float = 0.9,
#     ) -> VGroup | Text:
#         label_txt, body_txt = self.split_label_body(s, sep=sep)
#
#         body = Text(body_txt, font=font, font_size=body_size, line_spacing=line_spacing)
#
#         if label_txt is None:
#             return body
#
#         label = Text(label_txt, font=font, font_size=label_size, weight="BOLD")
#
#         item = VGroup(label, body).arrange(RIGHT, buff=label_buff, aligned_edge=UP)
#         return item
#
#     def highlight(self, scene, idx,
#                   dim_opacity=0.25, hi_opacity=1.0,
#                   hi_color=YELLOW,
#                   fade_rt: float = 0.6,
#                   reveal_rt: float = 0.4,
#                   wait_to: str = "",
#                   ):
#         """Return animations to highlight bullet `idx` WITHOUT touching self.i."""
#         anims = []
#         for j, m in enumerate(self.items):
#             if j == idx:
#                 anims += [
#                     m.animate.set_opacity(hi_opacity).set_color(hi_color),
#                     Indicate(m, scale_factor=1.06),
#                 ]
#             else:
#                 anims.append(m.animate.set_opacity(dim_opacity).set_color(WHITE))
#         # return anims
#         if self._slide is None:
#             raise AttributeError("self._slide not initiated yet, call .show() first")
#         self._slide.set_z_index(1001)
#         # add black cover to hide current objects
#         scene.play(FadeIn(self.cover), run_time=fade_rt)
#         # then show the intermission slide
#         # scene.play(FadeIn(self._slide), run_time=reveal_rt)
#         scene.play(*anims, run_time=1)
#         if wait_to:
#             try:
#                 scene.wait_to(TIMES["highlight OR point"], self._i-1)  # self._i already incremented
#             except Exception as e:
#                 print(f"wait_to should be in TIMES dict got: {e}")
#
#         # remove _slide and FadeOut the cover which is same as FadeIn old scene
#         scene.play(FadeOut(self._slide), run_time=fade_rt)
#         scene.play(FadeOut(self.cover), run_time=reveal_rt)
#
#
#     def show(
#         self,
#         scene: Scene,
#         *,
#         fade_rt: float = 0.6,
#         hold: float = 1.8,
#         reveal_rt: float = 0.4,
#         dim: float = 0.15,
#         use_dim: bool = False,
#         wait_to: str = "",
#     ) -> None:
#         """
#         Fade out everything currently on-screen EXCEPT `exclude`,
#         show the slide, reveal the next bullet, fade the slide out,
#         then bring everything back.
#
#         Call repeatedly to reveal bullets one-by-one.
#         """
#         if self._slide is None:
#             self._slide = self._build_slide()
#
#         bullets: BulletedList = self._slide[1]
#
#         # Snapshot everything currently on screen, excluding chosen objects + the slide itself (if present)
#         exclude_set = set(self.exclude)
#         exclude_set.add(self._slide)
#
#         # If there are bullets, reveal next (clamped so extra calls keep all visible)
#         if len(bullets) > 0:
#             idx = min(self._i, len(bullets) - 1)
#         else:
#             idx = None
#
#         self._slide.set_z_index(1001)
#         # add black cover to hide current objects
#         scene.play(FadeIn(self.cover), run_time=fade_rt)
#         # then show the intermission slide
#         scene.play(FadeIn(self._slide), run_time=reveal_rt)
#
#         # reveal next bullet
#         if idx is not None:
#             bullets[idx].set_opacity(1)
#             scene.play(Write(bullets[idx]), run_time=reveal_rt)
#             self._i = min(self._i + 1, len(bullets))
#
#         if wait_to:
#             try:
#                 scene.wait_to(wait_to, self._i-1)  # self._i already incremented
#             except Exception as e:
#                 print(f"wait_to should be a list, got error: {e}")
#
#         # remove _slide and FadeOut the cover which is same as FadeIn old scene
#         scene.play(FadeOut(self._slide), run_time=fade_rt)
#         scene.play(FadeOut(self.cover), run_time=reveal_rt)


class KMap2VarInstruct(KMapBase, TimingHelpers):
    def construct(self):
        # region setup
        # self.next_section(skip_animations=True)
        wm = self.add_watermark()
        self.setup()
        Text.set_default(font="Menlo")  # for KMaps to work properly

        # Set up the intermission slides
        # inter_title = Text("Karnaugh Maps Rules:", font_size=48, weight=BOLD)
        intermission = IntermissionSlides(title = "Karnaugh Maps Rules:",
                                          bullets=KMAP_POINTS,
                                          exclude=[wm],)
        # attach times
        self.attach_times(TIMES)
        # endregion setup

        # region Intro
        # Title header
        header = Text("Introduction to Karnaugh Maps", font_size=header1_size,
                      weight=BOLD, font=text_font)

        bullet = "• "
        # make 2 lines justified
        line1 = Text(bullet + "Build Karnaugh maps from truth tables", font_size=28, font=text_font)
        line2 = Text(bullet + "Get the implicants and their terms", font_size=28, font=text_font)
        line3 = Text(bullet + "Write the Boolean equation ", font_size=28, font=text_font)
        line4 = Text(bullet + "Draw the logic circuit ", font_size=28, font=text_font)

        subheader = VGroup(line1, line2, line3, line4
                           ).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        subheader.next_to(header, DOWN, buff=0.20).align_to(header, LEFT).shift(RIGHT * 0.6)
        # put this in 1 block to get the spacing correct
        title_block = VGroup(header, subheader).arrange(DOWN, buff=0.75)
        self.play(Write(header), run_time=1)
        self.play(Write(subheader), run_time=TIMES["intro_subheader2"])
        self.wait_to("end_intro")
        self.play(FadeOut(subheader))

        # region Part 1 intro

        # endregion Part 1 intro
        # endregion Intro

        # endregion Intro
        # return
        # region truth table
        truth_table = TruthTable(inputs=["A", "B"],
            outputs=["x"], minterms=[2], scale=3)

        self.play(truth_table.write_all(), run_time=5)

        self.wait_to("tt_intro")

        self.play(
            truth_table.animate.scale(0.7).to_corner(UR, buff=1.0).shift(0.3*UP),
            run_time=1.0
        )
        # endregion truth table

        # region kmap
        kmap_2x2_1 = KarnaughMap(num_vars=2,
                                 var_names=["A", "B"],
                                 stroke_width=4)
        kmap_2x2_1.shift(LEFT*1.9).scale(1.5)
        # self.play(kmap_2x2_1.write_all(run_time=2.0))
        self.play(FadeIn(kmap_2x2_1.cells_group))
        self.wait_to("KMap1_start")

        # draw kmaps A and B to link
        self.play(kmap_2x2_1.write("vars"), run_time=2)
        self.wait_to("kmap_vars")

        # draw kmaps A and B to link
        self.play(kmap_2x2_1.write("labels"), run_time=2)
        self.wait_to("kmap_labels")
        # endregion kmap

        # region helper functions
        def minterm_bit(min_term: int, inputs: list[str], var: str) -> int:
            """Return 0/1 for var in this minterm, using inputs order (A=MSB ... last=LSB)."""
            n = len(inputs)
            i = inputs.index(var)  # column index in your truth table
            shift = n - 1 - i  # MSB first
            return (min_term >> shift) & 1

        def pulse_var_reveal_min_term(vars, min_term, runtime=0.5):
            inputs = truth_table.inputs
            n_inputs = len(inputs)

            anims = []
            for i, var in enumerate(vars):
                var_tt = truth_table.get_var_label(var)
                var_digit_tt = truth_table.get_cell(row=min_term, col=i)
                # print(var_tt, var_digit_tt)
                # --- compute 0/1 for this var at this minterm ---
                val = minterm_bit(min_term, inputs, var)
                var_kmap = kmap_2x2_1.get_var_label(var)
                var_digit_kmap = kmap_2x2_1.get_var_digits(var, val)

        def get_kmap_var_digit(var, val):
            var_kmap = kmap_2x2_1.get_var_label(var)
            var_digit_kmap = kmap_2x2_1.get_var_digits(var, val)
            return [var_kmap, var_digit_kmap]

        def get_var_digits(var, val, tt_r_c):
            var_tt = truth_table.get_var_label(var)
            print(tt_r_c)
            var_digit_tt = truth_table.get_var_digits(row=tt_r_c[0], col=tt_r_c[1])
            var_kmap = kmap_2x2_1.get_var_label(var)
            var_digit_kmap = kmap_2x2_1.get_var_digits(var, val)
            return [var_tt, var_digit_tt, var_kmap, var_digit_kmap]

        # endregion helper functions

        # region map tt to kmap
        # highlight A 0 on truth table then K-Map
        # first time running, so figure out the loop later
        self.wait_to("add AB00")
        items = get_var_digits("A", 0, (0, 0))
        anims = [pulse(m, scale=1.5, run_time=0.8) for m in items]
        for m in items:
            m.set_color(BLUE)
        # self.play(a_a0_tt.animate.scale(2))
        self.play(*anims)

        # highlight A 0 on truth table then K-Map
        items = get_var_digits("B", 0, (0, 1))
        anims = [pulse(m, scale=1.5, run_time=0.8) for m in items]
        for m in items:
            m.set_color(YELLOW)
        # self.play(a_a0_tt.animate.scale(2))
        self.play(*anims)

        # move the 0 in minterm 0 to the KMap
        tt_cell_min0 = truth_table.get_cell(row=0, col=2)
        k_map_cell_min0, _ = kmap_2x2_1.get_cell_from_minterm(0)

        tt_cell_min0.set_color(ORANGE)
        # make a moving copy
        tt_cell_copy = tt_cell_min0.copy()

        # bring it above so it draws on top
        tt_cell_copy.set_z_index(10)

        self.add(tt_cell_copy)  # add the copy to the scene
        tt_cells1 = []
        tt_cells1.append(tt_cell_min0)

        # animate copy to the kmap location
        self.play(tt_cell_copy.animate.move_to(k_map_cell_min0.get_center()), run_time=2)

        self.wait_to("move_minterms", 0)

        ab_states = [(0, 0), (0, 1), (1, 0), (1, 1)]
        minterm_colors = [ORANGE, TEAL_B, PURPLE, GREEN_C]
        kmap_values = {}
        kmap_values[0] = tt_cell_copy
        for i in range(1, 4):
            self.wait_to("move_minterms", i)
            state_a, state_b = ab_states[i]
            items = get_var_digits("A", state_a, (i, 0))
            anims = [pulse(m, scale=1.5, run_time=0.8) for m in items]
            for m in items:
                m.set_color(BLUE)
            # self.play(a_a0_tt.animate.scale(2))
            self.play(*anims)
            self.wait(2)

            # highlight A 0 on truth table then K-Map

            items = get_var_digits("B", state_b, (i, 1))
            anims = [pulse(m, scale=1.5, run_time=0.8) for m in items]
            for m in items:
                m.set_color(YELLOW)
            # self.play(a_a0_tt.animate.scale(2))
            self.play(*anims)
            self.wait(2)

            # move the minterm in truth table to the minTerm on KMap
            tt_cell_min = truth_table.get_cell(row=i, col=2)
            k_map_cell_min, _ = kmap_2x2_1.get_cell_from_minterm(i)
            tt_cell_min.set_color(minterm_colors[i])
            # make a moving copy
            tt_cell_copy = tt_cell_min.copy()

            # bring it above so it draws on top
            tt_cell_copy.set_z_index(10)

            self.add(tt_cell_copy)  # add the copy to the scene
            tt_cells1.append(tt_cell_min)
            kmap_values[i] = tt_cell_copy
            # animate copy to the kmap location
            self.play(tt_cell_copy.animate.move_to(k_map_cell_min.get_center()), run_time=2)
        # endregion map tt to kmap

        # region implicants 1
        self.wait_to("explain_implicants", 0)
        # Make implicant / prime implicant
        implicant1 = kmap_2x2_1.highlight_group([2], color=RED,
                                               stroke_width=8, buff=-.2)
        self.play(FadeIn(implicant1), run_time=2)
        self.wait_to("implicants", 0)


        self.wait_to("explain_implicants", 1)
        # implicant1_label = MathTex(r"\text{Implicant: } A\overline{B}", font_size=54)
        implicant1_label = MathTex(
            r"\text{Implicant: }", r"A", "\\cdot", r"\overline{B}",
            font_size=54, tex_template=mono
        )
        implicant1_label.next_to(implicant1, UP, buff=1.8).shift(1.9*RIGHT)
        connector = Line(
            implicant1_label.get_bottom(),
            implicant1.get_corner(UR),
            stroke_width=5
        )
        self.play(
            Write(implicant1_label[0]),
            Create(connector),
            run_time=1.2
        )
        self.wait_to("explain_implicants", 1)

        # pulse A is 1 show A
        # looks dumb but its easier to not be DRY sometimes
        ab_state = (1, 0)
        items = get_kmap_var_digit("A", ab_state[0])
        anims = [pulse(m, scale=1.5, run_time=1) for m in items]
        implicant1_label[1].set_color(BLUE)
        anims.append(Write(implicant1_label[1], run_time=2))
        self.play(*anims)
        self.wait_to("explain_implicants", 2)

        items = get_kmap_var_digit("B", ab_state[1])
        anims = [pulse(m, scale=1.5, run_time=0.8) for m in items]
        implicant1_label[3].set_color(YELLOW)
        anims.append(Write(implicant1_label[2], run_time=2))
        anims.append(Write(implicant1_label[3], run_time=2))
        self.play(*anims)
        self.wait_to("explain_implicants", 3)

        self.explain_implicant = MathTex("1", "\\cdot", r"\overline{0}", font_size=54)
        self.explain_implicant.scale(
            implicant1_label.get_height() / self.explain_implicant.get_height())
        self.explain_implicant.next_to(implicant1_label, DOWN, buff=0.2)
        self.explain_implicant.align_to(implicant1_label, RIGHT).shift(0.06*LEFT)
        self.play(self.explain_implicant[0].animate.set_color(BLUE))
        self.play(Write(self.explain_implicant[1]))
        self.play(self.explain_implicant[2].animate.set_color(YELLOW))
        self.wait_to("explain_implicants", 4)

        # explain 10' is 1*1
        explain_implicant2 = MathTex("1", "\\cdot", "1",
                                     font_size=54, tex_template=mono)
        explain_implicant2[0].set_color(BLUE)
        explain_implicant2[2].set_color(YELLOW)
        explain_implicant2.scale( 0.85 *  # this is only one with not overhead bar so shrink
            implicant1_label.get_height() / explain_implicant2.get_height())
        explain_implicant2.next_to(self.explain_implicant, DOWN, buff=0.2)
        explain_implicant2.align_to(implicant1_label, RIGHT).shift(0.06*LEFT)

        self.play(Write(explain_implicant2[0]))
        self.play(Write(explain_implicant2[1]))
        self.play(Write(explain_implicant2[2]))

        explain_implicant3 = MathTex("=1", font_size=54, tex_template=mono)
        explain_implicant3.scale(0.85 *  # this is only one with not overhead bar so shrink
                                 implicant1_label.get_height() / explain_implicant3.get_height())
        explain_implicant3.next_to(explain_implicant2, DOWN, buff=0.2)
        explain_implicant3.align_to(implicant1_label, RIGHT).shift(0.06 * LEFT)
        self.play(Write(explain_implicant3))

        # show the ab' AND gate circuit
        ab_circuit = AndGate(leads=(r"A", r"\overline{B}"), output_label="x").scale(0.7)
        ab_circuit.shift(2.3*RIGHT + 0.8*DOWN)
        self.wait_to("circuit minTerm 1")

        self.play(Write(ab_circuit),
                  truth_table.animate.scale(0.75).to_corner(UR, buff=0.6),
                  run_time=2)
        # self.wait_to("intermissions", 0)
        # region show slide pt1
        intermission.show(self, wait_to="intermission ends")  # index: 0
        # endregion show slide pt1

        # self.wait_to("implicant ab 1 end")
        self.play(FadeOut(ab_circuit, implicant1_label,
                          connector, self.explain_implicant, explain_implicant2,
                          explain_implicant3), run_time=1)
        # endregion implicants 1

        self.wait_to("add minTerm3")

        # change the maxTerm3 to minTerm3 on the KMap and truth table
        tt_cell_min3 = truth_table.get_cell(row=3, col=2)
        anims = []

        for txt in [tt_cell_min3, kmap_values[3]]:
            new_txt = Text("1", font=numbers_font, font_size=txt.font_size)
            new_txt.move_to(txt).match_style(txt)
            anims.append(Transform(txt, new_txt))
        self.play(*anims)
        self.wait_to("add implicant 2")
        implicant2 = kmap_2x2_1.highlight_group([3], color=RED,
                                                stroke_width=8, buff=-.2)
        self.play(Create(implicant2), run_time=2)
        implicant2_label = MathTex("Implicant: AB", font_size=54)
        implicant2_label.next_to(implicant2, DOWN, buff=1.4).shift(1.8 * RIGHT)
        connector = Line(
            implicant2_label.get_top(),
            implicant2.get_corner(DR),
            stroke_width=5
        )
        self.play(
            Write(implicant2_label),
            Create(connector), run_time=1.2
        )

        self.wait_to("fade out implicant 2")
        self.play(FadeOut(implicant2_label, connector))
        # pulse both implicants and show circuit

        self.play(
            implicant1.animate.scale(PULSE_SCALE),
            implicant2.animate.scale(PULSE_SCALE),
            run_time=1
        )
        self.play(
            implicant1.animate.scale(1 / PULSE_SCALE),
            implicant2.animate.scale(1 / PULSE_SCALE),
            run_time=1
        )

        # 1) Build equation and isolate the two terms so we can point to them
        eq = MathTex(
            r"X = A\overline{B} + AB",
            substrings_to_isolate=[r"A\overline{B}", r"AB"],
            font_size=EQ_FONTSIZE,
        )
        eq.to_edge(UP, buff=0.6).shift(1.0*RIGHT)

        term1 = eq.get_part_by_tex(r"A\overline{B}")
        term2 = eq.get_part_by_tex(r"AB")

        # 2) Connector lines (use always_redraw so they track if you move things later)
        conn_anotb = always_redraw(lambda:
                              Line(term1.get_bottom(), implicant1.get_corner(UR), stroke_width=4)
                              )
        conn_ab = always_redraw(lambda:
                              Line(term2.get_bottom(), implicant2.get_corner(UR), stroke_width=4)
                              )
        # 3) Animate
        self.wait_to("show non prime eqn")
        self.play(Write(eq), run_time=1.2)
        self.play(Create(conn_anotb), Create(conn_ab), run_time=0.6)
        self.wait_to("show non prime circuit")

        truth_table.save_state()
        ckt = circuit_two_ands_into_or(
            and1_leads=(r"A", r"\overline{B}"),  # bar on top
            and2_leads=(r"A", r"B"),
            out_label=r"X"
        ).scale(0.7)
        ckt.shift(3.1*RIGHT + 0.3*DOWN)
        self.play(Create(ckt),
                  # truth_table.animate.scale(0.75).to_corner(UR, buff=0.6),
                  run_time=2)
        intermission.show(self, wait_to="intermission ends")  # index: 1

        # MOVED: do implicant expansion first
        prime_implicant1 = kmap_2x2_1.highlight_group([2, 3], color=RED,
                                                      stroke_width=8, buff=-.2)
        self.wait_to("prime implicant1 label")
        self.play(
            ReplacementTransform(implicant1.copy(), prime_implicant1),
            FadeOut(implicant2, implicant1),
            FadeOut(ckt, conn_anotb, conn_ab),
            run_time=1.4
        )
        prime_implicant1_label = (Tex(r"\text{Prime Implicant}", font_size=EQ_FONTSIZE, color=RED)
                                  .next_to(prime_implicant1, RIGHT, buff=0.35))
        self.play(Write(prime_implicant1_label))

        self.wait_to("simplify 1", 0)

        # First simplified equation
        eq1 = MathTex(
            r"X = A\left(B + \overline{B}\right)",
            font_size=EQ_FONTSIZE
        )
        eq1.next_to(eq, DOWN, buff=0.15)

        # Final simplified equation
        eq2 = MathTex(
            "X = A\\cdot 1",
            font_size=EQ_FONTSIZE
        )

        # Final simplified equation
        eq3 = MathTex(r"X = A", font_size=EQ_FONTSIZE, color=RED)
        eq2.next_to(eq1, DOWN, buff=0.15)
        eq2.align_to(eq1, RIGHT)
        eq3.next_to(eq2, DOWN, buff=0.25)
        eq3.align_to(eq2, RIGHT)

        # Animate
        self.play(Write(eq1), run_time=1.0)
        self.wait_to("simplify 1", 1)
        self.play(Write(eq2), run_time=1)
        self.wait_to("simplify 1", 2)
        self.play(Write(eq3), run_time=1)
        self.wait_to("simplify 1", 3)

        intermission.show(self, wait_to="intermission ends")  # index: 2

        self.wait_to("pulse ab")
        t1 = eq.get_part_by_tex(r"A\overline{B}")
        t2 = eq.get_part_by_tex(r"AB")

        self.play(Indicate(t1))
        self.wait_to("pulse ab")
        self.play(Indicate(t2))
        self.wait_to("pulse x=a1")
        self.play(Indicate(eq2))

        self.wait_to("pulse x=a")
        self.play(Indicate(eq3), run_time=1)

        # A Prime implicant is the largest implicant that can be formed by grouping 1's together
        # As the implicant size is 1 column, and 2 rows, it spans B is 0 and B is 1
        # Pulse B=0 then B=1 (digits + restore each time)
        self.wait_to("pulse b0")
        pulse0, restore0 = kmap_2x2_1.pulse_var_digits("B", 0, color=YELLOW, scale_factor=1.4, run_time=0.25)
        self.play(pulse0)
        self.play(Restore(restore0), run_time=0.5)

        self.wait_to("pulse b1")
        pulse1, restore1 = kmap_2x2_1.pulse_var_digits("B", 1, color=YELLOW, scale_factor=1.4, run_time=0.25)
        self.play(pulse1)
        self.play(Restore(restore1), run_time=0.5)

        intermission.show(self, wait_to="intermission ends")  # index: 3

        # remove all the prime implicant 1 stuff
        self.play(FadeOut(prime_implicant1_label, eq, eq1, eq2, eq3), run_time=1)
        # convert M0 to m0
        # change the maxTerm3 to minTerm3 on the KMap and truth table
        tt_cell_min0 = truth_table.get_cell(row=0, col=2)
        anims = []

        # self.next_section("Running")

        for txt in [tt_cell_min0, kmap_values[0]]:
            new_txt = Text("1", font=numbers_font, font_size=txt.font_size)
            new_txt.move_to(txt).match_style(txt)
            anims.append(Transform(txt, new_txt))
        self.play(*anims)
        self.wait_to("add implicant m0")
        implicant3 = kmap_2x2_1.highlight_group([0], color=ORANGE,
                                                stroke_width=8, buff=-.2)
        self.play(Create(implicant3), run_time=2)

        implicant3_label = MathTex(r"Implicant: \overline{A}\,\overline{B}",
                                   font_size=54, color=ORANGE)
        implicant3_label.next_to(implicant3, UP, buff=2.0).shift(1.7 * LEFT)

        connector = Line(
            implicant3_label.get_bottom(),
            implicant3.get_corner(UL),
            stroke_width=5, color=ORANGE,
        )
        self.play(
            Write(implicant3_label),
            Create(connector),
            run_time=1.2
        )
        self.wait_to("add implicant a'b'")
        # make scene to explain implicant a'b' to b'
        prime_implicant2 = kmap_2x2_1.highlight_group([0, 2], color=ORANGE,
                                                      stroke_width=8, buff=-.2)
        self.wait_to("add prime implicant 2")
        prime_implicant2_label = MathTex(r"\text{Prime Implicant:} \overline{B}",
                                         font_size=54, color=ORANGE)
        prime_implicant2_label.move_to(implicant3_label)

        # bring back later when explaining implicant expansion
        implicant3.save_state()
        implicant3_label.save_state()

        self.play(Transform(implicant3, prime_implicant2),
                  # FadeOut(implicant3_label, connector),
                  Transform(implicant3_label, prime_implicant2_label),
                  run_time=1)

        self.wait_to("explain prime implicants 2")

        intermission.show(self, wait_to="intermission ends")   # index: 4

        # explain you can do this because you can expand across
        # 1 variable, for b' you expand across A because A can
        # be 0 or 1
        # B = 0
        self.wait_to("pulse B 0")
        pulse_, digits = kmap_2x2_1.pulse_var_digits("B", 0, color=YELLOW, scale_factor=1.4, run_time=0.25)
        self.play(pulse_)
        self.play(Restore(digits), run_time=0.15)

        # A = 0
        pulse0, digits0 = kmap_2x2_1.pulse_var_digits("A", 0, color=YELLOW, scale_factor=1.4, run_time=0.25)

        # A = 1
        pulse1, digits1 = kmap_2x2_1.pulse_var_digits("A", 1, color=YELLOW, scale_factor=1.4, run_time=0.25)
        self.wait_to("pulse A 01")
        self.play(AnimationGroup(pulse0, pulse1, lag_ratio=0), run_time=0.35)

        self.play(
            AnimationGroup(Restore(digits0), Restore(digits1), lag_ratio=0),
            run_time=0.35
        )

        self.wait_to("explain implicant expansion")

        rule_text = MathTex(
            r"\text{Doubling a dimension of an implicant}\\",
            r"\text{ removes one variable from the equation}",
            font_size=44
        ).shift(2.5*DOWN + RIGHT*0)
        self.play(Write(rule_text))

        # explain a'b' to b' is removing a

        # Save PRIME state (store it as another snapshot)
        prime_state_box = implicant3.copy()
        prime_state_lbl = implicant3_label.copy()

        self.wait_to("explain prime implicant 2-2")
        self.play(Restore(implicant3),
                  Restore(implicant3_label), run_time=2)

        # Forward to PRIME again
        self.play(
            Transform(implicant3, prime_state_box),
            Transform(implicant3_label, prime_state_lbl),
            run_time=2
        )

        # add in A+B'
        self.play(FadeOut(rule_text))

        # prime_implicant2_label = MathTex("Prime Implicant: A",
        #                                  font_size=54, color=RED)

        prime_implicant1_label = MathTex(r"\text{Prime Implicant:} {A}",
                                         font_size=54, color=RED)
        prime_implicant1_label.shift(2.2*RIGHT+1.2*DOWN)

        connector = Line(
            prime_implicant1_label.get_left(),
            prime_implicant1.get_right(),
            stroke_width=5, color=RED, buff=0.1,
        )
        self.wait_to("add back implicant A")
        self.play(Write(prime_implicant1_label), Write(connector) )

        final_eqn = MathTex(
            r"X = A + \overline{B}",
            font_size=EQ_FONTSIZE
        )
        final_eqn.next_to(prime_implicant1_label, UP, buff=0.4)
        self.wait_to("add full eqn")
        self.play(Create(final_eqn), run_time=1)

        intermission.highlight(self, 1, wait_to="highlight OR point")

        ckt = OrGate(leads=[r"\overline{B}", "A"], output_label="X")
        ckt.next_to(final_eqn, UP, buff=0.4).scale(1.5)
        self.wait_to("add full circuit")
        self.play(Create(ckt), run_time=1)

        self.wait(2)


class GatePreview(Scene):
    def construct(self):
        # stroke = 3
        #
        # # Gates
        # # not_b = NotGate(leads=["B"]).shift(UP * 1.2)
        # and1 = AndGate(leads=["A", "B'"]).shift(UP * 1 + LEFT * 1.5).scale(0.7)
        # and2 = AndGate(leads=["A", "B"]).shift(DOWN * 1 + LEFT * 1.5).scale(0.7)
        # or_g = OrGate(leads=[None, None], output_label="F")
        #
        # # Wires
        # x_bus = or_g.get_left()[0] - 0.4
        # wires = VGroup(
        #     # AND1 -> OR
        #     # Line(and1.get_out(), or_g.get_in(0)).set_stroke(width=stroke),
        #     manhattan_wire(and1.get_out(), or_g.get_in(0), x_mid=x_bus, stroke_width=stroke),
        #
        #     # AND2 -> OR
        #     # Line(and2.get_out(), or_g.get_in(1)).set_stroke(width=stroke),
        # manhattan_wire(and2.get_out(), or_g.get_in(1), x_mid=x_bus, stroke_width=stroke),
        # )
        #
        # self.add(and1, and2, or_g, wires)
        # ckt = circuit_two_ands_into_or(
        #     and1_leads=(r"A", r"\overline{B}"),  # bar on top
        #     and2_leads=(r"A", r"B"),
        #     out_label=r"F"
        # )
        # ckt = NotGate()

        self.add(ckt)
        self.wait(2)


class FontTest(Scene):
    def construct(self):
        fonts = ["Avenir Next", "Helvetica Neue", "Palatino", "Georgia", "Hoefler Text", "Apple Chancery"]
        v = VGroup(*[Text(f"{f}: K-map Key points", font=f, font_size=36) for f in fonts]).arrange(DOWN, aligned_edge=LEFT)
        self.add(v)
