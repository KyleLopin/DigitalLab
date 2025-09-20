# Copyright (c) 2025 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""
A file to hold classes related to drawing digital signals for Manim scripts
"""

__author__ = "Kyle Vitautas Lopin"

# installed libraries
from manim import *

# local files
from .base import GlowDot

class DigitalSignal(VGroup):
    def __init__(
        self,
        period=1,
        low_level=0.0,
        high_level=1.0,
        threshold=None,
        start_x=0,
        start_y=0,
        scale_x=1.0,
        glow_dot_size=1.0,
        **kwargs
    ):
        """
        Parameters:
        - period (float): Clock period in seconds (e.g., 1e-6 for 1 µs).
        - low_level (float): Voltage level for logic LOW.
        - high_level (float): Voltage level for logic HIGH.
        - threshold (float or None): If provided, values are digitized.
        - start_x (float): Starting X position for drawing.
        - start_y (float): Baseline Y position.
        - scale_x (float): Horizontal scale multiplier.
        - glow_dot_size (float): Glow dot size.
        """
        super().__init__(**kwargs)
        self.period = period
        self.low_level = low_level
        self.high_level = high_level
        self.threshold = threshold
        self.start_x = start_x
        self.start_y = start_y
        self.scale_x = scale_x
        self.glow_dot_size = glow_dot_size

        self.signal_waveform = VGroup()
        self.add(self.signal_waveform)

    def draw(
             self,
             values,
             scene,
             vertical_time=0.1,
             horizontal_time=1.0,
             color=YELLOW,
             show_dot=False,
        ):
        """
        Draws a digital waveform with optional animation and visual effects.

        Parameters:
        - values (list of float): Input values.
        - scene (Scene): The calling Manim scene.
        - vertical_time (float): Animation time for vertical segments.
        - horizontal_time (float): Animation time for horizontal segments.
        - color (Color): Color of the waveform lines.
        - show_dot (bool): If True, shows a glowing dot at the leading edge.
        """
        points = []
        last_val = None

        for i, v in enumerate(values):
            # Threshold if applicable
            if self.threshold is not None:
                v = self.high_level if v >= self.threshold else self.low_level

            y_val = self.start_y + (self.high_level if v == self.high_level else self.low_level)
            x_val = self.start_x + i * self.period * self.scale_x

            if last_val is not None and last_val != v:
                # vertical edge
                points.append([x_val, last_y, 0])
            points.append([x_val, y_val, 0])

            last_val = v
            last_y = y_val

        # Glowing dot (if enabled)
        dot = None
        if show_dot and points:
            dot = GlowDot(points[0], color=color).scale(self.glow_dot_size)
            scene.add(dot)

        # Draw line segments
        if len(points) > 1:
            for i in range(len(points) - 1):
                start = points[i]
                end = points[i + 1]
                line = Line(start, end, color=color)
                self.signal_waveform.add(line)
                # Check if vertical or horizontal
                is_vertical = start[0] == end[0]
                run_time = vertical_time if is_vertical else horizontal_time

                if show_dot:
                    scene.play(
                        Create(line, rate_func=linear),
                        dot.animate.move_to(end),
                        dot.glow.animate.move_to(end),
                        run_time=run_time,
                        rate_func=linear
                    )
                else:
                    scene.play(Create(line), run_time=run_time, rate_func=linear)


class DigitalSignalThresholdScene(Scene):
    def construct(self):
        # Create axes
        axes = Axes(
            x_range=[0, 10, 1],  # 10 time units
            y_range=[-1, 6, 1],  # Voltage range with buffer
            x_length=10,
            y_length=4,
            axis_config={"include_numbers": True},
            tips=False
        )
        axes.to_edge(LEFT)  # Move axes to the left
        self.add(axes)

        # Signal instance with origin matching axes
        signal = DigitalSignal(
            period=1,
            low_level=0.0,
            start_x=axes.coords_to_point(0, 0)[0],
            start_y=axes.coords_to_point(0, 0)[1],
            scale_x=1.0,
            glow_dot_size=0.5
        )

        # Data (simulate analog signal to threshold)
        data = [0, 1, 1, 0, 1, 1, 0, 0, 0, 1, 0]
        signal.draw(data, scene=self, color=BLUE, show_dot=True)
        self.add(signal)

        self.wait(2)
