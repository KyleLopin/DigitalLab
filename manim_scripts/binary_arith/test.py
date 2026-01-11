# Copyright (c) 2025 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""
File to try new things
"""

__author__ = "Kyle Vitautas Lopin"

from manim import *

class AccumulatorDemo(Scene):
    def construct(self):
        self.camera.background_color = BLACK
        fg = WHITE

        # Blocks
        acc = RoundedRectangle(corner_radius=0.15, width=2.6, height=1.4).set_stroke(fg,2)
        acc_lbl = Text("ACC", font="Menlo", color=fg).scale(0.6).move_to(acc.get_top()+DOWN*0.35)
        acc_val = Text("0000", font="Menlo", color=fg).scale(0.9).move_to(acc)
        acc_grp = VGroup(acc, acc_lbl, acc_val).move_to(RIGHT*3)

        add = RoundedRectangle(corner_radius=0.15, width=2.2, height=1.2).set_stroke(fg,2)
        plus = Text("+", color=fg).scale(1.2).move_to(add)
        add_lbl = Text("Adder", font="Menlo", color=GRAY).scale(0.45).next_to(add, DOWN, buff=0.1)
        add_grp = VGroup(add, plus, add_lbl).next_to(acc_grp, LEFT, buff=2.2)

        # Inputs
        in_lbl = Text("IN", font="Menlo", color=fg).scale(0.6).next_to(add_grp, LEFT, buff=1.5)
        in_val = Text("0011", font="Menlo", color=YELLOW).scale(0.9).next_to(in_lbl, DOWN, buff=0.1).align_to(in_lbl, LEFT)

        # Wires
        w1 = Arrow(in_val.get_right(), add_grp.get_left(), buff=0.15).set_stroke(fg,2)
        w2 = Arrow(acc_grp.get_left(), add_grp.get_right(), buff=0.15).set_stroke(fg,2)  # ACC feedback to adder
        w3 = Arrow(add_grp.get_right()+RIGHT*0.2, acc_grp.get_left(), buff=0.15).set_stroke(fg,2)

        # Enable + clock
        en = Text("EN=0", font="Menlo", color=GRAY).scale(0.5).next_to(add_grp, UP, buff=0.2)
        clk = Text("CLK", font="Menlo", color=GRAY).scale(0.5).next_to(acc_grp, UP, buff=0.2)

        self.add(acc_grp, add_grp, in_lbl, in_val, w1, w2, w3, en, clk)

        # helpers
        def set_acc(val_bin: str):
            acc_val.set_text(val_bin)
            acc_val.move_to(acc)

        def tick_add(acc_bin: str, in_bin: str, en_on=True):
            # visualize sum in adder
            a = int(acc_bin,2); b = int(in_bin,2)
            s = format(a+b, f"0{len(acc_bin)}b")[-len(acc_bin):]  # wrap to width
            path = VMobject().set_stroke(YELLOW if en_on else GRAY, 4)
            path.set_points_as_corners([acc_grp.get_left(), add_grp.get_right(), acc_grp.get_left()])
            self.play(Create(path), run_time=0.3)
            if en_on:
                self.play(Indicate(add, color=YELLOW, scale_factor=1.03, run_time=0.3))
                self.play(Transform(acc_val, Text(s, font="Menlo", color=fg).scale(0.9).move_to(acc)), run_time=0.4)
            else:
                self.play(Indicate(add, color=GRAY, scale_factor=1.0, run_time=0.3))
            self.play(FadeOut(path), run_time=0.2)
            return s

        # Demo sequence
        width = 4
        set_acc("0000")

        # Show enable off (no update)
        self.play(en.animate.set_color(RED).set_text("EN=0"))
        _ = tick_add("0000", "0011", en_on=False)

        # Enable on, add repeatedly (accumulate)
        self.play(en.animate.set_color(GREEN).set_text("EN=1"))
        val = "0000"
        for nxt in ["0011", "0011", "0101"]:
            val = tick_add(val, nxt, en_on=True)

        # Overflow wrap demo (optional)
        self.play(in_val.animate.set_text("1111"))
        val = tick_add(val, "1111", en_on=True)  # wraps modulo 2^width
        # flash overflow
        self.play(Flash(acc_grp, color=RED, flash_radius=0.7), run_time=0.3)

