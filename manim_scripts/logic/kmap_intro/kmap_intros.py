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
import sys
from pathlib import Path

from typing_extensions import runtime

MANIM_SCRIPTS_DIR = Path(__file__).resolve().parents[2]  # .../manim_scripts
sys.path.insert(0, str(MANIM_SCRIPTS_DIR))


# local files
from helpers.timing_helpers import TimingHelpers
from helpers.base import IntermissionSlides, KMapBase  # is a Scene with watermark
from helpers.styles import KMAP_STYLE as S

INTRO_TIMES = {"intro_header": 6,
               "intro_subheader": 12,
               "roadmap": 22,
               "end_intro": 31,
               "start part 2": 45,
               "fade_end_rt": 3,
               "fade_part2": 45,
               "end part 2": 56,
               "lessons_part2": 49.5,
               "fade_part3": 64,
               "end part 3": 69}


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
        self.set_cue = False
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
                           ).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        subheader.next_to(header1, DOWN, buff=0.20).align_to(header, LEFT).shift(RIGHT * 0.6)
        # put this in 1 block to get the spacing correct
        title_block = VGroup(header, subheader).arrange(DOWN, buff=0.75)
        self.wait_to("intro_header")
        self.play(Write(header), run_time=2)
        self.wait_to("intro_subheader")
        self.play(Write(subheader), run_time=7)

        # endregion Full Video Intro

        # region Parts Intro

        # --- Roadmap: 2/3/4-variable examples ---
        roadmap_title = Text("Video Outline", font_size=S.header2_size,
                             weight=BOLD, font=S.text_font
                             ).next_to(header1, DOWN, buff=0.35)

        bullet = "• "
        r1 = Text(bullet + "Part 1: 2-variable K-maps (2×2)", font_size=28, font=S.text_font)
        r2 = Text(bullet + "Part 2: 3-variable K-maps (2×4)", font_size=28, font=S.text_font)
        r3 = Text(bullet + "Part 3: 4-variable K-maps (4×4)", font_size=28, font=S.text_font)

        roadmap_list = VGroup(r1, r2, r3).arrange(DOWN, aligned_edge=LEFT, buff=0.25)

        roadmap_block = VGroup(roadmap_title, roadmap_list
                               ).arrange(DOWN, aligned_edge=LEFT, buff=0.35)

        # place it under your intro subheader
        roadmap_block.next_to(header1, DOWN, buff=0.55).align_to(header1, LEFT).shift(DOWN * 0.2)

        # animate
        self.wait_to("roadmap")
        self.play(FadeOut(subheader))
        self.play(Write(roadmap_title), run_time=0.6)
        self.play(LaggedStart(Write(r1), Write(r2), Write(r3), lag_ratio=0.15), run_time=0.7)
        # endregion Parts Intro

        # region transition to end
        r_next, example_label = build_handoff(2, 1)
        self.wait_to("end_intro")

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
        self.wait_to("fade_part2")
        self.play(Restore(r1), FadeOut(example_label))
        self.add(r2, r3, header)

        r2.set_opacity(0.25)
        r3.set_opacity(0.25)

        self.play(
            r1.animate.set_opacity(0.25),
            # r3.animate.set_opacity(0.25),
            r2.animate.set_opacity(1.0),
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

        self.play(FadeOut(header, lessons_list), run_time=1)
        # r1.save_state()
        self.wait_to("end part 2")
        self.play(r2.animate.to_corner(UL, buff=0.2), run_time=0.6)
        self.play(Transform(r2, r_next),
                  Write(example_label))

        # endregion Intro 2

        # region Intro 3
        # reset slide
        self.play(Restore(r2))
        self.add(r1, r3, header)
        self.remove(example_label)
        self.wait_to("fade_part3")
        self.play(
            r1.animate.set_opacity(0.25),
            r2.animate.set_opacity(0.25),
            r3.animate.set_opacity(1.0),
            run_time=1
        )
        r_next, example_label = build_handoff(4, 9)
        self.wait_to("end part 3")
        # TODO: check this delete: example_label,
        self.play(FadeOut(header, r1, r2), run_time=1)
        # r1.save_state()
        # self.play(r3.animate.to_corner(UL, buff=0.2), run_time=1)
        self.play(Transform(r3, r_next))
        self.play(Write(example_label))

        # endregion Intro 3
        self.wait(2)


CONC_POINTS = [  # used for IntermissionsSlide
    "• Implicants are rectangular groups of 1s\n"
    "  with sizes that are powers of 2",
    "• Prime implicants are the largest valid groups\n"
    "  and make the equation simpler by removing variables",
    "• Implicants form AND terms\n"
    "  and the final function ORs them together\n"
    "  (Sum of Products)",
]
TIMES = {"intermission": [10, 20, 30]}

class Part1ConclusionsTransition(KMapBase, TimingHelpers):
    """
    Stand-alone transition slide for end of Part 1.
    Drop this scene between Part 1 and Part 2 (or render as its own clip).
    """

    def construct(self):
        wm = self.add_watermark()
        self.setup()

        Text.set_default(font="Menlo")  # for KMaps to work properly

        intermission = IntermissionSlides(title="Karnaugh Maps Basic Rules:",
                                          bullets=CONC_POINTS,
                                          exclude=[wm], )
        self.attach_times(TIMES)  # to intermission slide

        title = Text("Karnaugh Maps Basic Rules:", font_size=48, weight=BOLD)
        title.to_edge(UP)
        self.play(Write(title))
        bullet_mobs = VGroup(*[
            Text(p, font_size=32, line_spacing=1.1)
            for p in CONC_POINTS
        ]).arrange(DOWN, aligned_edge=LEFT, buff=0.45)

        bullet_mobs.next_to(title, DOWN, buff=0.6).to_edge(LEFT, buff=0.9)

        # Reveal one bullet at a time
        for i, mob in enumerate(bullet_mobs):
            self.play(Write(mob), run_time=1.2)
            self.wait(5)  # or self.wait_to("intermission", list_index=i) if you want timed cues

        self.wait(0.1)
