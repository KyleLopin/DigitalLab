# Copyright (c) 2025 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""

"""

__author__ = "Kyle Vitautas Lopin"

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))  # adds DigitalLab/ to sys.path

from manim import *

# local files
from manim_classes.digital_signals import DigitalSignal


class VDACSymbolBlock(VGroup):
    def __init__(self, width=2, height=1, label="VDAC", show_lead=False, show_vref=False, **kwargs):
        super().__init__(**kwargs)
        # Initialize binary display placeholder
        self.binary_display = None

        # Trapezoidal arrow shape pointing right
        points = [
            [-width/2, -height/2, 0],   # bottom left
            [width/4, -height/2, 0],    # bottom mid
            [width/2, 0, 0],            # arrow point
            [width/4, height/2, 0],     # top mid
            [-width/2, height/2, 0],    # top left
        ]
        trapezoid = Polygon(*points, color=BLACK, fill_color=BLUE_E, fill_opacity=0.6)

        self.text = Text(label, color=YELLOW_C, font_size=32).move_to(trapezoid.get_center())

        self.add(trapezoid, self.text)

        # Add lead line if requested
        if show_lead:
            lead_line = Line(
                start=trapezoid.get_right(),
                end=trapezoid.get_right() + 1.0 * RIGHT,
                color=BLACK
            )
            self.add(lead_line)

        # Add VREF pad + line if requested
        if show_vref:
            vref_pad = Square(side_length=0.4, color=BLACK, fill_opacity=1, fill_color=GREY_B)
            vref_pad.next_to(trapezoid, LEFT, buff=0.2)

            vref_line = Line(
                start=vref_pad.get_left(),
                end=vref_pad.get_left() - 0.8 * LEFT,
                color=BLACK
            )
            vref_label = Text("VREF", font_size=20, color=BLACK).next_to(vref_pad, UP, buff=0.05)

            self.add(vref_pad, vref_line, vref_label)

    def show_binary_input(self, number, bit_width=8):
        """
        Displays the given number in binary (bit_width bits) above the VDAC symbol,
        with the left edge of the binary number aligned to the left edge of the VDAC.
        Replaces any existing binary display.
        """
        # Remove existing binary text if present
        if self.binary_display:
            self.remove(self.binary_display)

        binary_str = f"{number:0{bit_width}b}"  # e.g., '00001101'

        binary_text = Text(binary_str, font_size=32, color=BLACK)

        # Position it above the VDAC
        binary_text.next_to(self, UP, buff=0.2)

        # Align left edges
        left_shift = self.get_left()[0] - binary_text.get_left()[0]
        binary_text.shift([left_shift, 0, 0])

        self.add(binary_text)
        self.binary_display = binary_text  # store reference for next update
        return binary_text


class VDACWithAxesScene(Scene):
    def construct(self):
        self.camera.background_color = WHITE  # white background

        # VDAC symbol on the left
        vdac = VDACSymbolBlock(show_lead=True)
        vdac.to_edge(LEFT, buff=1.2)

        # Built-in Axes on the right
        axes = Axes(
            x_range=[0, 10, 1],           # positive x only
            y_range=[0, 1, 0.2],          # positive y only
            axis_config={"color": BLACK},
            tips=False,
        ).scale(0.6)                      # smaller size
        axes.shift(3 * RIGHT)            # push axes to the right for space in the middle

        # Add x and y labels
        x_label = Text("Time", color=BLACK, font_size=28)
        y_label = Text("Voltage", color=BLACK, font_size=28).rotate(PI/2)

        x_label.next_to(axes.x_axis, DOWN, buff=0.2)
        y_label.next_to(axes.y_axis, LEFT, buff=0.2)

        # Animate everything
        self.play(FadeIn(vdac), Create(axes), Write(x_label), Write(y_label))
        self.wait(2)

        # Data series: each number is a binary input (8-bit DAC)
        binary_series = [
            1, 2, 3, 4, 5, 6, 7, 8]
        bit_width = 8

        prev_voltage = None
        plot_color = ORANGE
        time_axis_scale = 1
        time_scale = 1

        for i, value in enumerate(binary_series):
            binary_display = vdac.show_binary_input(value, bit_width=bit_width)
            self.play(Transform(binary_display, binary_display), run_time=0.5)

            voltage = value / (2 ** bit_width - 1) * 32  # for VDAC and will be 1 for DVDAC
            time = i / time_axis_scale

            if prev_voltage is not None:
                horiz_line = Line(
                    axes.c2p(prev_time, voltage),
                    axes.c2p(time, voltage),
                    color=plot_color
                )
                vert_line = Line(
                    axes.c2p(prev_time, prev_voltage),
                    axes.c2p(prev_time, voltage),
                    color=plot_color
                )

                self.play(Create(vert_line), run_time=0.05* time_scale)
                self.play(Create(horiz_line), run_time=1*time_scale)
            else:
                dot = Dot(axes.c2p(time, voltage), color=plot_color)
                self.play(FadeIn(dot), run_time=0.1*time_scale)

            prev_voltage = voltage
            prev_time = time

            self.wait(0.2*time_scale)

        # Create new label text with same position as current label
        new_text = Text("DVDAC", font_size=32, color=BLACK).move_to(vdac.text.get_center())

        # Animate the change smoothly
        self.play(Transform(vdac.text, new_text))

        self.wait(2)

        plot_color = RED
        midpoint = len(binary_series) // 2
        prev_time, prev_voltage = 0, 1
        for i, value in enumerate(binary_series):
            time = i / time_axis_scale

            if i < midpoint:
                # Normal VDAC behavior
                binary_display = vdac.show_binary_input(value, bit_width=bit_width)
                self.play(Transform(binary_display, binary_display), run_time=0.5)

                voltage = value / (2 ** bit_width - 1) * 32
                if prev_voltage is not None:
                    vert_line = Line(
                        axes.c2p(prev_time, prev_voltage),
                        axes.c2p(prev_time, voltage),
                        color=plot_color
                    )
                    horiz_line = Line(
                        axes.c2p(prev_time, voltage),
                        axes.c2p(time, voltage),
                        color=plot_color
                    )
                    self.play(Create(vert_line), run_time=0.05 * time_scale)
                    self.play(Create(horiz_line), run_time=1 * time_scale)
                else:
                    dot = Dot(axes.c2p(time, voltage), color=plot_color)
                    self.play(FadeIn(dot), run_time=0.1 * time_scale)

                prev_voltage = voltage
                prev_time = time
                self.wait(0.2 * time_scale)

            else:
                # DVDAC dithering behavior
                # Choose how many dither cycles to show per step
                dither_cycles = 5
                next_value = value

                # Optional: if you want to dither between previous and current value:
                dither_low = int(prev_voltage * (2 ** bit_width - 1) / 32)
                dither_high = next_value
                for j in range(dither_cycles):
                    dither_code = dither_low if j % 2 == 0 else dither_high
                    binary_display = vdac.show_binary_input(dither_code, bit_width=bit_width)
                    self.play(Transform(binary_display, binary_display), run_time=0.05)

                    dither_voltage = dither_code / (2 ** bit_width - 1) * 32
                    dither_time = time + j * 0.01  # quick small time steps for dither

                    vert_line = Line(
                        axes.c2p(dither_time, prev_voltage),
                        axes.c2p(dither_time, dither_voltage),
                        color=plot_color
                    )
                    horiz_line = Line(
                        axes.c2p(dither_time, dither_voltage),
                        axes.c2p(dither_time + 0.01, dither_voltage),
                        color=plot_color
                    )
                    self.play(Create(vert_line), run_time=0.02)
                    self.play(Create(horiz_line), run_time=0.03)

                    prev_voltage = dither_voltage
                    prev_time = dither_time


class VDACSymbolExample(Scene):
    def construct(self):
        self.camera.background_color = WHITE  # set scene background to white

        vdac = VDACSymbolBlock()
        vdac.move_to(ORIGIN)

        self.play(Create(vdac))
        self.wait(2)
