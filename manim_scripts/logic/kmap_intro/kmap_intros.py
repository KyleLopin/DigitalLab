# Copyright (c) 2025 Kyle Lopin (Naresuan University) <kylelopin@gmail.com>

"""
File to make the Intro scenes:
1) Overall Intro that morphs to Intro to 2 variable KMaps
2) Intro 3 variable KMap
3) Intro 4 varaible KMap
"""

__author__ = "Kyle Vitautas Lopin"


# installed libraries
from manim import *

# local files
from helpers.timing_helpers import TimingHelpers
from helpers.base import KMapBase  # is a Scene with watermark
from helpers.styles import KMAP_STYLE as S

INTRO_TIMES = {"intro_header": 3,
               "intro_subheader": 4,
               "end_intro": 8,
               "fade_end_rt": 3,
               "fade_part2": 20,
               "lessons_part2": 30,
               "fade_part3": 45,}


def build_handoff(num_var: int, example_start: int):
    r1_next = Text(f"{num_var}-variable K-maps",
                   font_size=26, font=S.text_font
                   ).to_corner(UL, buff=0.2)
    example_label = Text(f"Example {example_start}", font_size=26, font=S.text_font
                         ).next_to(r1_next, DOWN, buff=0.1
                                   ).align_to(r1_next, LEFT)
    return r1_next, example_label


class KMapIntros(KMapBase, TimingHelpers):

    def construct(self):
        times = INTRO_TIMES
        self.attach_times(INTRO_TIMES)  # this is used for TimingHelpers
        # region setup
        # self.next_section(skip_animations=True)
        wm = self.add_watermark()
        self.setup()
        Text.set_default(font="Menlo")  # for KMaps to work properly
        # endregion setup

        # region Intro

        # region Full Video Intro
        # Title header
        header1 = Text("Introduction to Karnaugh Maps\n", font_size=S.header1_size,
                      weight=BOLD, font=S.text_font)
        header2 = Text("(K-Maps)", font_size=S.header1_size,
                      weight=BOLD, font=S.text_font)
        header2.next_to(header1, DOWN, buff=0.1)
        # header2.align_to(header1, CENTER)

        header = VGroup(header1, header2)

        bullet = "• "
        # make 2 lines justified
        line1 = Text(bullet + "Build Karnaugh maps from truth tables", font_size=28, font=S.text_font)
        line2 = Text(bullet + "Get the implicants and their terms", font_size=28, font=S.text_font)
        line3 = Text(bullet + "Write the Boolean equation ", font_size=28, font=S.text_font)
        line4 = Text(bullet + "Draw the logic circuit ", font_size=28, font=S.text_font)

        subheader = VGroup(line1, line2, line3, line4
                           ).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        subheader.next_to(header1, DOWN, buff=0.20).align_to(header, LEFT).shift(RIGHT * 0.6)
        # put this in 1 block to get the spacing correct
        title_block = VGroup(header, subheader).arrange(DOWN, buff=0.75)
        self.play(Write(header), run_time=times["intro_header"])
        self.play(Write(subheader), run_time=times["intro_subheader"])
        self.wait_to("end_intro")
        self.play(FadeOut(subheader))

        self.wait(2)
        # endregion Full Video Intro

        # region Parts Intro

        # --- Roadmap: 2/3/4-variable examples ---
        roadmap_title = Text("Video Outline", font_size=S.header2_size, weight=BOLD, font=S.text_font)

        bullet = "• "
        r1 = Text(bullet + "Part 1: 2-variable K-maps (2×2)", font_size=28, font=S.text_font)
        r2 = Text(bullet + "Part 2: 3-variable K-maps (2×4)", font_size=28, font=S.text_font)
        r3 = Text(bullet + "Part 3: 4-variable K-maps (4×4)", font_size=28, font=S.text_font)

        roadmap_list = VGroup(r1, r2, r3).arrange(DOWN, aligned_edge=LEFT, buff=0.12)

        roadmap_block = VGroup(roadmap_title, roadmap_list
                               ).arrange(DOWN, aligned_edge=LEFT, buff=0.25)

        # place it under your intro subheader
        roadmap_block.next_to(header1, DOWN, buff=0.35).align_to(header1, LEFT).shift(DOWN * 0.2)

        # animate
        self.play(Write(roadmap_title), run_time=0.6)
        self.play(LaggedStart(Write(r1), Write(r2), Write(r3), lag_ratio=0.15), run_time=1.5)
        # endregion Parts Intro

        # region transition to end
        r_next, example_label = build_handoff(2, 1)

        self.play(FadeOut(r2, r3, header, roadmap_title),
                  run_time=1)
        r1.save_state()
        self.play(r1.animate.to_corner(UL, buff=0.2), run_time=1)
        self.play(Transform(r1, r_next))
        self.play(Write(example_label))
        # endregion transition to end

        # endregion Intro
        self.wait(5)

        # region Intro 2
        # reset slide
        self.play(Restore(r1), FadeOut(example_label))
        self.add(r2, r3, header)
        self.wait_to("fade_part2")
        self.play(
            r1.animate.set_opacity(0.25),
            r3.animate.set_opacity(0.25),
            # r2.animate.set_opacity(1.0),
            run_time=1
        )
        self.wait_to("lessons_part2")
        self.play(FadeOut(r1, r3))
        r2.save_state()
        self.play(r2.animate.next_to(header, DOWN, buff=0.5).align_to(header, LEFT))
        l1 = Text(bullet + "Using Gray code in Karnaugh Maps",
                  font_size=24, font=S.text_font)
        l2 = Text(bullet + "Wrap around implicants",
                  font_size=24, font=S.text_font)

        lessons_list = VGroup(l1, l2
                              ).arrange(DOWN, aligned_edge=LEFT, buff=0.30)
        lessons_list.next_to(r2, DOWN, buff=0.3).align_to(r2, LEFT).shift(0.5*RIGHT)
        self.play(Write(lessons_list))

        # region transition to end
        r_next, example_label = build_handoff(3, 4)

        self.play(FadeOut(header, lessons_list, example_label), run_time=1)
        # r1.save_state()
        self.play(r2.animate.to_corner(UL, buff=0.2), run_time=1)
        self.play(Transform(r2, r_next))
        self.play(Write(example_label))

        # endregion Intro 2

        # region Intro 3
        # reset slide
        self.play(Restore(r2))
        self.add(r1, r3, header)
        self.wait_to("fade_part3")
        self.play(
            FadeOut(example_label),
            r1.animate.set_opacity(0.25),
            r2.animate.set_opacity(0.25),
            r3.animate.set_opacity(1.0),
            run_time=1
        )

        # endregion Intro 3
        self.wait(2)
