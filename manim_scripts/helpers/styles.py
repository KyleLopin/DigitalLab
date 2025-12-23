# Copyright (c) 2025 Kyle Lopin (Naresuan University) <kylelopin@gmail.com>

"""
Style scripts to share visual style definitions

Typical usage
-------------
    from manim import Text
    from manim_scripts.helpers.styles import KMAP_STYLE as S

    Text.set_default(font=S.text_font)
    header = Text("Introduction", font_size=S.header1_size, weight="BOLD")

    bullet = S.bullet + " "
    lines = VGroup(
        Text(bullet + "Build a K-map", font_size=28),
        Text(bullet + "Group 1s", font_size=28),
    ).arrange(DOWN, aligned_edge=LEFT, buff=S.line_buff)

"""

__author__ = "Kyle Vitautas Lopin"

# standard libraries
from dataclasses import dataclass

# installed libraries
from manim import *

@dataclass(frozen=True)
class Style:
    """
    Immutable visual styling settings for Manim scenes.

    A Style bundles the “look and feel” parameters used repeatedly across scenes:
    fonts, header sizes, bullet symbol, and common layout spacing. Using a single
    Style object keeps scene code clean and makes it easy to switch themes by
    importing a different preset (e.g., KMAP_STYLE vs another series style).

    Attributes
    ----------
    numbers_font:
        Font used for numeric-heavy elements (tables, indices, minterms).
    text_font:
        Default font for general text (headers, labels, bullet points).
    fancy_font:
        Optional accent font for callouts or intermission slides.
    header1_size:
        Font size for primary titles.
    header2_size:
        Font size for secondary titles/subheaders.
    cue_enabled:
        Whether time-cue UI elements should be shown (used by TimingHelpers).
    bullet:
        Bullet character to prefix list items (e.g., "•", "–", "→").
    line_buff:
        Vertical spacing between lines in a stacked text list (VGroup.arrange).
    block_buff:
        Spacing between major blocks (e.g., title block vs body block).

    Example
    -------
        from manim import Text
        from manim_scripts.helpers.styles import KMAP_STYLE as S

        Text.set_default(font=S.text_font)
        title = Text("K-map Intro", font_size=S.header1_size)
    """
    numbers_font: str = "Menlo"
    text_font: str = "Monaco"
    fancy_font: str = "Noteworthy"
    header1_size: int = 38
    header2_size: int = 32
    cue_enabled: bool = True
    bullet: str = "•"
    line_buff: float = 0.12
    block_buff: float = 0.35


# Presets (import whichever you want)
KMAP_STYLE = Style(
    numbers_font="Menlo",
    text_font="Monaco",
    fancy_font="Noteworthy",
    header1_size=38,
    header2_size=32,
    cue_enabled=True,
)