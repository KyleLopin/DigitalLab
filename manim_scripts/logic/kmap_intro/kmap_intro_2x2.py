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

# HERE = Path(__file__).resolve().parent
# if str(HERE) not in sys.path:
#     sys.path.insert(0, str(HERE))
MANIM_SCRIPTS_DIR = Path(__file__).resolve().parents[2]  # .../manim_scripts
sys.path.insert(0, str(MANIM_SCRIPTS_DIR))


# local files
import context
from helpers.anim_helpers import pulse
from elements.TruthTable import TruthTable
from elements.KMaps import KarnaughMap
from gates.gates import *
# There will be a slide with main points that gets built up
# during video, it is stored in IntermissionSlides
from helpers.base import IntermissionSlides, KMapBase  # is a Scene with watermark
from helpers.timing_helpers import TimingHelpers
from helpers.styles import KMAP_STYLE as S
# get start elements
from kmap_intros import build_handoff

numbers_font = "Menlo"
# text_font = "Felix Titling"
text_font = "Monaco"
fancy_font = "Noteworthy"
header1_size = 38
header2_size = 32
IMPLICANT_A_COLOR = RED
IMPLICANT_AB_COLOR = GREEN
IMPLICANT_BNOT_COLOR = GREEN

PRODUCTION = True
SET_CUE = False

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


TIMES = {"KMap": [41, 45, 48.5, 56],
         "move_minterms": [71, 72, 76.3, 77.5, 83, 92, 96, 102],
         "explain_implicants": [121, 125, 131.5, 132.5, 145, 146,
                                149, 152, 162],

         "intermissions": [177, 263, 309, 383, 458, 522],
         "intermission ends": [200, 277, 321, 398, 466, 541],

         "example 2": [210, 215, 244, 244, 244, 253,
                       282, 290, 294, 339, 344,
                       350, 353, 373, 373],
         "simplify 1": [94, 96, 98, 101],

         "example 3": [405, 414, 417, 428, 432, 439, 442, 475,
                       480, 483, 485, 492, 512],
         "end": [518, 545],
         }

TEXT_SCALE = 32
PULSE_SCALE = 1.5
EQ_FONTSIZE = 64

KMAP_POINTS = [  # used for IntermissionsSlide
    "Rule 1)|Each implicant becomes an AND term",
    "Rule 2)|The final Boolean function is the OR of all required implicants\n(Sum-of-Products, SOP)",
    "Rule 3)|Implicant sizes can be powers of 2, e.g.:\n1×1, 1×2, 2×1, 2×2, 2×4, 4×2, 4×4, etc.",
    "Rule 4)|Prime implicants are the largest possible valid implicants",
    "Rule 5)|A single 1 can be grouped into multiple implicants",
]


