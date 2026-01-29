# Copyright (c) 2026 Kyle Lopin (Naresuan University) <kylelopin@gmail.com>

"""
Make a Manim animated video showing how a 4x4 - 4 variable Karnaugh Map works.
Is the 3rd of the 3 part intro series
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

# local files
from logic.gates.gates import *
from helpers.anim_helpers import pulse
from helpers.base import IntermissionSlides, KMapBase  # is a Scene with watermark
from helpers.timing_helpers import TimingHelpers
from kmap_intros import build_handoff
from logic.elements.TruthTable import TruthTable
from logic.elements.KMaps import KarnaughMap
import style_config as s

from manim import TexTemplate

tpl = TexTemplate()
tpl.add_to_preamble(r"\usepackage{amsmath}")  # for aligned + \text


TIMES = {"tt": [2, 10],
         "Add KMap": [15, 20, 25, 30, 32, 34, 36, 38, 40],
         "imp 1": [45, 47, 50, 52, 54, 56],
         "imp A": [60, 62, 64, 122, 126, 130, 135, 138],
         "imp b'd'": [75, 80, 82, 84, 86, 145],
         "imp bcd": [100, 105, 110, 112, 115, 120],
         "final": [130, 135, 117, 120, 125, 130],
         }
MAP_TIMING = {}

PRODUCTION = True

IMPLICANT_FONT_SIZE = 48

# COLORS
IMPLICANT_A_COLOR = RED_B
IMPLICANT_BNOTDNOT_COLOR = PURPLE
IMPLICANT_BCD_COLOR = PURE_GREEN

# SPACINGS
IMPLICANT_BUFF = 0.5


def flip_maxterm_to_minterm(term: Text, tt_term: Text):
    new_term = Text("1", font=s.numbers_font, font_size=term.font_size)
    new_term.move_to(term).match_style(term)
    # change font size to  match how the truth table got shrunk
    new_tt_term = Text("1", font=s.numbers_font, font_size=term.font_size*0.7+1)
    new_tt_term.move_to(tt_term).match_style(tt_term)
    return Transform(term, new_term), Transform(tt_term, new_tt_term)


class KMap4VarInstruct(KMapBase, TimingHelpers):
    def construct(self):
        # region setup
        self.next_section("setup")
        if not PRODUCTION:
            self.next_section(skip_animations=True)
        self.setup()  # for Manim?
        Text.set_default(font="Menlo")  # for KMaps graycode numbers to look proper
        wm = self.add_watermark()

        # attach times
        self.attach_times(TIMES)
        # initialize the upper level example numbers that were loaded during previous video
        # so that this has to be there at the start of voice over
        parts_label, example_label = build_handoff(4, 9)
        self.add(parts_label, example_label)

        implicant_label = MathTex(r"\text{Implicant:}", tex_template=tpl,
                                  font_size=IMPLICANT_FONT_SIZE)
        prime_imp_label = MathTex(r"\text{Prime Implicant:}", tex_template=tpl,
                                  font_size=IMPLICANT_FONT_SIZE)

        MINTERMS = [0, 2, 7, 8, 9, 10, 11, 12, 13, 14, 15]
        MINTERM_TEX = {
            0: r"A'B'C'D'",
            2: r"A'B'CD'",
            7: r"A'BCD",
            9: r"AB'C'D",
            10: r"AB'CD'",
            11: r"AB'CD",
            12: r"ABC'D'",
            13: r"ABC'D",
            14: r"ABCD'",
            15: r"ABCD",
        }
        # endregion setup

        # region truth table
        truth_table = TruthTable(inputs=["A", "B", "C", "D"], outputs=["X"],
                                 minterms=MINTERMS,
                                 scale=0.9)
        self.wait_to("tt", 0)
        self.play(truth_table.write_all(run_time=3))
        # move truth table to upper-left
        self.wait_to("tt", 1)
        self.play(
            truth_table.animate.scale(0.9).to_corner(UR, buff=1.0).shift(0.3 * UP),
            run_time=1.0
        )
        # endregion truth table

        # region KMap
        # region KMap init
        kmap = KarnaughMap(num_vars=4, var_names=["A", "B", "C", "D"],
                           stroke_width=4)
        kmap.scale(1.0).shift(1.8*LEFT + 0.5*DOWN)
        self.play(Create(kmap.cells_group), run_time=1)
        self.wait_to("Add KMap", 0)

        # draw kmaps A, B, C, and D to link
        _, (row_vars, col_vars) = kmap.write("vars", return_mobjects=True)
        self.play(Create(row_vars, run_time=2))
        self.wait_to("Add KMap", 1)

        self.play(Create(col_vars, run_time=2))
        self.wait_to("Add KMap", 2)

        # make column gray code, then row
        gray_code_anims, gray_code_mobjs_group = kmap.write("labels", return_mobjects=True)

        col_gray_mobs = gray_code_mobjs_group[0]
        self.play(FadeIn(*col_gray_mobs), run_time=2)

        row_gray_mobs = gray_code_mobjs_group[1]
        self.play(FadeIn(*row_gray_mobs), run_time=2)
        # endregion KMap init
        # region map to KMap
        kmap_terms = []
        kmap_terms_colors = [
            BLUE_A, BLUE_B, BLUE_C, BLUE_D,
            TEAL_A, TEAL_B, TEAL_C, TEAL_D,
            GREEN_A, GREEN_B, GREEN_C, GREEN_D,
            YELLOW_A, YELLOW_B, YELLOW_C, YELLOW_D,
        ]

        for i, _color in enumerate(kmap_terms_colors):
            _time = 2
            if i in MAP_TIMING:
                _time = MAP_TIMING[i]
            self.wait(_time)
            # show which input combination (a, bc) the term is in
            abcd = f"{i:0{4}b}"
            ab, cd = abcd[:2:], abcd[2:]

            # pulse the A B column labels
            ab_col_num = i//4
            ab_items = [kmap.get_var_digits("AB", ab_col_num)]
            ab_items.append(kmap.get_var_digits("AB", ab_col_num))
            ab_items.append(truth_table.get_label("A"))
            ab_items.append(truth_table.get_label("B"))
            ab_items.append(truth_table.get_cell(row=i, col=0))  # A value
            ab_items.append(truth_table.get_cell(row=i, col=1))  # B value
            ab_items.append(col_vars)
            for m in ab_items:
                m.set_color(BLUE)
            self.play(
                *[
                    m.animate.scale(1.5, about_point=m.get_center())
                    for m in ab_items
                ],
                rate_func=there_and_back,
                run_time=0.8,
            )

            # now the CD row and value
            cd_col_num = i%4
            cd_items = []
            cd_items.append(kmap.get_var_digits("CD", cd_col_num))
            cd_items.append(truth_table.get_label("C"))
            cd_items.append(truth_table.get_label("D"))
            cd_items.append(truth_table.get_cell(row=i, col=2))
            cd_items.append(truth_table.get_cell(row=i, col=3))
            cd_items.append(row_vars)
            for m in cd_items:
                m.set_color(YELLOW)
            self.play(
                *[
                    m.animate.scale(1.5, about_point=m.get_center())
                    for m in cd_items
                ],
                rate_func=there_and_back,
                run_time=0.8,
            )

            _term = truth_table.get_cell(row=i, col=4)  # last column
            print(i, _color)
            _term.set_color(_color)
            term = _term.copy()
            term.set_z_index(10)  # put in front
            self.add(term)
            kmap_terms.append(term)
            kmap_place, _ = kmap.get_cell_from_minterm(i)
            start = term.get_center()
            end = kmap_place.get_center()

            line = Line(start, end)
            self.play(Create(line), run_time=0.2)
            self.play(term.animate.move_to(end).scale(1.4),
                      FadeOut(line), run_time=1)

        # endregion map to KMap
        # endregion KMap

        # region implicant A B' C' D'
        imp_abncndn = kmap.highlight_group([8], IMPLICANT_A_COLOR,
                                           stroke_width=8, buff=-0.2,
                                           corner_radius=0.2)
        imp_abncndn_eqn = MathTex(r"&A\overline{B}\,\overline{C}\,\overline{D}",
                                  substrings_to_isolate=[r"A", r"\overline{B}", r"\overline{C}", r"\overline{D}"],
                                  tex_template=tpl,
                                  font_size=IMPLICANT_FONT_SIZE,
                                  color=IMPLICANT_A_COLOR)
        label_copy = implicant_label.copy().set_color(IMPLICANT_A_COLOR)
        imp_abncndn_label = VGroup(label_copy, imp_abncndn_eqn,
                                   ).arrange(DOWN, buff=0.15, aligned_edge=LEFT)
        imp_abncndn_label.next_to(imp_abncndn, RIGHT, buff=IMPLICANT_BUFF)

        self.play(Create(imp_abncndn), run_time=1.0)
        self.wait_to("imp 1", 0)

        self.play(Create(imp_abncndn_label), run_time=1.0)
        self.wait_to("imp 1", 1)

        # region all single imps
        single_imps = []
        for term in MINTERMS:
            if term == 8:
                continue  # already made
            single_imp = kmap.highlight_group([term], color=IMPLICANT_A_COLOR,
                                              stroke_width=8, buff=-0.2,
                                              corner_radius=0.2)
            self.play(Create(single_imp), run_time=0.6)
            single_imps.append(single_imp)
        # ugly equations
        big_ugly = MathTex(
            r"X=",
            r"\begin{aligned}"
            r"&\bar{A}\bar{B}\bar{C}\bar{D}"
            r" + \bar{A}\bar{B}C\bar{D}"
            r" + \bar{A}BC D\,+\\"
            r"&A\bar{B}\bar{C}\bar{D}"
            r" + A\bar{B}\bar{C}D"
            r" + A\bar{B}C\bar{D}"
            r" + A\bar{B}C D\,+\\"
            r"&AB\bar{C}\bar{D}"
            r" + AB\bar{C}D"
            r" + ABC\bar{D}"
            r" + ABCD"
            r"\end{aligned}"
        ).scale(0.95).shift(0.8*LEFT)

        self.wait_to("imp 1", 2)
        self.play(FadeOut(kmap),
                  *[FadeOut(m) for m in single_imps],
                  *[FadeOut(m) for m in kmap_terms],
                  FadeOut(imp_abncndn_label),
                  FadeOut(imp_abncndn),
                  Write(big_ugly),
                  run_time=2.0)

        self.wait_to("imp 1", 3)
        self.play(FadeIn(kmap),
                  # *[FadeIn(m) for m in single_imps],
                  *[FadeIn(m) for m in kmap_terms],
                  FadeIn(imp_abncndn_label),
                  FadeIn(imp_abncndn),
                  FadeOut(big_ugly),
                  run_time=2.0)

        # endregion all single imps

        # endregion implicant A B' C' D'

        # region implicant A
        # make all implicants at start
        imp_acndn = kmap.highlight_group([8, 12], IMPLICANT_A_COLOR,
                                         stroke_width=8, buff=-0.2,
                                         corner_radius=0.15)

        imp_acn = kmap.highlight_group([8, 9, 12, 13], IMPLICANT_A_COLOR,
                                       stroke_width=8, buff=-0.2,
                                         corner_radius=0.2)

        imp_a = kmap.highlight_group([8, 9, 10, 11, 12, 13, 14, 15], IMPLICANT_A_COLOR,
                                      stroke_width=8, buff=-0.2,
                                      corner_radius=0.2)
        imp_acndn_eqn = MathTex(r"A\,\overline{C}\,\overline{D}",
                                tex_template=tpl,
                                font_size=IMPLICANT_FONT_SIZE,
                                color=IMPLICANT_A_COLOR
                                ).move_to(imp_abncndn_eqn
                                          ).align_to(imp_abncndn_eqn, LEFT)

        imp_acn_eqn = MathTex(r"A\,\overline{C}",
                              tex_template=tpl,
                              font_size=IMPLICANT_FONT_SIZE,
                              color=IMPLICANT_A_COLOR
                              ).move_to(imp_acndn_eqn
                                        ).align_to(imp_acndn_eqn, LEFT)

        imp_a_eqn = MathTex(r"A",
                            # tex_template=tpl,
                            font_size=IMPLICANT_FONT_SIZE,
                            color=IMPLICANT_A_COLOR
                            ).move_to(imp_acn_eqn
                                      ).align_to(imp_acn_eqn, LEFT)

        self.wait_to("imp A", 0)
        self.play(# Create(imp_acndn),
                  Transform(imp_abncndn, imp_acndn),
                  TransformMatchingTex(imp_abncndn_eqn, imp_acndn_eqn),
                  rum_time=1.0)

        # pulse B is 0 and 1
        print("aa", kmap.row_gray_digits)
        print(kmap.row_gray_digits)
        B0 = kmap.get_var_digits("B", 0)[1]
        B1 = kmap.get_var_digits("B", 1)[1]
        B= kmap.get_var_label("B")
        anims = [pulse(m, scale=1.5, run_time=0.8)
                 for m in [B0, B1, B]]
        self.wait_to("imp A", 1)
        self.play(*anims)
        self.wait_to("imp A", 2)
        self.play(Transform(imp_abncndn, imp_acn),
                  TransformMatchingTex(imp_acndn_eqn, imp_acn_eqn),
                  run_time=1.0)

        D0 = kmap.get_var_digits("D", 0)[0]
        D1 = kmap.get_var_digits("D", 1)[0]
        D = kmap.get_var_label("D")
        anims = [pulse(m, scale=1.5, run_time=0.8)
                 for m in [D0, D1, D]]
        self.wait_to("imp A", 3)
        self.play(*anims)

        prime_label_copy = prime_imp_label.copy().set_color(IMPLICANT_A_COLOR)
        prime_label_copy.move_to(label_copy).align_to(label_copy, LEFT)
        # prime_imp_a_label = VGroup(label_copy, imp_a_eqn,
        #                            ).arrange(DOWN, buff=0.15, aligned_edge=LEFT
        #                                      ).scale(0.8)
        # prime_imp_a_label.next_to(imp_abncndn, RIGHT, buff=IMPLICANT_BUFF)
        self.wait_to("imp A", 4)
        self.play(Transform(imp_abncndn, imp_a),
                  TransformMatchingTex(imp_acn_eqn, imp_a_eqn),
                  run_time=1.0)
        # have to make each individual number so it scales around the middle of each
        C0 = kmap.get_var_digits("C", 0)[0]
        C01 = kmap.get_var_digits("C", 0)[1]
        C1 = kmap.get_var_digits("C", 1)[0]
        C11 = kmap.get_var_digits("C", 1)[1]
        C = kmap.get_var_label("C")
        anims = [pulse(m, scale=1.5, run_time=0.8)
                 for m in [C0, C1, C, C01, C11]]
        self.wait_to("imp A", 5)
        self.play(*anims)
        self.wait_to("imp A", 6)
        prime_explainer = Text("Prime implicants are\nimplicants that\ncan not be\nexpanded further",
                               font_size=s.num_font_size
                               ).next_to(imp_a_eqn, DOWN, buff=0.6
                                         ).align_to(imp_a_eqn, LEFT)
        self.play(TransformMatchingTex(label_copy, prime_label_copy),
                  Write(prime_explainer),
                  run_time=1.5)

        A0 = kmap.get_var_digits("A", 1)[0]
        A1 = kmap.get_var_digits("A", 1)[1]
        A = kmap.get_var_label("A")
        anims = [pulse(m, scale=1.5, run_time=0.8)
                 for m in [A, A0, A1]]

        self.wait_to("imp A", 7)
        self.play(*anims, FadeOut(prime_explainer))

        # endregion implicant A

        # region imp B'D'

        # make m0 implicant and label
        imp_m0 = kmap.highlight_group([0], IMPLICANT_BNOTDNOT_COLOR,
                                     stroke_width=8, buff=-0.2,
                                     corner_radius=0.15)
        imp_m0_eqn = MathTex(r"\overline{A}\,\overline{B}\,\overline{C}\,\overline{D}",
                             # substrings_to_isolate=[r"A", r"\overline{B}", r"\overline{C}", r"\overline{D}"],
                             # tex_template=tpl,
                             font_size=IMPLICANT_FONT_SIZE,
                             color=IMPLICANT_BNOTDNOT_COLOR)
        label_copy = implicant_label.copy().set_color(IMPLICANT_BNOTDNOT_COLOR)
        imp_m0_label = VGroup(label_copy, imp_m0_eqn
                              ).arrange(DOWN, buff=0.15, aligned_edge=RIGHT)
        imp_m0_label.next_to(imp_m0, LEFT).shift(1.0*UP)

        self.wait_to("imp b'd'", 0)
        self.play(Create(imp_m0), run_time = 1.0)
        self.play(Write(imp_m0_label), run_time=1.0)

        # expand top and bottom
        imp_m0_m2_top = kmap.highlight_group_open_wrap(
            [0], side="top", color=IMPLICANT_BNOTDNOT_COLOR,
            stroke_width=8, buff=-0.2, corner_radius=0.2)
        imp_m0_m2_bottom = kmap.highlight_group_open_wrap(
            [2], side="bottom", color=IMPLICANT_BNOTDNOT_COLOR,
            stroke_width=8, buff=-0.2, corner_radius=0.2)
        imp_m0_m2_eqn = MathTex(
            r"\overline{A}\,\overline{B}\,\overline{D}",
            font_size=IMPLICANT_FONT_SIZE,
            color=IMPLICANT_BNOTDNOT_COLOR
        ).move_to(imp_m0_eqn
                  ).align_to(imp_m0_label, RIGHT)

        self.wait_to("imp b'd'", 1)
        self.play(Transform(imp_m0, imp_m0_m2_top),
                  Transform(imp_m0_eqn, imp_m0_m2_eqn),
                  Create(imp_m0_m2_bottom),
                  run_time=1.2)

        # region connected vertical
        # flash top and bottom lines of kmap
        left_x = kmap.cells_group.get_left()[0]
        right_x = kmap.cells_group.get_right()[0]
        top_y = kmap.cells_group.get_top()[1]
        bot_y = kmap.cells_group.get_bottom()[1]

        top_line = Line([left_x, top_y, 0], [right_x, top_y, 0],
                        color=GREEN_C, stroke_width=10)
        bottom_line = Line([left_x, bot_y, 0], [right_x, bot_y, 0],
                           color=GREEN_C, stroke_width=10)
        self.wait_to("imp b'd'", 2)
        self.play(Create(top_line), Create(bottom_line), run_time=1.0)
        top_line.save_state()
        bottom_line.save_state()

        self.play(
            top_line.animate.set_stroke(width=24),
            bottom_line.animate.set_stroke(width=24),
            run_time=1.0,
        )
        self.play(
            Restore(top_line),
            Restore(bottom_line),
            run_time=1.0,
        )
        self.play(FadeOut(top_line, bottom_line))
        # endregion connected vertical

        # region connected horizontal
        left_line = Line([left_x, bot_y, 0], [left_x, top_y, 0],
                         color=GREEN_C, stroke_width=10)

        right_line = Line([right_x, bot_y, 0], [right_x, top_y, 0],
                          color=GREEN_C, stroke_width=10)
        self.wait_to("imp b'd'", 3)
        self.play(Create(left_line), Create(right_line), run_time=1.0)
        left_line.save_state()
        right_line.save_state()

        self.play(
            left_line.animate.set_stroke(width=24),
            right_line.animate.set_stroke(width=24),
            run_time=1.0,
        )
        self.play(
            Restore(left_line),
            Restore(right_line),
            run_time=1.0,
        )
        self.play(FadeOut(left_line, right_line))
        # endregion connected horizontal

        # show the implicant growing to the 4 corners
        imp_corner_m0 = kmap.highlight_group_open_wrap(
            [0], side="ul", color=IMPLICANT_BNOTDNOT_COLOR,
            stroke_width=8, buff=-0.2, corner_radius=0.2)
        imp_corner_m2 = kmap.highlight_group_open_wrap(
            [2], side="dl", color=IMPLICANT_BNOTDNOT_COLOR,
            stroke_width=8, buff=-0.2, corner_radius=0.2)
        imp_corner_m8 = kmap.highlight_group_open_wrap(
            [8], side="ur", color=IMPLICANT_BNOTDNOT_COLOR,
            stroke_width=8, buff=-0.2, corner_radius=0.2)
        imp_corner_m10 = kmap.highlight_group_open_wrap(
            [10], side="dr", color=IMPLICANT_BNOTDNOT_COLOR,
            stroke_width=8, buff=-0.2, corner_radius=0.2)

        imp_bndn_eqn = MathTex(
            r"\overline{B}\,\overline{D}",
            font_size=IMPLICANT_FONT_SIZE,
            color=IMPLICANT_BNOTDNOT_COLOR
        ).move_to(imp_m0_eqn
                  ).align_to(imp_m0_label, RIGHT)
        prime_label_2 = prime_imp_label.copy()
        prime_label_2.set_color(IMPLICANT_BNOTDNOT_COLOR)
        prime_label_2.move_to(label_copy)


        self.wait_to("imp b'd'", 4)
        self.play(Transform(imp_m0, imp_corner_m0),
                  Transform(imp_m0_m2_bottom, imp_corner_m2),
                  TransformMatchingTex(imp_m0_eqn, imp_bndn_eqn),
                  Create(imp_corner_m8),
                  Create(imp_corner_m10),
                  run_time=1.0)
        self.wait_to("imp b'd'", 5)
        self.play(TransformMatchingTex(label_copy, prime_label_2),
                  run_time=1.0)

        # endregion imp B'D'

        # region imp BCD
        imp_bcd = kmap.highlight_group([7, 15], IMPLICANT_BCD_COLOR,
                                       stroke_width=8, buff=-0.2,
                                       corner_radius=0.2)


        self.wait_to("imp bcd", 0)
        self.play(Create(imp_bcd))

        # implicant label
        imp_bcd_eqn = MathTex(r"BCD",
                              font_size=IMPLICANT_FONT_SIZE,
                              color=IMPLICANT_BCD_COLOR)
        label_copy = prime_imp_label.copy().set_color(IMPLICANT_BCD_COLOR)
        imp_bcd_label =VGroup(label_copy, imp_bcd_eqn,
                                   ).arrange(DOWN, buff=0.15, aligned_edge=LEFT)
        imp_bcd_label.next_to(imp_bcd, RIGHT, buff=1.4)
        connector = Line(
            imp_bcd.get_right(), imp_bcd_label.get_left(),
            stroke_width=8, color=IMPLICANT_BCD_COLOR,
        )

        self.play(Write(imp_bcd_label),
                  Create(connector),
                  run_time=1.2)
        self.wait_to("imp bcd", 0)
        self.play(FadeOut(connector),
                  run_time=1.2)

        # endregion imp BCD

        # region eqn and circuit
        self.next_section("Running")
        # region final eqn
        # remove the prime implicant labels
        self.play(FadeOut(prime_label_copy),
                  FadeOut(prime_label_2),
                  FadeOut(label_copy))

        # move the Kmap and stuff to make more room
        stuff_to_move = [kmap, imp_a, imp_bcd, imp_corner_m0, imp_corner_m2,
                         imp_corner_m8, imp_corner_m10]
        for term in kmap_terms:
            stuff_to_move.append(term)
        group = VGroup(*stuff_to_move)


        # final_eqn = MathTex(r"X = A + BCD", font_size=IMPLICANT_FONT_SIZE).to_corner(UR)
        final_eqn = MathTex("X=", "A", "+", "BCD", "+", "\overline{B}\,\overline{D}",
                            font_size=IMPLICANT_FONT_SIZE)
        final_eqn.shift(1.3*RIGHT+2.3*UP)
        # A_target = final_eqn.get_part_by_tex("A")
        # BCD_target = final_eqn.get_part_by_tex("BCD")

        print(type(imp_a_eqn), type(final_eqn[1]))
        self.wait_to("final", 0)
        self.remove(imp_m0_m2_top,
                    imp_m0_m2_bottom,
                    imp_abncndn,
                    imp_m0,
                    )
        self.play(
            group.animate.shift(LEFT * 1.5),
            imp_a_eqn.animate.move_to(final_eqn[1]),
            imp_bcd_eqn.animate.move_to(final_eqn[3]),
            imp_bndn_eqn.animate.move_to(final_eqn[5]),
            # TransformMatchingTex(imp_a_eqn, final_eqn[2]),  # "A" -> A slot
            # TransformMatchingTex(imp_bcd_eqn, final_eqn[4]),  # "BCD" -> BCD slot
            Write(final_eqn[0]),  # X=
            Write(final_eqn[2]),  # +
            Write(final_eqn[4]),  # +
            run_time = 4
        )
        # endregion final eqn

        # region circuit
        ckt_builder = CircuitBuilder(var_order=["A", "B", "C", "D"])
        inputs = [
            [("A", 1)],
            [("B", 1), ("C", 1), ("D", 1)],
            [("B", 0), ("D", 0)]
        ]
        final_ckt = ckt_builder.build_sop(inputs, output_label="X")
        final_ckt.scale(0.8)
        final_ckt.next_to(final_eqn, DOWN, buff=0.8)

        # color gates and wires
        final_ckt.gates[0].set_color(IMPLICANT_A_COLOR)
        final_ckt.wires[0].set_color(IMPLICANT_A_COLOR)
        final_ckt.gates[1].set_color(IMPLICANT_BCD_COLOR)
        final_ckt.wires[1].set_color(IMPLICANT_BCD_COLOR)
        final_ckt.gates[2].set_color(IMPLICANT_BNOTDNOT_COLOR)
        final_ckt.wires[2].set_color(IMPLICANT_BNOTDNOT_COLOR)

        self.wait_to("final", 1)
        self.play(Create(final_ckt),
                  run_time = 2.0)
        # endregion circuit

        # endregion eqn and circuit

        print("Scene mobjects:")
        for mob in self.mobjects:
            print(type(mob).__name__, mob)
        self.wait()
