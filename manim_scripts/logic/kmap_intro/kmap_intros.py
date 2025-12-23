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
               "end_intro": 8}


class KMapIntroFull(KMapBase, TimingHelpers):

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
        header = Text("Introduction to Karnaugh Maps", font_size=S.header1_size,
                      weight=BOLD, font=S.text_font)

        bullet = "• "
        # make 2 lines justified
        line1 = Text(bullet + "Build Karnaugh maps from truth tables", font_size=28, font=S.text_font)
        line2 = Text(bullet + "Get the implicants and their terms", font_size=28, font=S.text_font)
        line3 = Text(bullet + "Write the Boolean equation ", font_size=28, font=S.text_font)
        line4 = Text(bullet + "Draw the logic circuit ", font_size=28, font=S.text_font)

        subheader = VGroup(line1, line2, line3, line4
                           ).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        subheader.next_to(header, DOWN, buff=0.20).align_to(header, LEFT).shift(RIGHT * 0.6)
        # put this in 1 block to get the spacing correct
        title_block = VGroup(header, subheader).arrange(DOWN, buff=0.75)
        self.play(Write(header), run_time=times["intro_header"])
        self.play(Write(subheader), run_time=times["intro_subheader"])
        self.wait_to("end_intro")
        self.play(FadeOut(subheader))
        # endregion Full Video Intro

        # region Parts Intro

        # --- Roadmap: 2/3/4-variable examples ---
        roadmap_title = Text("Video Outline", font_size=S.header2_size, weight=BOLD, font=S.text_font)

        bullet = "• "
        r1 = Text(bullet + "Example 1: 2-variable K-map (2×2)", font_size=28, font=S.text_font)
        r2 = Text(bullet + "Example 2: 3-variable K-map (2×4)", font_size=28, font=S.text_font)
        r3 = Text(bullet + "Example 3: 4-variable K-map (4×4)", font_size=28, font=S.text_font)

        roadmap_list = VGroup(r1, r2, r3).arrange(DOWN, aligned_edge=LEFT, buff=0.12)

        roadmap_block = VGroup(roadmap_title, roadmap_list
                               ).arrange(DOWN, aligned_edge=LEFT, buff=0.25)

        # place it under your intro subheader
        roadmap_block.next_to(header, DOWN, buff=0.35).align_to(header, LEFT).shift(DOWN * 0.2)

        # animate
        self.play(Write(roadmap_title), run_time=0.6)
        self.play(LaggedStart(Write(r1), Write(r2), Write(r3), lag_ratio=0.15), run_time=1.5)

        # endregion Parts Intro

        # endregion Intro