class KMap2VarInstruct(KMapBase, TimingHelpers):
    def construct(self):
        # region setup
        self.next_section("setup")
        if not PRODUCTION:
            self.next_section(skip_animations=True)
        wm = self.add_watermark()
        self.setup()
        # add audio
        self.add_sound(
            "media/audio/KMap_2Var_instruct.wav",
            time_offset=0,
        )
        Text.set_default(font="Menlo")  # for KMaps to work properly

        # Set up the intermission slides
        # inter_title = Text("Karnaugh Maps Rules:", font_size=48, weight=BOLD)
        intermission = IntermissionSlides(title = "Karnaugh Maps Rules:",
                                          bullets=KMAP_POINTS,
                                          exclude=[wm],)
        # attach times
        self.attach_times(TIMES)

        parts_label, example_label = build_handoff(2, 1)
        self.add(parts_label, example_label)
        # endregion setup

        # Intro is in seperate video, this starts at the example phase

        # region truth table
        self.next_section("truth table")
        truth_table = TruthTable(inputs=["A", "B"],
            outputs=["x"], minterms=[2], scale=3)

        self.play(truth_table.write_all(), run_time=5)

        # endregion truth table
        self.next_section("kmap")
        # region kmap

        kmap_2x2_1 = KarnaughMap(num_vars=2,
                                 var_names=["A", "B"],
                                 stroke_width=4)
        kmap_2x2_1.shift(LEFT*1.9).scale(1.5)
        # self.play(kmap_2x2_1.write_all(run_time=2.0))

        self.wait_to("KMap", 0)
        self.play(
            truth_table.animate.scale(0.7).to_corner(UR, buff=1.0).shift(0.3 * UP),
            run_time=1.0
        )
        self.wait_to("KMap", 1)
        self.play(FadeIn(kmap_2x2_1.cells_group))


        # draw kmaps A and B to link
        self.wait_to("KMap", 2)
        self.play(kmap_2x2_1.write("vars"), run_time=2)


        # draw kmaps A and B to link
        self.wait_to("KMap", 3)
        self.play(kmap_2x2_1.write("labels"), run_time=2)

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

        self.next_section("map")
        # region map tt to kmap

        # highlight A 0 on truth table then K-Map
        # first time running, so figure out the loop later
        items = get_var_digits("A", 0, (0, 0))
        anims = [pulse(m, scale=1.5, run_time=0.8) for m in items]
        kmap_a0_anims = anims[2:]
        self.wait_to("move_minterms", 0)
        for m in items:
            m.set_color(BLUE)
        self.play(*anims)

        # highlight A 0 on truth table then K-Map
        items = get_var_digits("B", 0, (0, 1))
        anims = [pulse(m, scale=1.5, run_time=0.8) for m in items]
        for m in items:
            m.set_color(YELLOW)
        kmap_b0_anims = anims[2:]
        self.wait_to("move_minterms", 1)
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
        self.wait_to("move_minterms", 2)
        self.play(*kmap_a0_anims)
        self.wait_to("move_minterms", 3)
        self.play(*kmap_b0_anims)
        self.play(tt_cell_copy.animate.move_to(k_map_cell_min0.get_center()),
                  run_time=3)

        ab_states = [(0, 0), (0, 1), (1, 0), (1, 1)]
        minterm_colors = [ORANGE, TEAL_B, PURPLE, GREEN_C]
        kmap_values = {}
        kmap_values[0] = tt_cell_copy
        keepers = []
        for i in range(1, 4):
            self.wait_to("move_minterms", i+3)
            state_a, state_b = ab_states[i]
            items = get_var_digits("A", state_a, (i, 0))
            anims = [pulse(m, scale=1.5, run_time=1) for m in items]
            for m in items:
                m.set_color(BLUE)
            # self.play(a_a0_tt.animate.scale(2))
            self.play(*anims)
            keepers = anims[2:].copy()

            # highlight A 0 on truth table then K-Map

            items = get_var_digits("B", state_b, (i, 1))
            anims = [pulse(m, scale=1.5, run_time=1) for m in items]
            for m in items:
                m.set_color(YELLOW)
            # self.play(a_a0_tt.animate.scale(2))
            self.play(*anims)
            keepers.extend(anims[2:].copy())
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
        self.wait_to("move_minterms", 7)
        self.play(*keepers[:2])
        self.play(*keepers[2:])
        # endregion map tt to kmap
        self.next_section("implicants_1")
        # region implicants 1

        # Make implicant / prime implicant
        implicant1 = kmap_2x2_1.highlight_group([2], color=IMPLICANT_A_COLOR,
                                               stroke_width=8, buff=-.2)

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
        imp1_grp = VGroup(implicant1, implicant1_label, connector)
        self.wait_to("explain_implicants", 0)
        self.play(FadeIn(implicant1), run_time=2)

        self.wait_to("explain_implicants", 0)
        self.play(
            Write(implicant1_label[0]),
            Create(connector),
            run_time=1.2
        )


        # pulse A is 1 show A
        # looks dumb but its easier to not be DRY sometimes
        ab_state = (1, 0)
        items = get_kmap_var_digit("A", ab_state[0])
        anims = [pulse(m, scale=1.5, run_time=0.8) for m in items]
        implicant1_label[1].set_color(BLUE)
        anims.append(Write(implicant1_label[1], run_time=2))
        self.wait_to("explain_implicants", 2)
        self.play(*anims)

        items = get_kmap_var_digit("B", ab_state[1])
        anims = [pulse(m, scale=1.5, run_time=0.8) for m in items]
        implicant1_label[3].set_color(YELLOW)
        anims.append(Write(implicant1_label[2], run_time=2))
        anims.append(Write(implicant1_label[3], run_time=2))
        self.wait_to("explain_implicants", 3)
        self.play(*anims)

        self.explain_implicant = MathTex("1", "\\cdot", r"\overline{0}", font_size=54)
        self.explain_implicant.scale(
            implicant1_label.get_height() / self.explain_implicant.get_height())
        self.explain_implicant.next_to(implicant1_label, DOWN, buff=0.2)
        self.explain_implicant.align_to(implicant1_label, RIGHT).shift(0.06*LEFT)
        self.wait_to("explain_implicants", 4)
        self.play(self.explain_implicant[0].animate.set_color(BLUE),
                  Write(self.explain_implicant[1]))
        self.wait_to("explain_implicants", 5)
        self.play(self.explain_implicant[2].animate.set_color(YELLOW))

        # explain 10' is 1*1
        explain_implicant2 = MathTex("1", "\\cdot", "1",
                                     font_size=54, tex_template=mono)
        explain_implicant2[0].set_color(BLUE)
        explain_implicant2[2].set_color(YELLOW)
        explain_implicant2.scale( 0.85 *  # this is only one with not overhead bar so shrink
            implicant1_label.get_height() / explain_implicant2.get_height())
        explain_implicant2.next_to(self.explain_implicant, DOWN, buff=0.2)
        explain_implicant2.align_to(implicant1_label, RIGHT).shift(0.06*LEFT)

        self.wait_to("explain_implicants", 6)
        self.play(Write(explain_implicant2[0]))
        self.play(Write(explain_implicant2[1]))
        self.play(Write(explain_implicant2[2]))

        explain_implicant3 = MathTex("=1", font_size=54, tex_template=mono)
        explain_implicant3.scale(0.85 *  # this is only one with not overhead bar so shrink
                                 implicant1_label.get_height() / explain_implicant3.get_height())
        explain_implicant3.next_to(explain_implicant2, DOWN, buff=0.2)
        explain_implicant3.align_to(implicant1_label, RIGHT).shift(0.06 * LEFT)
        self.wait_to("explain_implicants", 7)
        self.play(Write(explain_implicant3))

        # show the ab' AND gate circuit
        ab_circuit = AndGate(leads=(r"A", r"\overline{B}"), output_label="x").scale(0.7)
        ab_circuit.shift(2.3*RIGHT + 0.8*DOWN)

        self.wait_to("explain_implicants", 8)
        self.play(Write(ab_circuit),
                  truth_table.animate.scale(0.75).to_corner(UR, buff=0.6),
                  run_time=2)

        # region show slide pt1
        self.wait_to("intermissions", 0)
        intermission.show(self, wait_to="intermission ends")  # index: 0
        # endregion show slide pt1

        # self.wait_to("implicant ab 1 end")
        self.play(FadeOut(ab_circuit, implicant1_label,
                          connector, self.explain_implicant, explain_implicant2,
                          explain_implicant3), run_time=1)
        # endregion implicants 1
        self.next_section("implicant_2")
        # region implicant 2
        # region add minterm

        # change the maxTerm3 to minTerm3 on the KMap and truth table
        tt_cell_min3 = truth_table.get_cell(row=3, col=2)
        anims = []

        for txt in [tt_cell_min3, kmap_values[3]]:
            new_txt = Text("1", font=numbers_font, font_size=txt.font_size)
            new_txt.move_to(txt).match_style(txt)
            anims.append(Transform(txt, new_txt))
        example_label2 = Text(f"Example 2", font_size=26, font=S.text_font
                              ).move_to(example_label)
        anims.append(Transform(example_label, example_label2))
        self.wait_to("example 2", 0)
        self.play(*anims)
        # endregion add minterm
        # region add implicant 2
        # also change example number

        implicant2 = kmap_2x2_1.highlight_group(
            [3], color=IMPLICANT_AB_COLOR,
            stroke_width=8, buff=-.2)
        self.wait_to("example 2", 1)
        self.play(Create(implicant2), run_time=2)
        implicant2_label = MathTex("Implicant: AB",
                                   font_size=54, color=IMPLICANT_AB_COLOR)
        implicant2_label.next_to(implicant2, DOWN, buff=1.4).shift(1.8 * RIGHT)
        connector = Line(
            implicant2_label.get_top(),
            implicant2.get_corner(DR),
            stroke_width=5, color=IMPLICANT_AB_COLOR
        )
        self.play(
            Write(implicant2_label),
            Create(connector), run_time=1.2
        )
        self.wait_to("example 2", 2)
        self.play(FadeOut(implicant2_label, connector))
        imp2_grp = VGroup(implicant2, implicant2_label, connector)
        # endregion add implicant 2
        # explain implicant 2
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
        eq[1].set_color(IMPLICANT_A_COLOR)
        eq[3].set_color(IMPLICANT_AB_COLOR)
        eq.to_edge(UP, buff=1.2).shift(1.0*RIGHT)

        term1 = eq.get_part_by_tex(r"A\overline{B}")
        term2 = eq.get_part_by_tex(r"AB")

        # 2) Connector lines (use always_redraw so they track if you move things later)
        conn_anotb = always_redraw(lambda:
                              Line(term1.get_bottom(), implicant1.get_corner(UR),
                                   stroke_width=4, color=IMPLICANT_A_COLOR)
                              )
        conn_ab = always_redraw(lambda:
                              Line(term2.get_bottom(), implicant2.get_corner(UR),
                                   stroke_width=4, color=IMPLICANT_AB_COLOR)
                              )
        # 3) Animate
        self.wait_to("example 2", 3)
        self.play(Write(eq), run_time=1.2)
        self.play(Create(conn_anotb), Create(conn_ab), run_time=0.6)
        non_prime_txt = Text("Not optimal solution", font_size=38,
                             color=YELLOW_B)
        non_prime_txt.next_to(eq, UP, buff=0.3)
        self.wait_to("example 2", 4)
        self.play(Write(non_prime_txt), run_time=1.2)

        truth_table.save_state()
        ckt_builder = CircuitBuilder(var_order=["A", "B", "C", "D"])
        inputs = [
            [("A", 1), ("B", 0)],
            [("A", 1), ("B", 1)],
        ]
        ckt = ckt_builder.build_sop(inputs, output_label="X")
        # ckt = circuit_two_ands_into_or(
        #     and1_leads=(r"A", r"\overline{B}"),  # bar on top
        #     and2_leads=(r"A", r"B"),
        #     out_label=r"X"
        # )
        ckt.scale(0.7)
        ckt.shift(2.5*RIGHT + 2.7*DOWN)
        ckt.gates[0].set_color(IMPLICANT_A_COLOR)
        ckt.gates[1].set_color(IMPLICANT_AB_COLOR)
        ckt.wires[0].set_color(IMPLICANT_A_COLOR)
        ckt.wires[1].set_color(IMPLICANT_AB_COLOR)

        self.wait_to("example 2", 5)
        self.play(Create(ckt),
                  # truth_table.animate.scale(0.75).to_corner(UR, buff=0.6),
                  run_time=2)

        self.wait_to("intermissions", 1)
        intermission.show(self, wait_to="intermission ends")  # index: 1
        # add the implicants can be any size but prime impicants can not be expanded

        # MOVED: do implicant expansion first
        prime_implicant1 = kmap_2x2_1.highlight_group(
            [2, 3], color=IMPLICANT_A_COLOR, stroke_width=8, buff=-.2)
        self.wait_to("example 2", 6)
        self.play(
            ReplacementTransform(implicant1.copy(), prime_implicant1),
            FadeOut(implicant2, implicant1),
            FadeOut(eq),
            FadeOut(ckt, conn_anotb, conn_ab, non_prime_txt),
            run_time=1.4
        )


        # First simplified equation
        eq1 = MathTex(
            r"X = A\left(B + \overline{B}\right)",
            font_size=EQ_FONTSIZE
        )
        eq1.next_to(eq, DOWN, buff=-0.6)

        # Final simplified equation
        eq2 = MathTex(
            "X = A\\cdot 1",
            font_size=EQ_FONTSIZE
        )

        expand_imp = Paragraph(
            "Implicants can be expanded.",
            "Adjacent squares differ",
            "by only 1 variable",
            font_size=28,
            color=LIGHTER_GRAY,
            line_spacing=0.8,  # increase this
            alignment="left",
        )
        expand_imp.shift(3.3*RIGHT)
        power_text = Paragraph(
            "Implicants are groups with",
            "sizes of powers of 2:",
            "i.e. 1, 2, 4, etc.",
            font_size=28,
            color=LIGHTER_GRAY,
            line_spacing=0.8,  # increase this
            alignment="left",
        )
        power_text.next_to(expand_imp, DOWN, buff=0.4)
        self.wait_to("example 2", 7)
        self.play(
            FadeOut(truth_table),
            Write(expand_imp), run_time=1.2)
        self.wait_to("example 2", 8)
        self.play(Write(power_text), run_time=1.2)

        # Final simplified equation
        eq3 = MathTex(r"X = A", font_size=EQ_FONTSIZE,
                      color=IMPLICANT_A_COLOR)
        eq3.next_to(eq, DOWN, buff=0.6).shift(0.3*RIGHT)
        eq2.next_to(eq1, DOWN, buff=-0.6)
        eq2.align_to(eq1, RIGHT)

        connector = Line(
            prime_implicant1.get_right(),
            eq3.get_corner(DL),
            stroke_width=5, color=IMPLICANT_A_COLOR
        )
        self.wait_to("intermissions", 2)
        intermission.show(self, wait_to="intermission ends")  # index: 2

        # Animate
        self.wait_to("example 2", 9)
        self.play(FadeOut(expand_imp),
                  FadeOut(power_text),
                  FadeIn(truth_table), run_time=1.0)
        self.play(Write(eq3), run_time=1)
        self.play(Create(connector), run_time=1.0)


        prime_implicant1_label = (Tex(r"\text{Prime Implicant}",
                                      font_size=EQ_FONTSIZE, color=IMPLICANT_A_COLOR)
                                  .next_to(prime_implicant1, RIGHT, buff=0.35)
                                  .shift(0.6 * DOWN))
        self.wait_to("example 2", 10)
        self.play(Write(prime_implicant1_label))


        # self.wait_to("simplify 1", 0)
        # self.play(eq.animate.shift(0.8 * UP),
        #           Write(eq1),
        #           run_time=1.0)
        # self.wait_to("simplify 1", 1)
        # self.play(Write(eq2), run_time=1)

        # self.wait_to("pulse ab")
        # t1 = eq.get_part_by_tex(r"A\overline{B}")
        # t2 = eq.get_part_by_tex(r"AB")
        #
        # self.play(Indicate(t1))
        # self.wait_to("pulse ab")
        # self.play(Indicate(t2))
        # self.wait_to("pulse x=a1")
        # self.play(Indicate(eq2))
        #
        # self.wait_to("pulse x=a")
        # self.play(Indicate(eq3), run_time=1)
        self.wait_to("example 2", 11)
        implicant1.set_color(WHITE)
        implicant1_label.set_color(WHITE)
        self.play(
            Succession(
                FadeIn(imp1_grp, run_time=0.5),
                Wait(0.4),
                FadeOut(imp1_grp, run_time=0.5),
            )
        )

        self.wait_to("example 2", 12)
        self.play(
            Succession(
                FadeIn(imp2_grp, run_time=0.5),
                Wait(0.4),
                FadeOut(imp2_grp, run_time=0.5),
            )
        )

        # A Prime implicant is the largest implicant that can be formed by grouping 1's together
        # As the implicant size is 1 column, and 2 rows, it spans B is 0 and B is 1
        # Pulse B=0 then B=1 (digits + restore each time)
        self.wait_to("example 2", 13)
        pulse0, restore0 = kmap_2x2_1.pulse_var_digits("B", 0, color=YELLOW, scale_factor=1.4, run_time=0.25)
        self.play(pulse0)
        self.play(Restore(restore0), run_time=0.5)

        self.wait_to("example 2", 14)
        pulse1, restore1 = kmap_2x2_1.pulse_var_digits("B", 1, color=YELLOW, scale_factor=1.4, run_time=0.25)
        self.play(pulse1)
        self.play(Restore(restore1), run_time=0.5)

        self.wait_to("intermissions", 3)
        intermission.show(self, wait_to="intermission ends")  # index: 3

        # remove all the prime implicant 1 stuff
        self.play(FadeOut(prime_implicant1_label, eq3, connector), run_time=1)
        # endregion implicant 2
        self.next_section("implicant_3")
        # region implcant 3
        # convert M0 to m0
        # change the maxTerm3 to minTerm3 on the KMap and truth table
        tt_cell_min0 = truth_table.get_cell(row=0, col=2)
        anims = []

        for txt in [tt_cell_min0, kmap_values[0]]:
            new_txt = Text("1", font=numbers_font, font_size=txt.font_size)
            new_txt.move_to(txt).match_style(txt)
            anims.append(Transform(txt, new_txt))
        example_label3 = Text(f"Example 3", font_size=26, font=S.text_font
                              ).move_to(example_label2)

        self.wait_to("example 3", 0)
        self.play(*anims,
                  Transform(example_label, example_label3),
                  run_time=1.5)

        implicant3 = kmap_2x2_1.highlight_group([0], color=IMPLICANT_BNOT_COLOR,
                                                stroke_width=8, buff=-.2)
        self.wait_to("example 3", 1)
        self.play(Create(implicant3), run_time=2)

        implicant3_label = MathTex(r"Implicant: \overline{A}\,\overline{B}",
                                   font_size=54, color=IMPLICANT_BNOT_COLOR)
        implicant3_label.next_to(implicant3, UP, buff=1.1).shift(1.9 * LEFT)

        connector = Line(
            implicant3_label.get_bottom(),
            implicant3.get_corner(UL),
            stroke_width=5, color=IMPLICANT_BNOT_COLOR,
        )
        self.wait_to("example 3", 2)
        self.play(
            Write(implicant3_label),
            Create(connector),
            run_time=1.2
        )

        # make scene to explain implicant a'b' to b'
        prime_implicant2 = kmap_2x2_1.highlight_group([0, 2], color=IMPLICANT_BNOT_COLOR,
                                                      stroke_width=8, buff=-.2)
        prime_implicant2_label = MathTex(r"\text{Prime Implicant:} \overline{B}",
                                         font_size=54, color=IMPLICANT_BNOT_COLOR)
        prime_implicant2_label.move_to(implicant3_label)

        # bring back later when explaining implicant expansion
        implicant3.save_state()
        implicant3_label.save_state()

        # region explain implicant shapes
        # Can not make L shape
        l_group = kmap_2x2_1.outline_cells([0, 2, 3], color=MAROON_C,
                                           stroke_width=8, buff=-.2)
        # self.play(Write(l_group), run_time=1)
        prime_implicant1.save_state()
        self.wait_to("example 3", 3)
        self.play(Transform(prime_implicant1, l_group), run_time=2)


        l_shape_label1 = Text("Invalid implicant shape",
                              font_size=32, color=MAROON_C)
        l_shape_label2 = Text("No Boolean AND Term",
                              font_size=32, color=MAROON_C)
        l_shape_label1.next_to(prime_implicant1, UP, buff=1.9).shift(3.0 * RIGHT)
        l_shape_label2.next_to(l_shape_label1, DOWN, buff=.1)
        conn_l = Line(l_group.get_corner(UR), l_shape_label2.get_bottom(),
                      stroke_width=8, color=MAROON_C, buff=0.1,)
        self.wait_to("example 3", 4)
        self.play(Write(l_shape_label1),
                  Write(l_shape_label2),
                  Write(conn_l), run_time=1)

        self.wait_to("example 3", 5)
        self.play(Restore(prime_implicant1),
                  FadeOut(l_shape_label1, l_shape_label2, conn_l),)
        # Can not expand implicant to 2x2


        # endregion explain implicant shapes
        self.wait_to("example 3", 6)
        self.play(Transform(implicant3, prime_implicant2),
                  # FadeOut(implicant3_label, connector),
                  Transform(implicant3_label, prime_implicant2_label),
                  run_time=1)

        self.wait_to("intermissions", 4)
        intermission.show(self, wait_to="intermission ends")   # index: 4

        # explain you can do this because you can expand across
        # 1 variable, for b' you expand across A because A can
        # be 0 or 1
        # B = 0
        self.wait_to("example 3", 7)
        pulse_, digits = kmap_2x2_1.pulse_var_digits("B", 0, color=YELLOW, scale_factor=1.4, run_time=0.25)
        self.play(pulse_)
        self.play(Restore(digits), run_time=0.15)

        # A = 0
        pulse0, digits0 = kmap_2x2_1.pulse_var_digits("A", 0, color=YELLOW, scale_factor=1.4, run_time=0.25)

        # A = 1
        pulse1, digits1 = kmap_2x2_1.pulse_var_digits("A", 1, color=YELLOW, scale_factor=1.4, run_time=0.25)
        self.wait_to("example 3", 8)
        self.play(AnimationGroup(pulse0, pulse1, lag_ratio=0), run_time=0.35)

        self.play(
            AnimationGroup(Restore(digits0), Restore(digits1), lag_ratio=0),
            run_time=0.35
        )


        rule_text = MathTex(
            r"\text{Doubling a dimension of an implicant}\\",
            r"\text{ removes one variable from the equation}",
            font_size=44
        ).shift(2.5*DOWN + RIGHT*0)
        # self.wait_to("example 3", 9)


        # explain a'b' to b' is removing a

        # Save PRIME state (store it as another snapshot)
        prime_state_box = implicant3.copy()
        prime_state_lbl = implicant3_label.copy()

        self.wait_to("example 3", 10)
        self.play(Restore(implicant3),
                  Restore(implicant3_label), run_time=2)
        self.play(Write(rule_text))
        # Forward to PRIME again
        self.wait_to("example 3", 11)
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
                                         font_size=54, color=IMPLICANT_A_COLOR)
        prime_implicant1_label.shift(2.2*RIGHT+1.2*DOWN)

        connector = Line(
            prime_implicant1_label.get_left(),
            prime_implicant1.get_right(),
            stroke_width=5, color=IMPLICANT_A_COLOR, buff=0.1,
        )
        self.wait_to("example 3", 12)
        self.play(Write(prime_implicant1_label), Write(connector) )
        # endregion implcant 3

        # region end
        final_eqn = MathTex(
            r"X = A + \overline{B}",
            substrings_to_isolate=[r"A", r"\overline{B}"],
            font_size=EQ_FONTSIZE
        )
        final_eqn[1].set_color(IMPLICANT_A_COLOR)
        final_eqn[3].set_color(IMPLICANT_BNOT_COLOR)
        final_eqn.next_to(prime_implicant1_label, UP, buff=0.4)
        self.wait_to("end", 0)
        self.play(Create(final_eqn), run_time=1)

        self.wait_to("intermissions", 5)
        intermission.highlight(self, 1, wait_to="intermission ends")

        ckt = OrGate(leads=[r"\overline{B}", "A"], output_label="X")
        # labels are reversed
        ckt.input_labels[0].set_color(IMPLICANT_BNOT_COLOR)
        ckt.input_labels[1].set_color(IMPLICANT_A_COLOR)
        ckt.input_leads[0].set_color(IMPLICANT_BNOT_COLOR)
        ckt.input_leads[1].set_color(IMPLICANT_A_COLOR)

        print("99: ", ckt.input_labels)
        ckt.next_to(final_eqn, UP, buff=0.4).scale(1.5)
        self.wait_to("end", 1)
        self.play(Create(ckt), run_time=1)
        # endregion end
        self.wait(2)



