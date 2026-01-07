# Copyright (c) 2025 Kyle Lopin (Naresuan University) <kylelopin@gmail.com>

"""

"""

__author__ = "Kyle Vitautas Lopin"


from manim import ApplyMethod, AnimationGroup, there_and_back, there_and_back_with_pause

def pulse(mobj, scale=1.25, color=None, run_time=0.4, pause=False):
    rf = there_and_back_with_pause if pause else there_and_back
    anims = [ApplyMethod(mobj.scale, scale, rate_func=rf)]
    if color is not None:
        anims.append(ApplyMethod(mobj.set_color, color, rate_func=rf))
    return AnimationGroup(*anims, lag_ratio=0.0, run_time=run_time)
