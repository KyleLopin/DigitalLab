# Copyright (c) 2025 Kyle Lopin (Naresuan University) <kylelopin@gmail.com>

"""
Make a Manim scene introducing how a 2 column x 4 row Karnaugh Map works.
"""

__author__ = "Kyle Vitautas Lopin"

# standard libraries
import sys
from pathlib import Path

from typing_extensions import runtime

MANIM_SCRIPTS_DIR = Path(__file__).resolve().parents[2]  # .../manim_scripts
sys.path.insert(0, str(MANIM_SCRIPTS_DIR))
# installed libraries
from manim import *
from manim_studio import LiveScene

from manim import TexTemplate

tpl = TexTemplate()
tpl.add_to_preamble(r"\usepackage{amsmath}")  # for aligned + \text

# local files
from logic.gates.gates import *

from helpers.anim_helpers import pulse
from helpers.base import IntermissionSlides, KMapBase  # is a Scene with watermark
from helpers.timing_helpers import TimingHelpers
# get start elements
from kmap_intros import build_handoff
from logic.elements.TruthTable import TruthTable
from logic.elements.KMaps import KarnaughMap
import style_config as s

TIMES = {"finish tt": 2,
         "Add KMap": [4, 6],
         "Add gray code": [8, 10, 12, 14, 16],
         "intermissions": [20, 80],
         "intermission ends": [24, 84],

         "Highlight gray code": [18, 20, 22, 24, 26],
         "Start mapping": [28, 30, 32, 34, 36, 38, 40, 42],
         "implicant 1": [50, 52, 54, 56, 58, 60, 62, 64, 66],
         "implicant ac'": [70, 72, 74, 76, 78, 80, 82, 84, 86],
         "implicant ab": [85, 90, 92, 95, 97, 100, 102, 104, 106, 108],
         "implicant b": [110, 112, 114, 116, 118, 120],
         "implicant a": [125, 130, 132, 134, 136, 138],
}
PRODUCTION = True

IMPLICANT_FONT_SIZE = 48
IMPLICANT_ACNOT_COLOR = RED_B

INVALID_IMPLICANT_COLOR = PURE_RED
IMPLICANT_AB_COLOR = BLUE
IMPLICANT_ANOTB_COLOR = TEAL_C
FALSE_IMPLICANT_COLOR = YELLOW_C
IMPLICANT_BUFF = 0.8

intermssion_pts = [  # used for IntermissionsSlide
    "Point 1)|Use Gray code ordering so adjacent cells differ\nby only 1 variable",
    "Point 2)|Karnaugh map edges are adjacent (wrap-around)",
]

# intermissin_points = [
#     "Rule 1)|Implicant terms are ANDed together",
#     "Rule 2)|The final output are the implicants ORed",
#     "Rule 3)|Chose prime implicants of the largest allowed sizes (2^nx2^m)",
#     "Rule 4)|Use Grey Code for labels",
#     "Rule 5)|Implicants can wrap around the edges of Karnaugh Maps",
# ]

def running_in_studio() -> bool:
    argv = " ".join(sys.argv).lower()
    return "manim-studio" in argv or "manim_studio" in argv

_Base = (LiveScene, KMapBase, TimingHelpers) if running_in_studio() else (KMapBase, TimingHelpers)


def flip_maxterm_to_minterm(term: Text, tt_term: Text):
    new_term = Text("1", font=s.numbers_font, font_size=term.font_size)
    new_term.move_to(term).match_style(term)
    # change font size
    new_tt_term = Text("1", font=s.numbers_font, font_size=term.font_size*0.7+1)
    new_tt_term.move_to(tt_term).match_style(tt_term)
    return Transform(term, new_term), Transform(tt_term, new_tt_term)