class KMap2VarConclusion(KMapBase, TimingHelpers):
    # --- TUNING KNOBS ---
    TITLE_FONT = "Avenir Next"
    BODY_FONT = "Palatino"

    TITLE_SIZE = 50
    LABEL_SIZE = 38  # "1)" / "2)" / "3)"
    BODY_SIZE = 36  # main text
    WM_SIZE = 24

    ITEM_BUFF = 0.45  # vertical spacing between points
    TITLE_BUFF = 0.60  # spacing between title and list
    SLIDE_BUFF = 0.8  # spacing to top of screen
    WIDTH_FRAC = 0.92  # fraction of frame width for slide

    COVER_FRAC = 0.90  # top % of screen to black out
    LINE_SPACING = 0.9
    times = {"write time": 3,
             "fade out": 2}

    @staticmethod
    def make_hanging_item(
            s: str,
            *,
            sep: str = "|",
            font: str = "Avenir Next",
            label_size: int = 36,
            body_size: int = 36,
            label_buff: float = 0.25,
            line_spacing: float = 0.9,
    ) -> Mobject:
        """Build a single 'LABEL|BODY' item with hanging indent for BODY newlines."""
        if sep in s:
            label_txt, body_txt = s.split(sep, 1)
            label_txt = label_txt.strip()
            body_txt = body_txt.strip()

            label = Text(label_txt, font=font, font_size=label_size, weight="BOLD")
            body = Text(body_txt, font=font, font_size=body_size, line_spacing=line_spacing)

            item = VGroup(label, body).arrange(RIGHT, buff=label_buff, aligned_edge=UP)
            return item

        return Text(s, font=font, font_size=body_size, line_spacing=line_spacing)

    def construct(self):
        wm = self.add_watermark()

        # --- Slide content (your 3 teaching points) ---
        TITLE_FONT = "Avenir Next"
        TEXT_FONT = "Palatino"  # try "Palatino", "Georgia", "Hoefler Text", etc.

        bullet = "• "
        points = [
            f"{bullet}|Implicants are rectangular groups of 1’s.\n"
            "Groups must be sizes of 2ⁿ (powers of two), e.g. 1×1, 1×2, 2×1, 2×2, 2x4, etc.",
            f"{bullet}|Prime implicants are the largest valid groups.\n"
            "Larger groups eliminate more variables → simpler equations and smaller circuits",
            f"{bullet}|Each group becomes an AND term.\n"
            "The final function is the OR of all required implicants (Sum-of-Products, SOP)",
        ]

        title = Text("Key points for Karnaugh Maps (Part 1)", font=TITLE_FONT,
                     font_size=self.TITLE_SIZE, weight="BOLD")

        items = VGroup(*[
            self.make_hanging_item(
                p,
                sep="|",
                font=TEXT_FONT,
                label_size=self.LABEL_SIZE,
                body_size=self.BODY_SIZE,
            )
            for p in points
        ]).arrange(DOWN, aligned_edge=LEFT, buff=self.ITEM_BUFF)

        # Hanging indent alignment: align all bodies to the same left x
        bodies = VGroup(*[
            it[1] for it in items
            if isinstance(it, VGroup) and len(it) >= 2
        ])
        if len(bodies) > 0:
            target_left_x = bodies[0].get_left()[0]
            for b in bodies:
                b.shift(RIGHT * (target_left_x - b.get_left()[0]))

        slide = VGroup(title, items).arrange(DOWN, buff=0.6, aligned_edge=LEFT)
        slide.set_width(config.frame_width * self.WIDTH_FRAC)
        slide.to_edge(UP, buff=self.SLIDE_BUFF)
        slide.set_z_index(1001)

        # Hide all bullet items initially (title stays)
        for it in items:
            it.set_opacity(0)

        # --- Cover only top 90% so watermark area stays visible ---
        cover = Rectangle(
            width=config.frame_width,
            height=0.90 * config.frame_height,
        ).set_fill(BLACK, 1).set_stroke(width=0)
        cover.to_edge(UP, buff=0)
        cover.set_z_index(1000)

        # Keep watermark above the cover (optional). If you prefer it under, remove these 2 lines.
        wm.set_z_index(1100)

        # --- Animate ---
        self.add(cover, slide)

        self.play(FadeIn(title), run_time=self.times["write time"])

        for it in items:
            it.set_opacity(1)
            self.play(Write(it), run_time=self.times["write time"])
            self.wait(0.4)

        self.wait(1.5)
        return
        self.play(FadeOut(slide), run_time=self.times["fade out"])
        self.remove(cover, slide)
        self.wait(0.5)


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
