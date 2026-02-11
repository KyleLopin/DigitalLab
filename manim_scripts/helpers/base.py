# Copyright (c) 2025 Kyle Lopin (Naresuan University) <kylelopin@gmail.com>

"""
Base classes for manim video scripts, including:
base Scene class to add watermark
Style scripts to share visual style definitions
"""

__author__ = "Kyle Vitautas Lopin"

# standard libraries
from dataclasses import dataclass, field

# installed libraries
from manim import *


# Base scene to add watermark
class KMapBase(Scene):
    def add_watermark(self):
        # wm = Text("KVL", font_size=24, weight=BOLD, font="Brush Script MT")
        wm = Text("KVL", font_size=28, weight=BOLD, font="Snell Roundhand")

        wm.set_opacity(0.6)
        wm.to_corner(DL, buff=0.25)
        self.add(wm)
        return wm


@dataclass
class IntermissionSlides:
    """
    Reusable intermission “points slide” controller.

    Call `.show(scene, content)` repeatedly; each call reveals one additional bullet.
    The helper stores its internal slide and counter.
    The slide it shows is built in _build_slide()
    """
    title: str
    bullets: list[str]

    # Objects that should NOT be faded out (e.g., watermark, cue label)
    exclude: list[Mobject] = field(default_factory=list)

    # Styling knobs (override if you want)
    title_size: int = 46
    text_size: int = 34
    width: float = 11.0
    slide_buff: float = 0.45
    bullet_buff: float = 0.25

    TITLE_FONT = "Avenir Next"
    TEXT_FONT = "Avenir Next"

    # Internal state
    # _slide is the slide this Class shows
    _slide: VGroup | None = field(default=None, init=False, repr=False)
    # _i keeps track of which bullet points are shown
    _i: int = field(default=0, init=False, repr=False)

    def _build_slide(self, production=True) -> VGroup:
        """Create the slide and hide all bullets initially."""
        print(f"Building slide {self.title}")
        t = Text(self.title, font_size=self.title_size, weight=BOLD,
                 font=self.TITLE_FONT)
        # self.items = VGroup(*[Text(p, font_size=self.text_size, weight=BOLD,
        #                       font=self.TEXT_FONT) for p in self.bullets])
        self.items = VGroup(*[
            self.make_hanging_item(p, font=self.TEXT_FONT,
                                   label_size=int(self.text_size*0.95),
                                   body_size=self.text_size,
                                   ) for p in self.bullets
                              ])

        # IMPORTANT: arrange them so they don't overlap
        self.items.arrange(DOWN, aligned_edge=LEFT, buff=self.bullet_buff)

        # Align all bodies to the same left x (hanging indent)
        bodies = VGroup(*[
            it[1] for it in self.items
            if isinstance(it, VGroup) and len(it) >= 2
        ])
        if len(bodies) > 0:
            target_left_x = bodies[0].get_left()[0]
            for b in bodies:
                b.shift(RIGHT * (target_left_x - b.get_left()[0]))

        _slide = VGroup(t, self.items
                        ).arrange(DOWN, buff=self.slide_buff, aligned_edge=LEFT
                                  ).move_to(ORIGIN)
        _slide.set_width(self.width)
        # hide all bullets initially
        for item in self.items:
            item.set_opacity(0)

        # Make an all black slide to hide the orignal slide to project new intermission slide on
        scale = 0.8
        if production:
            scale = 1.0
        self.cover = Rectangle(width=config.frame_width,
                          height=scale * config.frame_height
                          ).set_fill(BLACK, 1).set_stroke(
            width=0).set_z_index(1000)

        return _slide

    def reset(self) -> None:
        """Reset bullet reveal progression back to the start."""
        self._i = 0
        if self._slide is not None:
            bl: BulletedList = self._slide[1]
            for item in bl:
                item.set_opacity(0)

    def split_label_body(self, s: str, sep: str = "|") -> tuple[str | None, str]:
        """Split 'LABEL|BODY'. If no sep, returns (None, s)."""
        if sep in s:
            left, right = s.split(sep, 1)
            return left.strip(), right.strip()
        return None, s

    def make_hanging_item(self, s: str,
            *,
            sep: str = "|",
            font: str = "Avenir Next",
            label_size: int = 36,
            body_size: int = 36,
            label_buff: float = 0.25,
            line_spacing: float = 0.9,
    ) -> VGroup | Text:
        label_txt, body_txt = self.split_label_body(s, sep=sep)

        body = Text(body_txt, font=font, font_size=body_size, line_spacing=line_spacing)

        if label_txt is None:
            return body

        label = Text(label_txt, font=font, font_size=label_size, weight="BOLD")

        item = VGroup(label, body).arrange(RIGHT, buff=label_buff, aligned_edge=UP)
        return item

    def highlight(self, scene, idx,
                  dim_opacity=0.25, hi_opacity=1.0,
                  hi_color=YELLOW,
                  fade_rt: float = 0.6,
                  reveal_rt: float = 0.4,
                  wait_to: str = "",
                  ):
        """Return animations to highlight bullet `idx` WITHOUT touching self.i."""
        anims = [self._slide[0].animate.set_opacity(dim_opacity).set_color(WHITE)]
        for j, m in enumerate(self.items):
            if j == idx:
                anims += [
                    m.animate.set_opacity(hi_opacity).set_color(hi_color),
                    Indicate(m, scale_factor=1.06),
                ]
            else:
                anims.append(m.animate.set_opacity(dim_opacity).set_color(WHITE))
        # return anims
        if self._slide is None:
            raise AttributeError("self._slide not initiated yet, call .show() first")
        self._slide.set_z_index(1001)
        # add black cover to hide current objects
        scene.play(FadeIn(self.cover), run_time=fade_rt)
        # then show the intermission slide
        # scene.play(FadeIn(self._slide), run_time=reveal_rt)
        scene.play(*anims, run_time=1)
        if wait_to:
            try:
                scene.wait_to(wait_to, self._i)  # self._i only as this does not increment

            except Exception as e:
                raise KeyError(f"wait_to should be in TIMES dict got: {e}")

        # remove _slide and FadeOut the cover which is same as FadeIn old scene
        scene.play(FadeOut(self._slide), run_time=fade_rt)
        scene.play(FadeOut(self.cover), run_time=reveal_rt)


    def show(
        self,
        scene: Scene,
        *,
        fade_rt: float = 0.6,
        hold: float = 1.8,
        reveal_rt: float = 0.4,
        dim: float = 0.15,
        use_dim: bool = False,
        wait_to: str = "",
    ) -> None:
        """
        Fade out everything currently on-screen EXCEPT `exclude`,
        show the slide, reveal the next bullet, fade the slide out,
        then bring everything back.

        Call repeatedly to reveal bullets one-by-one.
        """
        if self._slide is None:
            self._slide = self._build_slide()

        bullets: BulletedList = self._slide[1]

        # Snapshot everything currently on screen, excluding chosen objects + the slide itself (if present)
        exclude_set = set(self.exclude)
        exclude_set.add(self._slide)

        # If there are bullets, reveal next (clamped so extra calls keep all visible)
        if len(bullets) > 0:
            idx = min(self._i, len(bullets) - 1)
        else:
            idx = None

        self._slide.set_z_index(1001)
        # add black cover to hide current objects
        scene.play(FadeIn(self.cover), run_time=fade_rt)
        # then show the intermission slide
        scene.play(FadeIn(self._slide), run_time=reveal_rt)

        # reveal next bullet
        if idx is not None:
            bullets[idx].set_opacity(1)
            scene.play(Write(bullets[idx]), run_time=reveal_rt)
            self._i = min(self._i + 1, len(bullets))

        if wait_to:
            try:
                scene.wait_to(wait_to, self._i-1)  # self._i already incremented
            except Exception as e:
                print(f"wait_to should be a list, got error: {e}")

        # remove _slide and FadeOut the cover which is same as FadeIn old scene
        scene.play(FadeOut(self._slide), run_time=fade_rt)
        scene.play(FadeOut(self.cover), run_time=reveal_rt)