class KMap3VarInstruct(*_Base):
    def construct(self):
        # region setup
        self.next_section("setup")
        if not PRODUCTION:
            self.next_section(skip_animations=True)
        self.setup()  # for Manim?
        Text.set_default(font="Menlo")  # for KMaps graycode numbers to look proper
        wm = self.add_watermark()

        intermission_slide = IntermissionSlides(title="Karnaugh Maps Points:",
                                                bullets=intermssion_pts,
                                                exclude=[wm])
        # attach times
        self.attach_times(TIMES)
        # initialize the upper level example numbers that were loaded during previous video
        # so that this has to be there at the start of voice over
        parts_label, example_label = build_handoff(3, 4)
        self.add(parts_label, example_label)

        implicant_label = MathTex(r"\text{Implicant:}", tex_template=tpl,
                                  font_size=IMPLICANT_FONT_SIZE, color=IMPLICANT_ACNOT_COLOR)
        prime_imp_label = MathTex(r"\text{Prime Implicant:}", tex_template=tpl,
                                  font_size=IMPLICANT_FONT_SIZE, color=IMPLICANT_ACNOT_COLOR)

        # endregion setup

        # region truth table
        truth_table = TruthTable(inputs=["A", "B", "C"],
                                 outputs=["X"], minterms=[4], scale=1.8)
        self.play(truth_table.write_all(run_time=3))
        self.wait_to("finish tt")
        self.play(
            truth_table.animate.scale(0.7).to_corner(UR, buff=1.0).shift(0.3 * UP),
            run_time=1.0
        )
        # endregion truth table

        # region KMap
        # region KMap init
        kmap = KarnaughMap(num_vars=3, var_names=["A", "B", "C"],
                           stroke_width=4)
        kmap.shift(LEFT * 1.7).scale(1.2)
        self.play(Create(kmap.cells_group), run_time=1)
        self.wait_to("Add KMap", 0)

        # draw kmaps A, B and C to link
        self.play(kmap.write("vars"), run_time=2)
        self.wait_to("Add KMap", 1)

        # draw kmap row and column labels
        gray_code_anims, gray_code_mobjs_group = kmap.write("labels", return_mobjects=True)
        # self.play(kmap.write("labels"), run_time=2)
        print("gray_code_anims", gray_code_anims)
        print("gray_code_mobjs", gray_code_mobjs_group)
        # manually go in and get grey codes
        a_labels = gray_code_mobjs_group[1]
        gray_code_mobjs = gray_code_mobjs_group[0]
        self.play(Write(a_labels))
        self.wait_to("Add gray code", 0)
        # gray_code_mobjs has structure of 4 rows of 2 columns for the gray code on columns
        for mobj in gray_code_mobjs:
            print("mobj", mobj)
        for i, gray_code in enumerate(gray_code_mobjs):
            self.play(FadeIn(gray_code), run_time=2)
            self.wait_to("Add gray code", i+1)
        # highlight how the adjacent squares differ by only 1 variable
        # the animation sequence will be to highlight the same, then pulse the different
        # ones to go with the script.
        round = 0  # for timing
        # get B and C to highlight and restore
        b = kmap.get_var_label("B")
        c = kmap.get_var_label("C")
        b.save_state()
        c.save_state()
        sides = [b, c]  # store here to index with col index

        for current_row in range(4):
            next_row = (current_row + 1) % 4  # wrap around the map
            same_col = current_row % 2  # what column stays the same
            next_col = (current_row+1) % 2  # what column changes a variable
            # the coordinates of the numbers that stay the same between columns
            same_side1, same_side2 = gray_code_mobjs[current_row][same_col], gray_code_mobjs[next_row][same_col]
            # and numbers that differ by 1
            adj1, adj2 = gray_code_mobjs[current_row][next_col], gray_code_mobjs[next_row][next_col]
            self.play(Indicate(same_side1, scale_factor=1.4, color=YELLOW),
                      Indicate(same_side2, scale_factor=1.4, color=YELLOW),
                      Indicate(sides[same_col], scale_factor=1.4, color=YELLOW),
                      run_time=1)

            # scale sides[next_col] and change to red
            self.play(
                sides[next_col].animate.scale(1.15).set_color(RED),
                run_time=0.15
            )
            self.play(Indicate(adj1, scale_factor=1.4, color=RED),
                      run_time=0.5)
            self.play(Indicate(adj2, scale_factor=1.4, color=RED), run_time=0.5)
            self.play(Restore(sides[next_col]), run_time=0.25)
            # restore sides[next_col]
            self.wait_to("Highlight gray code", current_row)

        # endregion KMap init

        intermission_slide.show(self, wait_to="intermission ends")  # index: 0

        # region KMap map from truth table
        # for the data in the KMap get from Truth Table and make a copy and save in:
        kmap_terms = []
        kmap_terms_colors = [GREEN_B, GREEN_C, GREEN_D, TEAL_E,
                             PURPLE_B, PURPLE_C, PURPLE_D, MAROON_E]
        for i in range(8):
            self.wait_to("Start mapping", i)
            # region indicate combination
            # show which input combination (a, bc) the term is in
            abc = f"{i:0{3}b}"
            a, bc = abc[2], abc[0:2]
            # print(f"bin = {abc}, a = {a}, bc={bc}")
            # show A and its value
            a_items = []
            a_items.append(truth_table.get_label("A"))
            a_items.append(truth_table.get_cell(row=i, col=0))
            a_items.append(kmap.get_var_label("A"))

            a_bit = i // 4
            a_items.append(kmap.get_var_digits("A", a_bit)) # value is 0 or 1
            anims = [pulse(m, scale=1.5, run_time=0.8)
                     for m in a_items]
            for m in a_items:
                m.set_color(BLUE)
            self.play(*anims)

            bc_items = []
            bc_items.append(truth_table.get_label("B"))
            bc_items.append(truth_table.get_label("C"))
            bc_items.append(truth_table.get_cell(row=i, col=1))
            bc_items.append(truth_table.get_cell(row=i, col=2))

            bc_items.append(kmap.get_var_label("B"))
            bc_items.append(kmap.get_var_label("C"))
            bc_items.append(kmap.get_var_digits("BC", i%4))

            anims = [pulse(m, scale=1.5, run_time=0.8)
                     for m in bc_items]
            for m in bc_items:
                m.set_color(YELLOW)
            self.play(*anims)
            # endregion indicate combination

            # region move tt number to KMap
            # get truth table number
            _term = truth_table.get_cell(row=i, col=3)  # last column [3]
            # change its color and copy it
            _term.set_color(kmap_terms_colors[i])
            term = _term.copy()  # make copy to keep for kmap
            term.set_z_index(10)  # move on top
            self.add(term)  # add copy to frame to move
            kmap_terms.append(term)
            kmap_place, _ = kmap.get_cell_from_minterm(i)
            start = term.get_center()
            end = kmap_place.get_center()

            line = Line(start, end)
            self.play(Create(line), run_time=0.2)
            self.play(term.animate.move_to(end).scale(1.4),
                      FadeOut(line), run_time=1)
            # endregion move tt number to KMap

        # endregion KMap map from truth table
        # endregion truth table and KMap

        # region implicant ab'c'
        implicant_1 = kmap.highlight_group([4], color=IMPLICANT_ACNOT_COLOR,
                                           stroke_width=8, buff=-0.2)

        implicant_1_eqn = MathTex(r"&A\overline{B}\,\overline{C}",
                                    substrings_to_isolate=[r"A", r"\overline{B}", r"\overline{C}"],
                                    tex_template=tpl,
                                    font_size=IMPLICANT_FONT_SIZE,
                                    color=IMPLICANT_ACNOT_COLOR)
        implicant_1_header = implicant_label.copy()
        implicant_1_eqn.next_to(implicant_1_header, DOWN
                                ).align_to(implicant_1_header, LEFT)

        implicant_1_label = VGroup(implicant_label.copy(), implicant_1_eqn)
        implicant_1_label.next_to(implicant_1, RIGHT, buff=IMPLICANT_BUFF)

        self.play(Create(implicant_1), run_time=2)
        self.wait_to("implicant 1", 0)
        # pulse A 1 and BC 00
        a1 = [kmap.get_var_label("A"), kmap.get_var_digits("A", 1)]
        bc_00 = [kmap.get_var_label("B"), kmap.get_var_label("C"),
                 kmap.get_var_digits("BC", "00")]

        # show implicant label
        self.play(Write(implicant_1_label), run_time=1.0)
        self.wait_to("implicant 1", 1)
        # pulse A 1 and BC 00
        # self.play(Indicate(a1), scale_factor=1.4, run_time=1)
        anims = [pulse(m, scale=1.5, run_time=0.8)
                 for m in a1]
        self.play(*anims)
        self.wait_to("implicant 1", 2)
        # self.play(Indicate(bc_00), scale_factor=1.4, run_time=1)
        anims = [pulse(m, scale=1.5, run_time=0.8)
                 for m in bc_00]
        self.play(*anims)
        self.wait_to("implicant 1", 3)

        # make point here that it is a prime implicant
        false_imp_bnotcnot = kmap.highlight_group([0, 4], buff=-0.2,
                                                  stroke_width=s.imp_stroke_width,
                                                  color=FALSE_IMPLICANT_COLOR)
        false_imp_abnot = kmap.highlight_group([5, 4], buff=-0.2,
                                               stroke_width=s.imp_stroke_width,
                                               color=FALSE_IMPLICANT_COLOR)
        implicant_acnot_top = kmap.highlight_group_open_wrap(
            minterms=[4], side="top", color=FALSE_IMPLICANT_COLOR,
            stroke_width=s.imp_stroke_width, buff=-0.2)
        implicant_acnot_bottom = kmap.highlight_group_open_wrap(
            minterms=[6], side="bottom", color=FALSE_IMPLICANT_COLOR,
            stroke_width=s.imp_stroke_width, buff=-0.2)

        self.wait_to("implicant 1", 4)
        self.play(Create(false_imp_abnot), run_time=1.0)

        self.wait_to("implicant 1", 5)
        self.play(Create(false_imp_bnotcnot),
                  FadeOut(false_imp_abnot), run_time=1.0)

        self.wait_to("implicant 1", 6)
        self.play(Create(implicant_acnot_top),
                  Create(implicant_acnot_bottom),
                  FadeOut(false_imp_bnotcnot), run_time=1.0)

        self.wait_to("implicant 1", 7)
        self.play(FadeOut(implicant_acnot_top),
                  FadeOut(implicant_acnot_bottom),
                  run_time=1.0)
        new_prime_label = prime_imp_label.copy().set_color(IMPLICANT_ACNOT_COLOR)
        new_prime_label.move_to(implicant_1_label[0]).shift(0.3*RIGHT)
        self.play(Transform(implicant_1_label[0], new_prime_label))

        # make circuit
        ckt_1 = AndGate(leads=[r"A", r"\overline{B}", r"\overline{C}"],
                        output_label="X")
        ckt_1.scale(0.6)
        ckt_1.next_to(implicant_1_label, DOWN, buff=0.3)
        self.play(Create(ckt_1), run_time=1.0)
        self.wait_to("implicant 1", 8)
        # implicant_1_group = VGroup(ckt_1, implicant_1_label)

        # endregion implicant ab'c'

        # region implicant ac'
        self.wait_to("implicant ac'", 0)
        self.play(FadeOut(ckt_1), run_time=1.0)

        # region flip m6
        # convert truth table and KMap maxTerm 6 to minTerm 6 and change example number
        term_flip, tt_flip = flip_maxterm_to_minterm(kmap_terms[6], truth_table.get_cell(row=6, col=3))
        example_label_new = Text(f"Example 5", font_size=s.ex_lbl_font_size,
                                 font=s.text_font
                                 ).move_to(example_label)
        # change prime implicant to implicant
        revert_imp_label = implicant_label.copy().set_color(IMPLICANT_ACNOT_COLOR)
        revert_imp_label.move_to(implicant_1_label[0]
                                 ).shift(0.3*LEFT)
        # self.play()

        anims = [term_flip, tt_flip, Transform(implicant_1_label[0], revert_imp_label),
                 example_label.animate.become(example_label_new)]

                 # Transform(example_label, example_label_new)]
        self.play(*anims, run_time=1.0)
        # example_label= example_label_new
        # endregion flip m6

        # add implicant abc'
        implicant_m6 = kmap.highlight_group([6], buff=-0.2,
                                            stroke_width=s.imp_stroke_width,
                                            color=BLUE)
        implicant_2_label = MathTex(# r"\begin{aligned}"
                                    r"&\text{Implicant: }\\"
                                    r"&AB\overline{C}",
                                    # r"&A", r"B", r"\overline{C}",
                                    # r"\end{aligned}",
                                    substrings_to_isolate=[r"A", r"B", r"\overline{C}"],
                                    tex_template=tpl,
                                    font_size=IMPLICANT_FONT_SIZE,
                                    color=BLUE)

        print("implicant_1_label: ", implicant_1_label)
        ACbar_top = [implicant_2_label[0], implicant_2_label[2],
                     implicant_1_eqn[0], implicant_1_eqn[2]]  # idk its [4]

        implicant_2_label.next_to(implicant_m6, RIGHT, buff=0.7)
        self.wait_to("implicant ac'", 1)
        self.play(Create(implicant_m6))
        self.wait_to("implicant ac'", 2)
        self.play(Write(implicant_2_label))

        # make the point that AC' are the same, but only B differs
        anims = [pulse(m, scale=1.5, run_time=0.8) for m in ACbar_top]
        self.wait_to("implicant ac'", 3)
        self.play(*anims)

        # implicant_acnot_top = kmap.highlight_group_open_wrap(
        #     minterms=[4], side="top", color=IMPLICANT_ACNOT_COLOR,
        #     stroke_width=s.imp_stroke_width, buff=-0.2)
        # implicant_acnot_bottom = kmap.highlight_group_open_wrap(
        #     minterms=[6], side="bottom", color=IMPLICANT_ACNOT_COLOR,
        #     stroke_width=s.imp_stroke_width, buff=-0.2)
        implicant_acnot_top.set_color(IMPLICANT_ACNOT_COLOR)
        implicant_acnot_bottom.set_color(IMPLICANT_ACNOT_COLOR)
        implicant_acnot_label = MathTex(  # r"\begin{aligned}"
            r"&\text{Prime Implicant: }\\"
            r"&A\overline{C}",
            # r"\end{aligned}",
            substrings_to_isolate=[r"&\text{Prime Implicant: }", r"A", r"\overline{C}"],
            tex_template=tpl,
            font_size=IMPLICANT_FONT_SIZE,
            color=IMPLICANT_ACNOT_COLOR
        ).move_to(implicant_1_label).shift(0.3*RIGHT)
        # implicant_acnot = VGroup(implicant_acnot_top, implicant_acnot_bottom)
        self.wait_to("implicant ac'", 4)
        self.play(TransformMatchingShapes(implicant_1, implicant_acnot_top),
                  TransformMatchingShapes(implicant_m6, implicant_acnot_bottom),
                  run_time=1.0)
        # The transform is bad, but fading out and in is worse
        self.play(TransformMatchingShapes(implicant_1_label, implicant_acnot_label),
        # self.play(FadeOut(implicant_1_label),
                  FadeOut(implicant_2_label),
        #           FadeIn(implicant_acnot_label),
                  run_time=2.0)

        ckt_2 = AndGate(leads=[r"A", r"\overline{C}"],
                        output_label="X")
        ckt_2.scale(0.7)
        ckt_2.next_to(implicant_acnot_label, DOWN, buff=0.3)
        intermission_slide.show(self, wait_to="intermission ends")  # index: 1
        self.wait_to("implicant ac'", 5)

        # flash top and bottom lines of kmap
        left_x = kmap.cells_group.get_left()[0]
        right_x = kmap.cells_group.get_right()[0]
        top_y = kmap.cells_group.get_top()[1]
        bot_y = kmap.cells_group.get_bottom()[1]

        top_line = Line([left_x, top_y, 0], [right_x, top_y, 0],
                        color=GREEN_C, stroke_width=10)
        bottom_line = Line([left_x, bot_y, 0], [right_x, bot_y, 0],
                           color=GREEN_C, stroke_width=10)
        self.play(Create(top_line), Create(bottom_line), run_time=1.0)
        self.wait_to("implicant ac'", 6)

        top_line.save_state()
        bottom_line.save_state()

        self.play(
            top_line.animate.set_stroke(width=24),
            bottom_line.animate.set_stroke(width=24),
            run_time=0.5,
        )
        self.play(
            Restore(top_line),
            Restore(bottom_line),
            run_time=0.5,
        )

        self.play(FadeOut(top_line), FadeOut(bottom_line), run_time=1.0)
        self.wait_to("implicant ac'", 7)


        self.wait_to("implicant ac'", 8)
        self.play(Create(ckt_2), run_time=2)
        # endregion implicant ac'

        # region implicant ab
        # fade out circuit, change example number and flip M7 to m7
        self.wait_to("implicant ab", 0)
        example_label_new = Text(f"Example 6", font_size=s.ex_lbl_font_size,
                                 font=s.text_font
                                 ).move_to(example_label)
        term_flip, tt_flip = flip_maxterm_to_minterm(kmap_terms[7], truth_table.get_cell(row=7, col=3))

        self.play(FadeOut(ckt_2), term_flip, tt_flip,
                  example_label.animate.become(example_label_new),
                  run_time=1.0)

        # region invalid implicant
        invalid_label = Text("Not valid implicant\n(shape 3x1)",
                             font_size=s.text_font_size, font=s.text_font,
                             color=INVALID_IMPLICANT_COLOR)
        invalid_impl = kmap.highlight_group_open_wrap(
            minterms=[7, 6], side="bottom", color=INVALID_IMPLICANT_COLOR,
            stroke_width=s.imp_stroke_width, buff=-0.2)
        invalid_label.next_to(invalid_impl, RIGHT).shift(0.7*DOWN)
        self.wait_to("implicant ab", 1)
        implicant_acnot_bottom.save_state()
        implicant_acnot_top.save_state()
        self.play(Transform(implicant_acnot_bottom, invalid_impl),
                  implicant_acnot_top.animate.set_stroke(color=INVALID_IMPLICANT_COLOR),
                  Write(invalid_label), 
                  FadeOut(implicant_acnot_label), run_time=1.0)
        self.wait_to("implicant ab", 2)
        # restore everything
        self.play(FadeIn(implicant_acnot_label),
                  FadeOut(invalid_label),
                  Restore(implicant_acnot_bottom), Restore(implicant_acnot_top),
                  run_time=1.0)
        # endregion invalid implicant
        implicant_ab_start = kmap.highlight_group([7], color=IMPLICANT_AB_COLOR,
                                            stroke_width=8, buff=-0.2)
        implicant_ab = kmap.highlight_group([6, 7], color=IMPLICANT_AB_COLOR,
                                            stroke_width=8, buff=-0.2)
        implicant_ab_eqn = MathTex(r"AB",
                                     font_size=IMPLICANT_FONT_SIZE,
                                     color=IMPLICANT_AB_COLOR)
        implicant_ab_header = prime_imp_label.copy()
        implicant_ab_header.set_color(IMPLICANT_AB_COLOR)
        implicant_ab_eqn.next_to(implicant_ab_header, DOWN
                                 ).align_to(implicant_ab_header, LEFT)

        implicant_ab_label = VGroup(implicant_ab_header, implicant_ab_eqn)

        implicant_ab_label.next_to(implicant_ab, RIGHT, buff=IMPLICANT_BUFF
                                   ).shift(0.3*LEFT)
        self.wait_to("implicant ab", 3)
        self.play(Create(implicant_ab_start), run_time=1.0)

        self.wait_to("implicant ab", 4)
        self.play(Transform(implicant_ab_start, implicant_ab),
                  Write(implicant_ab_label),
                  run_time=1.0)

        self.wait_to("implicant ab", 5)
        # change the prime implicant
        new_prime_label = prime_imp_label.copy().set_color(IMPLICANT_AB_COLOR)
        new_prime_label.move_to(implicant_1_label[0]).shift(0.3 * RIGHT)


        self.remove(implicant_ab_start)
        kmap_group = VGroup(kmap, implicant_ab, implicant_acnot_top,
                            implicant_acnot_bottom,
                            # implicant_ab_start,
                            kmap_terms)
        # save and then shift
        kmap_group.save_state()
        implicant_ab_label.save_state()
        implicant_acnot_label.save_state()
        # make a circuit to show the implicants form SOP and shift the 2 implicant labels to make room
        self.play(implicant_ab_label.animate.shift(0.5*DOWN+0.5*LEFT),
                  implicant_acnot_label.animate.shift(1.0*UP+0.5*LEFT),
                  kmap_group.animate.shift(1.0*LEFT))

        ckt_builder = CircuitBuilder(var_order=["A", "B", "C"])
        inputs = [
            [("A", 1), ("C", 0)],
            [("A", 1), ("B", 1)]]
        sop_ckt1 = ckt_builder.build_sop(inputs, output_label="X")
        sop_ckt1.next_to(implicant_acnot_label, DOWN, buff=0.2).shift(0.5*RIGHT)
        sop_ckt1.scale(0.85)

        # is default to white, but incase it changes
        sop_ckt1.gates[0].set_color(IMPLICANT_ACNOT_COLOR)
        sop_ckt1.gates[1].set_color(IMPLICANT_AB_COLOR)
        # sop_ckt1.set_opacity(0)
        # self.add(sop_ckt1)

        self.wait_to("implicant ab", 7)
        self.play(Create(sop_ckt1.gates[0], run_time=1))

        self.wait_to("implicant ab", 8)
        self.play(Create(sop_ckt1.gates[1], run_time=1))

        self.wait_to("implicant ab", 9)
        rest = VGroup(*[sop_ckt1.final_gate, sop_ckt1.wires[0], sop_ckt1.wires[1]])
        self.play(Create(rest))
        # endregion implicant ab

        # region implicant b
        # clean up, shift everything back
        self.play(
            Restore(implicant_ab_label),
            Restore(implicant_acnot_label),
            Restore(kmap_group),

            FadeOut(sop_ckt1),
            run_time=2.0
        )
        self.wait_to("implicant b", 0)
        # flip M2 and M3 to m2 and m3
        example_label_new = Text(f"Example 7", font_size=s.ex_lbl_font_size,
                                 font=s.text_font
                                 ).move_to(example_label)
        term_flip_2, tt_term_flip_2 = flip_maxterm_to_minterm(kmap_terms[2], truth_table.get_cell(row=2, col=3))
        term_flip_3, tt_term_flip_3 = flip_maxterm_to_minterm(kmap_terms[3], truth_table.get_cell(row=3, col=3))
        revert_imp_label2 = implicant_label.copy().set_color(IMPLICANT_AB_COLOR)
        revert_imp_label2.move_to(implicant_ab_label[0]
                                  ).align_to(implicant_ab_label[0], LEFT)

        implicant_ab_label[0].save_state()
        self.play(term_flip_2, term_flip_3, tt_term_flip_2, tt_term_flip_3,
                  Transform(implicant_ab_label[0], revert_imp_label2),
                  example_label.animate.become(example_label_new),
                  run_time=1.0)
        self.next_section("Running")
        self.wait_to("implicant b", 1)
        # region add implicant a'b
        # not added, will think about it
        implicant_anotb = kmap.highlight_group([2, 3], color=IMPLICANT_ANOTB_COLOR,
                                               stroke_width=s.imp_stroke_width, buff=-0.2)
        implicant_anotb_label = MathTex(r"&\text{Implicant: }\\"
                                        r"&\overline{A}\,B",
                                        substrings_to_isolate=[r"\overline{A}", r"B"],
                                        tex_template=tpl,
                                        font_size=IMPLICANT_FONT_SIZE,
                                        color=IMPLICANT_ANOTB_COLOR)
        implicant_anotb_label.next_to(implicant_anotb, LEFT, buff=0.7)
        # endregion add implicant a'b

        implicant_b = kmap.highlight_group([2, 3, 6, 7], buff=-0.2,
                                           stroke_width=s.imp_stroke_width,
                                           color=IMPLICANT_AB_COLOR)


        implicant_b_eqn = MathTex(
            r"B", font_size=IMPLICANT_FONT_SIZE,
            color=IMPLICANT_AB_COLOR
            ).move_to(implicant_ab_eqn
            ).align_to(implicant_acnot_label, LEFT)
        self.wait_to("implicant b", 2)
        self.play(Transform(implicant_ab, implicant_b),
                  Transform(implicant_ab_eqn, implicant_b_eqn),
                  Restore(implicant_ab_label[0]),
                  # FadeOut(implicant_ab_label),
                  run_time=1.0)

        # pulse B 1
        digits = kmap.get_var_digits("B", 1)
        b1 = [kmap.get_var_label("B"), digits[0], digits[1]]
        anims = [pulse(m, scale=1.5, run_time=3, pause=1.0,
                       add_box=False,
                       ) for m in b1]
        self.play(*anims)
        # self.play(Circumscribe(VGroup(kmap.get_var_label("B")), color=YELLOW, time_width=2.0),
        #           Circumscribe(VGroup(kmap.get_var_digits("B", 1)), color=YELLOW, time_width=2.0))

        self.wait_to("implicant b", 3)

        # show circuit after moving everything
        self.wait_to("implicant b", 4)
        implicant_ab_label.save_state()
        implicant_acnot_label.save_state()
        kmap_group.save_state()
        self.play(implicant_ab_label.animate.shift(0.5 * DOWN + 0.9 * LEFT),
                  implicant_acnot_label.animate.shift(1.0 * UP + 0.9 * LEFT),
                  kmap_group.animate.shift(1.2 * LEFT))
        # region acnot+b circuit
        inputs = [
            [("A", 1), ("C", 0)],
            [("B", 1)]]
        sop_ckt2 = ckt_builder.build_sop(inputs, output_label="X")
        sop_ckt2.next_to(implicant_acnot_label, DOWN, buff=0.2).shift(0.5 * RIGHT)
        sop_ckt2.scale(0.85)
        sop_ckt2.gates[0].set_color(IMPLICANT_ACNOT_COLOR)
        sop_ckt2.wires[0].set_color(IMPLICANT_ACNOT_COLOR)
        sop_ckt2.gates[1].set_color(IMPLICANT_AB_COLOR)
        sop_ckt2.wires[1].set_color(IMPLICANT_AB_COLOR)

        self.play(Create(sop_ckt2))
        # endregion acnot+b circuit

        self.wait_to("implicant b", 5)
        self.play(Restore(implicant_ab_label),
                  Restore(implicant_acnot_label),
                  Restore(kmap_group),
                  FadeOut(sop_ckt2),
                  run_time=2.0)

        # endregion implicant b

        # region implicant a
        # convert truth table and KMap maxTerm 6 to minTerm 6 and change example number
        term_flip, tt_flip = flip_maxterm_to_minterm(kmap_terms[5],
                                                     truth_table.get_cell(row=5, col=3))
        example_label_new = Text(f"Example 8", font_size=s.ex_lbl_font_size,
                                 font=s.text_font
                                 ).move_to(example_label)
        revert_imp_label = implicant_label.copy().set_color(IMPLICANT_ACNOT_COLOR)
        revert_imp_label.move_to(implicant_acnot_label[0]
                                 ).shift(0.3 * LEFT).align_to(implicant_ab_eqn, LEFT)
        anims = [term_flip, tt_flip, Transform(implicant_acnot_label[0], revert_imp_label),
                 example_label.animate.become(example_label_new)]

        self.wait_to("implicant a", 0)
        self.play(*anims, run_time=1.0)

        implicant_a = kmap.highlight_group([4, 5, 6, 7], color=IMPLICANT_ACNOT_COLOR,
                                           stroke_width=8, buff=-0.2)

        implicant_a_label = MathTex(r"&\text{Prime Implicant: }\\",
            r"&A",
            # substrings_to_isolate=[r"&\text{Prime Implicant: }", r"A"],
            tex_template=tpl,
            font_size=IMPLICANT_FONT_SIZE,
            color=IMPLICANT_ACNOT_COLOR
        ).move_to(implicant_1_label).shift(0.3 * RIGHT)
        self.play(ReplacementTransform(VGroup(implicant_acnot_top),
                                       implicant_a),
                  FadeOut(implicant_acnot_bottom),
                  ReplacementTransform(implicant_acnot_label, implicant_a_label),
                  run_time=1.2)
        self.wait_to("implicant a", 1)

        # make the equation
        final_eqn = MathTex("X = A + B",
            tex_template=tpl,
            font_size=IMPLICANT_FONT_SIZE,
            color=WHITE)
        final_eqn.next_to(implicant_a_label, DOWN, buff=0.2)
        self.play(Create(final_eqn))
        self.wait_to("implicant a", 2)

        sop_ckt3 = OrGate(leads=[r"B", r"A"],
                          output_label="X")
        sop_ckt3.next_to(implicant_acnot_label, DOWN, buff=0.2).shift(0.3*RIGHT + 0.2*DOWN)
        # sop_ckt3.scale(0.85)
        print(sop_ckt3.input_labels)
        sop_ckt3.input_labels[1].set_color(IMPLICANT_ACNOT_COLOR)
        sop_ckt3.input_labels[1].scale(1.3)
        sop_ckt3.input_leads[1].set_color(IMPLICANT_ACNOT_COLOR)
        sop_ckt3.input_labels[0].set_color(IMPLICANT_AB_COLOR)
        sop_ckt3.input_labels[0].scale(1.3)
        sop_ckt3.input_leads[0].set_color(IMPLICANT_AB_COLOR)

        self.play(implicant_a_label.animate.shift(0.8*UP),
                  final_eqn.animate.shift(0.8*UP),
                  implicant_ab_label.animate.shift(0.3*DOWN))

        self.play(Create(sop_ckt3))

        self.wait_to("implicant a", 3)

        # endregion implicant a

        self.wait(1)
        super().construct()  # <-- THIS hands control to Manim Studio GUI
