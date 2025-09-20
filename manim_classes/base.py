# Copyright (c) 2025 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""

"""

__author__ = "Kyle Vitautas Lopin"


from manim import *
from manim.mobject.opengl.opengl_mobject import OpenGLMobject  # safe to import in MCE

class GlowDot(VGroup):
    def __init__(self, point=ORIGIN, color=YELLOW, radius=0.08, glow_radius=0.3, glow_opacity=0.3, **kwargs):
        super().__init__(**kwargs)

        self.dot = Dot(point=point, radius=radius, color=color)
        self.glow = Circle(radius=glow_radius, color=color).set_opacity(glow_opacity)
        self.glow.move_to(self.dot)

        self.add(self.glow, self.dot)
