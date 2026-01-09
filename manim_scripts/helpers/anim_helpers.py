# Copyright (c) 2025-2026 Kyle Lopin (Naresuan University) <kylelopin@gmail.com>

"""
anim_helper.py

Small animation utilities used across scenes.

Currently this module provides `pulse()`, a reusable “attention” animation that
scales a mobject up and back down (there-and-back), optionally tinting it and/or
drawing a temporary surrounding box.

Typical usage:
    from anim_helper import pulse

    self.play(pulse(label, scale=1.3, color=YELLOW, run_time=0.5))
    self.play(pulse(VGroup(a, b), add_box=True, run_time=0.7))

"""

__author__ = "Kyle Vitautas Lopin"


from manim import *


def pulse(mobj, scale=1.25, color=None,
          run_time=0.4, pause=False, add_box=False,
          box_color=YELLOW, box_buff=0.15,
          box_stroke_width=4, box_corner_radius=0.2):
    """
    Create a “pulse” animation for a Manim mobject.

    The pulse scales the mobject up and back down using a there-and-back rate
    function. Optionally, it can also temporarily change the mobject’s color.
    If `add_box=True`, a surrounding rectangle is drawn around the mobject
    during the pulse and then faded out.

    The returned value is an Animation (AnimationGroup or Succession) intended
    to be passed directly into `Scene.play()`.

    Args:
        mobj (Mobject): The mobject to pulse.
        scale (float): Peak scale factor applied to `mobj` during the pulse.
        color (Manim color | None): Optional temporary color for `mobj` during
            the pulse (applied there-and-back). If None, color is unchanged.
        run_time (float): Total duration of the pulse animation (seconds).
        pause (bool): If True, uses `there_and_back_with_pause` so the mobject
            lingers briefly at peak scale; otherwise uses `there_and_back`.
        add_box (bool): If True, draws a `SurroundingRectangle` around `mobj`
            for the duration of the pulse and then fades it out.
        box_color (Manim color): Stroke color of the surrounding rectangle.
        box_buff (float): Padding between `mobj` and the surrounding rectangle.
            This value is multiplied by `scale` internally so the box still
            looks padded at peak scale.
        box_stroke_width (float): Stroke width of the surrounding rectangle.
        box_corner_radius (float): Corner radius of the surrounding rectangle.

    Returns:
        Animation:
            - If `add_box` is False: an `AnimationGroup` that pulses `mobj`.
            - If `add_box` is True: a `Succession` that creates the box, pulses
              `mobj`, then fades out the box.

    Example:
        >>> self.play(pulse(label, scale=1.3, color=YELLOW, run_time=0.5))
        >>> self.play(pulse(VGroup(a, b), add_box=True, run_time=0.7))
    """
    box_buff *= scale
    rf = there_and_back_with_pause if pause else there_and_back
    anims = [ApplyMethod(mobj.scale, scale, rate_func=rf)]
    if color is not None:
        anims.append(ApplyMethod(mobj.set_color, color, rate_func=rf))

    if add_box:
        box = SurroundingRectangle(
            mobj, buff=box_buff, color=box_color,
            stroke_width=box_stroke_width, corner_radius=box_corner_radius
        )
        return Succession(Create(box),
                          AnimationGroup(*anims, lag_ratio=0.0, run_time=run_time * 0.6),
                          FadeOut(box),
                          run_time=run_time
                         )

    return AnimationGroup(*anims, lag_ratio=0.0, run_time=run_time)
