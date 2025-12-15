# Copyright (c) 2025 Kyle Lopin (Naresuan University) <kylelopin@gmail.com>

"""

"""

__author__ = "Kyle Vitautas Lopin"

# installed libraries
from manim import *

# local libraries
import context
from elements.TruthTable import TruthTable
from elements.KMaps import KarnaughMap
from anim_helpers import pulse

numbers_font = "Menlo"
# text_font = "Felix Titling"
text_font = "Monaco"
fancy_font = "Noteworthy"
header1_size = 38
header2_size = 32

class KMapBase(Scene):
    def add_watermark(self):
        # wm = Text("KVL", font_size=24, weight=BOLD, font="Brush Script MT")
        wm = Text("KVL", font_size=28, weight=BOLD, font="Snell Roundhand")

        wm.set_opacity(0.6)
        wm.to_corner(DL, buff=0.25)
        self.add(wm)
        return wm


class TimingHelpers:
    def mark(self):
        return self.renderer.time

    def wait_since(self, mark_time: float, duration: float):
        """Ensure duration seconds have passed since mark_time."""
        print("wait: ", max(0.0, (mark_time + duration) - self.renderer.time))
        self.wait(max(0.0, (mark_time + duration) - self.renderer.time))

    def wait_to(self, t: float):
        """Wait until absolute scene time t (seconds)."""
        self.wait(max(0.0, t - self.renderer.time))


TIMES = {"intro_subheader2": 3,
        "end_intro": 5,
         "tt_intro": 15,
         "KMap1_end": 21}


class KMapFillFromTruthTableIntro(KMapBase, TimingHelpers):
    def construct(self):
        self.add_watermark()
        Text.set_default(font="Menlo")  # for KMaps to work properly

        # Title header
        header = Text("Introduction to Karnaugh Maps", font_size=header1_size,
                      weight=BOLD, font=text_font)
        # subheader = Text("Fill a 2 variable Karnaugh map\nfrom a truth table",
        #                  font_size=28, font=text_font)
        # make 2 lines justified
        line1 = Text("Fill a 2 variable Karnaugh map", font_size=28, font=text_font)
        line2 = Text("from a truth table", font_size=28, font=text_font)

        subheader = VGroup(line1, line2).arrange(DOWN, buff=0.1)

        subheader.next_to(header, DOWN, buff=1.25).align_to(header, LEFT)
        title_block = VGroup(header, subheader).arrange(DOWN, buff=0.75)

        self.play(Write(header), run_time=2)
        self.wait_to(TIMES["intro_subheader2"])
        self.play(FadeIn(subheader), run_time=1)
        # self.play(FadeIn(subheader, shift=DOWN * 0.2), run_time=0.6)
        self.wait_to(TIMES["end_intro"])
        self.play(FadeOut(title_block))

        truth_table = TruthTable(inputs=["A", "B"],
            outputs=["x"], minterms=[2], scale=3)

        self.play(truth_table.write_all(), run_time=5)

        self.wait_to(TIMES["tt_intro"])

        self.play(
            truth_table.animate.scale(0.7).to_corner(UR, buff=1.0).shift(0.3*UP),
            run_time=1.0
        )
        # minterms = [0, 0, 1, 0]
        kmap_2x2_1 = KarnaughMap(num_vars=2, values = [],
                                 var_names=["A", "B"],
                                 stroke_width=4)
        kmap_2x2_1.shift(LEFT*1.4).scale(1.5)
        # self.play(kmap_2x2_1.write_all(run_time=2.0))
        self.play(FadeIn(kmap_2x2_1.cells_group))
        self.wait_to(TIMES["KMap1_end"])

        # draw kmaps A and B to link
        self.play(kmap_2x2_1.write("vars"), run_time=2)

        # draw kmaps A and B to link
        self.play(kmap_2x2_1.write("labels"), run_time=2)



        # highlight A 0 on truth table then K-Map
        # first time running, so figure out the loop later
        a_tt = truth_table.get_var_label("A")
        a0_tt = truth_table.get_cell(row=0, col=0)

        a_kmap = kmap_2x2_1.get_var_label("A")
        a0_kmap = kmap_2x2_1.get_var_digits("A", 0)
        items = [a_tt, a0_tt, a_kmap, a0_kmap]
        anims = [pulse(m, scale=1.5, run_time=0.8) for m in items]
        for m in items:
            m.set_color(BLUE)
        # self.play(a_a0_tt.animate.scale(2))
        self.play(*anims)
        self.wait(2)

        b_tt = truth_table.get_var_label("B")
        b0_tt = truth_table.get_cell(row=0, col=0)

        b_kmap = kmap_2x2_1.get_var_label("B")
        b0_kmap = kmap_2x2_1.get_var_digits("B", 0)

        b_b0_tt = VGroup(b_tt, b0_tt, b_kmap, b0_kmap)
        b_b0_tt.set_color(BLUE)
        # self.play(a_a0_tt.animate.scale(2))
        self.play(pulse(b_b0_tt, scale=1.5, run_time=0.8))

        self.wait(2)
