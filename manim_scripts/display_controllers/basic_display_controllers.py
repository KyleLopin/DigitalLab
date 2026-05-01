# Copyright (c) 2026 Kyle Lopin (Naresuan University) <kylelopin@gmail.com>

"""

"""

__author__ = "Kyle Vitautas Lopin"


from pathlib import Path
import sys

MANIM_SCRIPTS_DIR = Path(__file__).resolve().parents[1]  # .../manim_scripts
sys.path.insert(0, str(MANIM_SCRIPTS_DIR))


from manim import *

# local files
from helpers.timing_helpers import SimpleTiming


WAIT_TOS = [3, 5.5, 11, 18]

class DisplayControllerIntro(Scene, SimpleTiming):
    def construct(self):

        self.add_sound(
            "display_controllers/audio/Display_Controller_Intro.wav",
            time_offset=0,
        )
        # -----------------------------
        # Text
        # -----------------------------
        title_text = "Display Controller"
        subtitle_text = "Counters and memory to display an image"
        bullet_texts = [
            "1) Counters and decoders to select pixels",
            "2) Add memory to store and display an image",
        ]

        # -----------------------------
        # Title and subtitle
        # -----------------------------
        title = Text(title_text, font_size=44, weight=BOLD)
        title.to_edge(UP).shift(DOWN * 0.25)

        subtitle = Text(subtitle_text, font_size=26)
        subtitle.next_to(title, DOWN, buff=0.3)
        self.wait_to(WAIT_TOS[0])
        self.play(FadeIn(title, shift=DOWN), run_time=0.9)
        self.wait_to(WAIT_TOS[1])
        self.play(FadeIn(subtitle, shift=DOWN), run_time=0.8)
        self.wait(0.3)

        # -----------------------------
        # Bullet lines
        # -----------------------------
        bullets = VGroup()
        for text in bullet_texts:
            bullet = Text(text, font_size=30)
            bullets.add(bullet)

        bullets.arrange(DOWN, aligned_edge=LEFT, buff=0.5)
        bullets.next_to(subtitle, DOWN, buff=0.8)
        bullets.align_to(title, LEFT)

        bullet_items = VGroup()
        for bullet in bullets:
            # bullet_dot = Dot(radius=0.06)
            # bullet_dot.next_to(bullet, LEFT, buff=0.25)
            bullet_items.add(VGroup(bullet))

        bullet_items.arrange(DOWN, aligned_edge=LEFT, buff=0.5)
        bullet_items.move_to(bullets.get_center())
        bullet_items.align_to(subtitle, LEFT)

        # -----------------------------
        # Animate each bullet with incoming points
        # -----------------------------
        for i, item in enumerate(bullet_items):
            # bullet_dot, bullet_text = item
            bullet_text = item

            # y = bullet_dot.get_y()
            # end_x = bullet_dot.get_x() - 0.2
            y = bullet_text.get_y()
            end_x = bullet_text.get_x() - 0.2

            start_x = -6.5

            # points = VGroup(*[
            #     Dot(radius=0.04).move_to([start_x - i * 0.3, y, 0])
            #     for i in range(6)
            # ])

            # self.add(points)
            self.wait_to(WAIT_TOS[2+i])
            self.play(
                # LaggedStart(
                #     *[p.animate.move_to([end_x, y, 0]) for p in points],
                #     lag_ratio=0.08
                # ),
                # FadeIn(bullet_dot, scale=0.5),
                FadeIn(bullet_text, shift=RIGHT * 0.2),
                run_time=1.1
            )

            # self.remove(points)
            self.wait(0.25)

        self.wait(10)