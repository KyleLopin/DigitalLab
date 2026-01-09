# standard libraries
import math

# installed libraries
from manim import *
import manimpango  # Needed for font listing
from sympy.stats.rv import sampling_E


class ShowAllFonts(Scene):
    def construct(self):
        # 1. Get list of installed fonts
        # --- Config ---
        ENTRIES_PER_BATCH = 9  # how many fonts shown at once
        COLS = 3  # columns in each page grid
        WAIT_TIME = 1.5  # pause per page
        TRANSITION_TIME = 0.4  # fade/replace speed
        font_list = manimpango.list_fonts()

        # 2. Create Text mobjects for each font
        # This will now hold VGroups, where each VGroup is [FontName, SampleText]
        all_font_entries = VGroup()
        sample_text = "Hello Manim!"
        font_name_size = 18  # Smaller size for the name
        font_sample_size = 24  # Your original size for the sample

        # Filter out duplicates and invalid entries (good practice)
        unique_font_list = sorted(list(set(f for f in font_list if isinstance(f, str) and f.strip())))

        # 2) Build ALL entries (but don't arrange all at once)
        entries = []
        for font_name in unique_font_list:
            try:
                name_mobject = Text(font_name, font_size=font_name_size, color=YELLOW_A)
                sample_mobject = Text(sample_text, font=font_name, font_size=font_sample_size, color=WHITE)

                entry = VGroup(name_mobject, sample_mobject).arrange(
                    DOWN, buff=0.1, aligned_edge=LEFT
                )
                entries.append(entry)
            except Exception as e:
                print(f"Could not render font '{font_name}': {e}")

        if not entries:
            self.add(Text("No fonts found / renderable."))
            self.wait(2)
            return

        # Helper: make a page group for a slice of entries
        def make_page(start_idx: int) -> VGroup:
            page_entries = entries[start_idx:start_idx + ENTRIES_PER_BATCH]
            page = VGroup(*page_entries)

            # Arrange this page only
            page.arrange_in_grid(
                cols=COLS,
                buff=(1.0, 0.6),
                aligned_edge=LEFT,
            )
            # page.move_to(ORIGIN)

            # --- FIT INSIDE THE FRAME (both directions), THEN CENTER ---
            margin = 2  # increase if you still see clipping
            page.scale_to_fit_width(config.frame_width - margin)
            page.scale_to_fit_height(config.frame_height - (margin + 1.0))  # leave room for counter
            page.move_to(ORIGIN)
            return page

        total_pages = math.ceil(len(entries) / ENTRIES_PER_BATCH)

        # Optional page counter
        counter = Text("", font_size=24).to_edge(DOWN)

        # 3) Show pages one by one
        page0 = make_page(0)
        counter.text = f"Fonts {1}-{min(ENTRIES_PER_BATCH, len(entries))} / {len(entries)}"
        self.add(counter)

        self.play(FadeIn(page0, shift=0.1 * UP), run_time=TRANSITION_TIME)
        self.wait(WAIT_TIME)

        prev_page = page0
        for p in range(1, total_pages):
            start = p * ENTRIES_PER_BATCH
            end = min(start + ENTRIES_PER_BATCH, len(entries))

            next_page = make_page(start)
            new_counter = Text(f"Fonts {start + 1}-{end} / {len(entries)}", font_size=24).to_edge(DOWN)

            self.play(
                FadeOut(prev_page, shift=0.1 * DOWN),
                FadeIn(next_page, shift=0.1 * UP),
                Transform(counter, new_counter),
                run_time=TRANSITION_TIME
            )
            self.wait(WAIT_TIME)
            prev_page = next_page

        self.wait(1)


# Copyright (c) 2025 Kyle Lopin (Naresuan University) <kylelopin@gmail.com>

"""

"""

__author__ = "Kyle Vitautas Lopin"
