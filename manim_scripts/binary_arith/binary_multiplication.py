# Copyright (c) 2025 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""

"""

__author__ = "Kyle Vitautas Lopin"

# installed libaries
from manim import *

# standard libraries
from types import SimpleNamespace

config.max_files_cached = 500
TIME = SimpleNamespace(
    title_in = 1,
    after_title=0.5,
    multiplicand_in=0.8,
    multiplier_in=0.8,
    line_in=0.6,
    beat_after_line=0.8,
    first_partial_product=1,
    first_partial=1,
    second_partial=1,
    third_partial=1,
    circumscribe=2,
    move_to_binary=5,
    binary_steps=2,

    circumscribe_multiplier=1,
    right_shift=1,
    algo_wait=3,
    algo_arrow_between=2,
    lsb_box=2,
    accum_move=2,
    lsb_0_wait=3,
    algo_indicates=2,
    wait_compare=3,
    end_indicate=2,
)
SCALE = 0.9
BIN_SCALE = 0.7
# Manim Community v0.18+
# Scene: Decimal long multiplication of 21 × 26 on the RIGHT side.
# (Left side reserved for your future binary walk-through.)
NUM1 = 27
NUM2 = 103
SMALL_NUM_1 = 27
SMALL_NUM_2 = 11
# RENDER_SECTIONS = {"decimal_1", "binary_1", "binary_2"}  # first part comparing decimal and binary
# RENDER_SECTIONS = {"decimal_1", "binary_1"}
RENDER_SECTIONS = {"binary_2", "binary_shift"}
# RENDER_SECTIONS = {"working"}
BIN_WIDTH = 11


class Multiplication(Scene):
    def sec(self, name: str):
        self.next_section(name, skip_animations=(name not in RENDER_SECTIONS))

    def construct(self):
        self.sec("decimal_1")
        # region settings and helper functions
        self.camera.background_color = BLACK
        dark = WHITE
        # inner helper functions
        def add_text(_str: str, scale: float=0.9, _color=dark):
            return Text(_str, font="Menlo", color=_color).scale(scale)

        def dim_all_except(*targets, level=0.05, rt=0.25):
            # include target submobjects so letters stay bright
            keep = set()
            for t in targets:
                keep.update(t.get_family_members_with_points())
            others = [m for m in self.mobjects if m not in keep]
            print(others)
            self.play(*[
                m.animate.set(opacity=level, stroke_opacity=level)
                for m in others
            ], run_time=rt)

        char_w = Text("0", font="Menlo", color=WHITE).scale(SCALE).width
        def surround_digit_column(group, column: int = 1, color=WHITE):
            pad_w, pad_h = 0.1, 0.3  # padding around the rows
            box = RoundedRectangle(
                corner_radius=0.15,
                width=char_w + pad_w,
                height=group.height + pad_h,
            ).set_stroke(color, 2).set_fill(opacity=0)  # no fill
            # Align the box’s RIGHT edge to the group’s RIGHT edge, then shift to the Nth column center
            box.align_to(group, RIGHT)
            box.shift(LEFT * (column ) + 0.05)  # 0.5 = center of the column

            return box

        # endregion settings and helper functions

        # region Layout
        left_col_x = -4.2  # reserved space for binary (you'll fill later)
        right_col_x = 3.8  # decimal work area

        # ---- Left placeholder (Empty space only, no label) ----
        placeholder = Rectangle(width=5.6, height=6.5, color=GREY).set_stroke(GREY, 2, opacity=0.1)
        # placeholder.move_to([left_col_x, 0, 0])
        placeholder.set_x(left_col_x).to_edge(UP, buff=0.75)  # top-align with a small margin

        # endregion

        # region Titles
        bin_title = Text("Binary Multiplication", weight=BOLD, color=dark).scale(0.6)
        bin_title.align_to(placeholder, UP + RIGHT).shift(LEFT * 0.25 + DOWN * 0.25)
        self.play(FadeIn(bin_title))
        self.add(placeholder)

        title = Text("Decimal\nlong multiplication", weight=BOLD, color=dark).scale(0.6)
        title.to_edge(UP, buff=0.75).align_to(ORIGIN + RIGHT * right_col_x, RIGHT)
        self.play(FadeIn(title, shift=DOWN))
        self.wait(TIME.title_in)
        # endregion

        # region multipliers
        scale = 0.9
        # Stack: multiplicand, multiplier, line
        multiplicand = Text(str(NUM1), font="Menlo", color=dark).scale(scale)
        multiplicand.next_to(title, DOWN, buff=0.3).align_to(title, RIGHT)
        multiplier = Text(f"× {NUM2}", font="Menlo", color=dark).scale(scale)
        multiplier.next_to(multiplicand, DOWN, buff=0.15).align_to(title, RIGHT)
        hline = Line(ORIGIN, ORIGIN + RIGHT * 2.8).next_to(multiplier, DOWN, buff=0.15).align_to(multiplier, RIGHT)
        # hline.shift(DOWN * 0.15)

        lbl_scale = 0.7
        lbl_multiplicand = Text("Multiplicand", font="Menlo", color=TEAL).scale(lbl_scale)
        lbl_multiplicand.next_to(multiplicand, LEFT, buff=0.5).align_to(multiplicand, DOWN)

        lbl_multiplier = Text("Multiplier", font="Menlo", color=TEAL).scale(lbl_scale)
        lbl_multiplier.next_to(multiplier, LEFT, buff=0.5).align_to(multiplier, DOWN)

        # show them
        # self.play(Write(multiplicand), Write(lbl_multiplicand))
        # self.play(Write(multiplier), Write(lbl_multiplier))

        self.play(FadeIn(lbl_multiplicand), Write(multiplicand))
        self.wait(TIME.multiplicand_in)
        self.play(FadeIn(lbl_multiplier), Write(multiplier))
        self.wait(TIME.multiplier_in)
        self.play(Create(hline))
        self.wait(TIME.beat_after_line)
        # endregion

        self.play(FadeOut(lbl_multiplier), FadeOut(lbl_multiplicand))

        # region decimal multiplication
        # region make partial products
        # Highlight digits (units/tens) in the multiplier
        # We'll draw transparent rectangles over the digits in the monospace Text
        def digit_box(target_text: Text, char_index_from_right: int, color=YELLOW):
            # char_index_from_right: 0 -> rightmost character
            # Find the corresponding sub-mobject for that character
            # Using monospace font, we can compute approximate box around the glyph
            # We'll scan characters to locate the non-space glyph indices.
            glyphs = [g for g in target_text]
            # Build a list of visible (non-space) glyphs with their positions left->right
            vis = [g for g in glyphs if g.width > 0.01]
            if not vis:
                return SurroundingRectangle(target_text, color=color, buff=0.08)
            target = vis[-1 - char_index_from_right] if char_index_from_right < len(vis) else vis[0]
            box = SurroundingRectangle(target, color=color, buff=0.05)
            box.set_stroke(color, 2)
            return box

        # Highlight the first digits of multiplier and multiplicand
        self.play(multiplicand.animate.set_color(YELLOW))  # highlights the '2'
        self.play(multiplier[3].animate.set_color(YELLOW))
        multiplier_box = digit_box(multiplier, 0, color=YELLOW)
        multiplicand_box = SurroundingRectangle(multiplicand, color=YELLOW, buff=0.06)
        self.play(FadeIn(multiplier_box), FadeIn(multiplicand_box))

        # add first partial product row
        partial1 = add_text(f"  {NUM1*3}", _color=YELLOW)  # 6 × 21
        partial1.next_to(hline, DOWN, buff=0.18).align_to(multiplier, RIGHT)

        scratch_pre = add_text("partial\nproduct:", _color=YELLOW, scale=0.5)
        scratch_pre.next_to(multiplicand, RIGHT, buff=0.6).align_to(multiplicand, UP).shift(UP * 0.15)
        scratch1 = MathTex(r"3\times 27 = 81", color=YELLOW).scale(0.8)
        scratch1.next_to(multiplier, RIGHT, buff=0.6).align_to(multiplier, UP)
        self.play(Write(scratch_pre))
        self.wait(TIME.first_partial_product)
        self.play(Write(scratch1))
        self.play(Write(partial1))
        self.wait(TIME.first_partial)

        self.play(multiplicand.animate.set_color(WHITE))  # highlights the '2'
        self.play(multiplier[3].animate.set_color(WHITE))

        # finish partial product 1
        self.play(FadeOut(scratch1), FadeOut(scratch_pre),
                  FadeOut(multiplicand_box), FadeOut(multiplier_box))

        self.play(multiplicand.animate.set_color(WHITE))  # highlights the '2'
        self.play(multiplier[3].animate.set_color(WHITE))

        # start partial product 2
        partial_color = PURPLE
        self.play(multiplicand.animate.set_color(partial_color))  # highlights the '2'
        self.play(multiplier[2].animate.set_color(partial_color))

        scratch_pre2 = add_text("partial\nproduct:", _color=partial_color, scale=0.5)
        scratch_pre2.next_to(multiplicand, RIGHT, buff=0.6).align_to(multiplicand, UP).shift(UP * 0.15)
        scratch2 = MathTex(r"0\times 27 = 0", color=partial_color).scale(0.8)
        scratch2.next_to(multiplier, RIGHT, buff=0.6).align_to(multiplier, UP)

        self.play(Write(scratch_pre2))
        self.play(Write(scratch2))

        self.wait(TIME.second_partial)

        # 0 × 21, shifted by a zero (tens place)
        partial2 = add_text("    00", _color=PURPLE)
        partial2.next_to(partial1, DOWN, buff=0.10).align_to(partial1, RIGHT)
        self.play(Write(partial2))
        self.wait(TIME.second_partial)
        # finish partial product 2
        # clean up partial product 2
        self.play(FadeOut(scratch2), FadeOut(scratch_pre2))
        self.play(multiplicand.animate.set_color(WHITE))  # highlights the '2'
        self.play(multiplier[2].animate.set_color(WHITE))

        # start partial product 3
        partial_color = TEAL
        self.play(multiplicand.animate.set_color(partial_color))  # highlights the '2'
        self.play(multiplier[1].animate.set_color(partial_color))

        scratch3 = MathTex(r"1\times 27 = 27", color=partial_color).scale(0.8)
        scratch3.next_to(multiplier, RIGHT, buff=0.6).align_to(multiplier, UP)

        self.play(Write(scratch3))

        self.wait(TIME.third_partial)

        # 0 × 21, shifted by a zero (tens place)
        partial3 = add_text("  2700", _color=partial_color)
        partial3.next_to(partial2, DOWN, buff=0.10).align_to(partial1, RIGHT)

        arrow_shift = Arrow(start=partial3.get_right() + RIGHT * 1.1,
                            end=partial3.get_right() + RIGHT * 0.1, buff=0,
                            color=dark)
        shift_label = Text("hundred place → append 00", font="Menlo", color=TEAL).scale(0.5)
        shift_label.next_to(arrow_shift, DOWN, buff=0.05)
        self.play(FadeIn(shift_label))
        self.play(FadeIn(arrow_shift))

        self.play(Write(partial3), FadeOut(shift_label))
        self.play(FadeOut(arrow_shift))
        self.wait(TIME.third_partial)
        # finish partial 3 and clean up
        self.play(FadeOut(scratch3))
        self.play(multiplicand.animate.set_color(WHITE))  # highlights the '2'
        self.play(multiplier[1].animate.set_color(WHITE))
        # endregion make partial products

        # region add partial products
        plus_sign = Text("+", font="Menlo", color=dark).scale(0.9)
        plus_sign.next_to(partial3, LEFT, buff=0.35)
        sum_line = Line(hline.get_left(), hline.get_right(), color=dark)
        sum_line.next_to(partial3, DOWN, buff=0.12)
        sum_line.align_to(hline, RIGHT)

        self.play(FadeIn(plus_sign), FadeIn(sum_line))

        def circumscribe_digits(group: VGroup, _result, _color=WHITE, time: int=TIME.circumscribe):
            self.play(Circumscribe(group, color=_color, buff=0.05, fade_out=True),
                      FadeIn(_result), run_time=time)

        # add the decimal parts
        result = Text("2781", font="Menlo", color=WHITE).scale(scale)
        result.next_to(sum_line, DOWN, buff=0.12).align_to(multiplier, RIGHT)

        partials = VGroup(partial1[1], partial2[1], partial3[3])
        # circumscribe_digits(partials, result[3])
        self.play(Circumscribe(partials, color=WHITE, buff=0.05, fade_out=True),
                  FadeIn(result[3]), run_time=2.5)

        partials = VGroup(partial1[0], partial2[0], partial3[2])
        self.play(Circumscribe(partials, color=WHITE, buff=0.05, fade_out=True),
                  FadeIn(result[2]), run_time=2.5)

        partials = VGroup(partial3[1])
        self.play(Circumscribe(partials, color=WHITE, buff=0.05, fade_out=True),
                  FadeIn(result[1]), run_time=2.5)
        self.play(result[1].animate.set_opacity(1))

        partials = VGroup(partial3[0])
        self.play(Circumscribe(partials, color=WHITE, buff=0.05, fade_out=True),
                  FadeIn(result[0]), run_time=2.5)
        self.play(result[0].animate.set_opacity(1))  # simple fade-in
        # endregion decimal multiplication
        self.sec("binary_1")
        # region binary multiplication
        long_bin_stuff = []  # collection to fade out when done
        multiplicand_bin = Text(f"{NUM1:b}", font="Menlo", color=dark).scale(BIN_SCALE)
        multiplicand_bin.next_to(bin_title, DOWN, buff=0.3).align_to(bin_title, RIGHT)
        multiplier_bin = Text(f"×{NUM2:b}", font="Menlo", color=dark).scale(BIN_SCALE)
        multiplier_bin.next_to(multiplicand, DOWN, buff=0.15).align_to(bin_title, RIGHT)
        hline_bin = Line(ORIGIN, ORIGIN + RIGHT * 2.8).next_to(multiplier_bin, DOWN, buff=0.15
                                                               ).align_to(multiplier_bin, RIGHT)
        long_bin_stuff.extend([hline_bin, multiplier_bin, multiplicand_bin])
        # invisible row just below the binary underline to reserve carry space, use \u2007 as blank
        bin_carry = Text("0111122111100", font="Menlo", color=dark).scale(BIN_SCALE)
        bin_carry.next_to(hline_bin, DOWN, buff=0.08).align_to(multiplier_bin, RIGHT)
        bin_carry.set_opacity(0)  # keep as layout-only
        self.add(bin_carry)

        self.play(FadeIn(multiplicand_bin), FadeIn(multiplier_bin), FadeIn(hline_bin))

        color_cycle = [YELLOW, PURPLE, TEAL, RED, RED, GOLD, BLUE]
        multiplier_bin_str = f"{NUM2:b}"
        bin_partials = []

        # add partial products
        for i, _color in enumerate(color_cycle):
            box_1 = digit_box(multiplier_bin, i, color=_color)
            box_2 = SurroundingRectangle(multiplicand_bin, color=_color, buff=0.06)
            self.play(FadeIn(box_1), FadeIn(box_2))
            print("i: ", i, multiplier_bin_str [-(i+1)])
            if multiplier_bin_str [-(i+1)] == "1":
                # add partial products
                val = NUM1 << i
                print("val: ", val)
                bin_partials.append(Text(f"{val:b}", font="Menlo", color=_color).scale(BIN_SCALE))
            else:
                # add "00000"
                bin_partials.append(Text("0"*(5+i), font="Menlo", color=_color).scale(BIN_SCALE))
            if i > 0:
                bin_partials[-1].next_to(bin_partials[-2], DOWN, buff=0.10).align_to(multiplier_bin, RIGHT)
            else:
                bin_partials[-1].next_to(hline_bin, DOWN, buff=0.18).align_to(multiplier_bin, RIGHT)

            # add highlight the padded zeros
            self.play(FadeIn(bin_partials[-1]))

            if i>0:
                zeros_group = VGroup(bin_partials[-1][-i:])
                zeros_box = SurroundingRectangle(zeros_group, color=_color, buff=0.06)
                arrow = Arrow(
                    start=zeros_group.get_right() + RIGHT * 0.6,
                    end=zeros_group.get_right()+RIGHT * 0.1,
                    buff=0,
                    color=_color,
                    stroke_width=3,
                )
                label = Text(
                    f"append {i} zero{'s' if i != 1 else ''}",
                    font="Menlo",
                    color=_color
                ).scale(0.45)
                label.next_to(arrow, RIGHT, buff=0.08)
                self.play(FadeIn(zeros_box), FadeIn(arrow))
                self.wait(TIME.binary_steps)
                self.play(FadeOut(box_1), FadeOut(box_2),
                          FadeOut(zeros_box), FadeOut(arrow))
            else:
                self.wait(TIME.binary_steps)
                self.play(FadeOut(box_1), FadeOut(box_2))

        partials_group = VGroup(*bin_partials)  # your already-created partial rows


        self.play(
            partials_group.animate
            .next_to(bin_carry, DOWN, buff=0.10)  # place directly under carry row
            .align_to(multiplier_bin, RIGHT)  # keep right edge locked
        )

        hline_bin_sum = Line(ORIGIN, ORIGIN + RIGHT * 3.4
                             ).next_to(partials_group, DOWN, buff=0.15
                             ).align_to(multiplier_bin, RIGHT)
        plus = Text("+", font="Menlo", color=dark).scale(BIN_SCALE * 0.9)
        plus.next_to(bin_partials[-1], LEFT, buff=0.25).match_y(bin_partials[-1])

        self.play(FadeIn(hline_bin_sum), FadeIn(plus))
        # endregion decimal multiplication

        bin_result = Text("101011011101", font="Menlo", color=dark).scale(BIN_SCALE)
        bin_result.next_to(bin_partials[-1], DOWN, buff=0.30).align_to(multiplier_bin, RIGHT)

        long_bin_stuff.extend([bin_partials, hline_bin_sum, plus, bin_result, bin_carry])

        n_columns, n_rows = 11, 7
        for column in range(n_columns):

            # put a box around bin_partials[right side]
            # make Vgroup

            start = 10-column
            # add the carry bit for top of Circuiscribe and last row
            if column == 0:
                vgroup = [bin_partials[0][4], bin_partials[6][10]]
            else:
                vgroup = [bin_carry[-(column+1)], bin_partials[6][start]]
            self.play(Circumscribe(VGroup(vgroup), color=WHITE,
                                   buff=0.05, fade_out=True), run_time=1.5)
            # light up result[i]
            print("ll: ", -(column+1), bin_result, bin_carry)
            # light up sum and carry
            if column == n_columns-1:
                self.play(bin_result[11 - column].animate.set_opacity(1))  # simple fade-in
            else:
                self.play(bin_result[11-column].animate.set_opacity(1),
                          bin_carry[11-column].animate.set_opacity(1))  # simple fade-in
        self.play(bin_carry[1].animate.set_opacity(1))
        self.play(bin_result[0].animate.set_opacity(1))
        bin_dec_res = Text("(2781)", color=ORANGE).next_to(bin_result, RIGHT)
        self.play(Write(bin_dec_res))
        self.wait(0.1)
        # endregion

        # region binary multiplication
        # region binary 2
        # remove all decimal stuff
        self.sec("binary_2")
        new_title = Text("Binary Multiplication", color=WHITE).scale(0.6)
        new_title.to_edge(UP, buff=0.75).align_to([right_col_x, 0, 0], RIGHT)

        self.play(FadeOut(multiplicand), FadeOut(multiplier), FadeOut(hline),
                  FadeOut(partial1), FadeOut(partial2), FadeOut(partial3),
                  FadeOut(result), FadeOut(plus_sign), FadeOut(sum_line),
                  ReplacementTransform(title, new_title))

        multiplicand = Text(f"{SMALL_NUM_1:b}", font="Menlo", color=dark).scale(scale)
        multiplicand.next_to(title, DOWN, buff=0.3).align_to(title, RIGHT)
        multiplier = Text(f"× {SMALL_NUM_2:b}", font="Menlo", color=dark).scale(scale)
        multiplier.next_to(multiplicand, DOWN, buff=0.15).align_to(title, RIGHT)
        hline = Line(ORIGIN, ORIGIN + RIGHT * 2.8).next_to(multiplier, DOWN, buff=0.15).align_to(multiplier, RIGHT)

        self.play(FadeIn(multiplicand), FadeIn(multiplier), FadeIn(hline))

        # decimal labels
        lbl_scale = scale * 0.75
        lbl_color = ORANGE

        dec1 = Text(f" ({SMALL_NUM_1})", font="Menlo", color=lbl_color).scale(lbl_scale)
        dec1.next_to(multiplicand, RIGHT, buff=0.35).align_to(multiplicand, DOWN)

        dec2 = Text(f" ({SMALL_NUM_2})", font="Menlo", color=lbl_color).scale(lbl_scale)
        dec2.next_to(multiplier, RIGHT, buff=0.35).align_to(multiplier, DOWN)

        self.play(FadeIn(dec1), FadeIn(dec2))

        # --- Build binary partial products (multiplicand = SMALL_NUM_1, multiplier = SMALL_NUM_2)
        bin_partials_short = []
        color_cycle = [YELLOW, PURPLE, TEAL, RED, GOLD, BLUE, ORANGE]

        # Fixed width so every row aligns (bits of product can be up to sum of bit-lengths)
        total_width = SMALL_NUM_1.bit_length() + SMALL_NUM_2.bit_length() - 1

        multiplier_bits = format(SMALL_NUM_2, "b")  # e.g., 27 -> "11011"

        for i, bit in enumerate(reversed(multiplier_bits)):  # LSB -> MSB
            # highlight current bit (optional, cheap box)
            cur_bit_idx_from_right = i  # 0 = ones, 1 = twos, ...
            # (If you have a glyph-level box helper, call it here)

            # build row string
            if bit == "1":
                val = SMALL_NUM_1 << i
                row_str = format(val, f"0{total_width}b")
                row_color = color_cycle[i % len(color_cycle)]
            else:
                row_str = "0" * total_width
                row_color = GREY_B

            row = Text(row_str, font="Menlo", color=row_color).scale(scale * 0.9)

            # position under the underline, right-aligned to the same column as multiplier
            if bin_partials_short:
                row.next_to(bin_partials_short[-1], DOWN, buff=0.10).align_to(multiplier, RIGHT)
            else:
                row.next_to(hline, DOWN, buff=0.18).align_to(multiplier, RIGHT)

            self.play(Write(row), run_time=0.5)
            bin_partials_short.append(row)

        # CARRY ROW
        # use a figure space at end so a trailing blank column is preserved
        carry_str = "11121110X"  # last cell blank
        bin_carry = Text(carry_str, font="Menlo", color=GREY_B).scale(scale * 0.9)
        bin_carry.next_to(hline, DOWN, buff=0.08).align_to(multiplier, RIGHT)
        bin_carry.set_opacity(0)
        self.add(bin_carry)

        # (Optional) plus sign by the last partial created (typical long-multiplication layout cue)
        plus = Text("+", font="Menlo", color=WHITE).scale(scale * 0.9)
        plus.next_to(bin_partials_short[-1], LEFT, buff=0.25).match_y(bin_partials_short[-1])

        # (Optional) sum line under partials
        hline_bin_sum = Line(bin_partials_short[0].get_left(), bin_partials_short[0].get_right()).set_stroke(WHITE, 2)
        hline_bin_sum.align_to(bin_partials_short[-1], RIGHT).next_to(bin_partials_short[-1], DOWN, buff=0.12)

        # prepare the target pose for the group
        partials_short = VGroup(*bin_partials_short, hline_bin_sum, plus)
        partials_short.generate_target()
        partials_short.target.next_to(bin_carry, DOWN, buff=0.10).align_to(multiplier, RIGHT)

        self.play(FadeIn(plus), Create(hline_bin_sum),
                  MoveToTarget(partials_short),
                  run_time=0.2)

        # (Optional) final result (you can reveal digit-by-digit later if you want)
        product = SMALL_NUM_1 * SMALL_NUM_2
        result_short = Text(format(product, f"0{total_width}b"), font="Menlo", color=WHITE).scale(scale * 0.9)
        result_short.next_to(hline_bin_sum, DOWN, buff=0.12).align_to(multiplier, RIGHT)
        # self.play(Write(result_short), run_time=0.5)

        step_rt = 0.8  # per-column duration

        num_cols = len(result_short)  # same width used for rows/carry/result
        print("num_cols: ", num_cols, len(result_short), result_short)
        for k in range(num_cols-1, 0, -1):  # k=0 -> ones, 1 -> twos, ...
            anims = []
            print("k = ", k, "r=", k-1, len(result_short), result_short)
            # reveal carry for this column (skip if the source character is blank figure space)
            # show_carry = (carry_str[-(k + 1)] not in ("X", " ")) if k < len(carry_str) else False
            if k<9:
                anims.append(bin_carry[k-1].animate.set_opacity(1))
                # self.play(*anims, run_time=step_rt)

            # reveal result bit for this column
            # if len(result) >= (k + 1):
            anims.append(result_short[k].animate.set_opacity(1))

            # play all together for this column
            self.play(*anims, run_time=step_rt)

        self.play(result_short[0].animate.set_opacity(1))
        # show the decimal value of results next to binary results
        dec_results = Text(f"({product})", font="Menlo", color=WHITE).scale(scale * 0.9)
        dec_results.next_to(result_short, RIGHT, buff=0.35)

        self.play(FadeIn(dec_results))

        # endregion binary 2

        # region binary with shift
        self.sec("binary_shift")

        # region binary with shift setup
        # fade out all the orginial binary stuff
        self.play(FadeOut(VGroup(*long_bin_stuff)), FadeOut(title))

        multiplicand_value = SMALL_NUM_1
        multiplicand = Text(f"{SMALL_NUM_1:b}", font="Menlo", color=dark).scale(scale)
        multiplicand.next_to(title, DOWN, buff=0.5).align_to(bin_title, RIGHT)
        multiplier = Text(f"{SMALL_NUM_2:b}", font="Menlo", color=dark).scale(scale)
        multiplier.next_to(multiplicand, DOWN, buff=0.15).align_to(bin_title, RIGHT)
        multi_sign = Text("x ", font="Menlo", color=dark).scale(scale)
        multi_sign.next_to(multiplier, LEFT, buff=0.75)
        hline = Line(ORIGIN, ORIGIN + RIGHT * 2.8).next_to(multiplier, DOWN, buff=0.15).align_to(multiplier, RIGHT)

        self.play(FadeIn(multiplicand), FadeIn(multiplier),
                  FadeIn(multi_sign), FadeIn(hline))

        # decimal labels
        lbl_scale = scale * 0.75
        lbl_color = ORANGE

        dec1 = Text(f" ({SMALL_NUM_1})", font="Menlo", color=lbl_color).scale(lbl_scale)
        dec1.next_to(multiplicand, RIGHT, buff=0.35).align_to(multiplicand, DOWN)

        dec2 = Text(f" ({SMALL_NUM_2})", font="Menlo", color=lbl_color).scale(lbl_scale)
        dec2.next_to(multiplier, RIGHT, buff=0.35).align_to(multiplier, DOWN)

        self.play(FadeIn(dec1), FadeIn(dec2))
        # endregion binary with shift setup

        # region introduce shift
        for i in range(len(multiplier)-1, -1, -1):
            # circumscribe each number from right to left
            self.play(Indicate(multiplier[i]),
                      Circumscribe(multiplier[i], color=ORANGE),
                               color=YELLOW, run_time=TIME.circumscribe_multiplier)

        self.play(FadeOut(dec1), FadeOut(dec2))

        shift_arrows = Text(">>", font="Menlo", color=YELLOW).scale(scale)
        shift_arrows.next_to(multiplier, RIGHT, buff=0.35)
        shift_arrows_left = Text("<<", font="Menlo", color=YELLOW).scale(scale)
        shift_arrows_left.next_to(multiplicand, RIGHT, buff=0.35)
        shift_lbl = Text("right shift", font="Menlo", color=YELLOW).scale(0.7*scale)
        shift_lbl.next_to(shift_arrows, DOWN, buff=0.35)

        # self.play(FadeIn(shift_arrows), run_time=0.5)
        self.play(Succession(
            Indicate(shift_arrows, color=YELLOW, scale_factor=1.35, run_time=0.35),
            Indicate(shift_arrows, color=YELLOW, scale_factor=1.35, run_time=0.35),
        ),
        FadeIn(shift_lbl))

        self.wait(TIME.right_shift)
        # endregion introduce shift

        # region implement shift
        # put a box around the LSB (rightmost bit)
        lsb_box = SurroundingRectangle(multiplier[-1], corner_radius=0.12, buff=0.06) \
            .set_stroke(YELLOW_C, 4).set_fill(opacity=0)
        self.play(Create(lsb_box))
        # char_w = Text("0", font="Menlo", color=WHITE).scale(scale).width  # measure once
        print("LL: ", char_w, multiplier[0].width)
        multiplier.save_state()

        for i in range(1, 4):
            print("i = ", i)
            dx = multiplier[-i].get_center()[0] - multiplier[-(i+1)].get_center()[0]
            col_step = abs(dx)
            right_x = multiplier[-(i+1)].get_right()[0]
            print("right_x: ", right_x, multiplier.get_center(), multiplier.get_right())
            # self.play(multiplier.animate.move_to([right_x, multiplier.get_center()[1], 0],
            #           aligned_edge=RIGHT),
            #           multiplier[-i].animate.set_opacity(0), run_time=2)
            self.play(multiplier.animate.shift(RIGHT * col_step),
                      multiplier[-i].animate.set_opacity(0), run_time=2)
        self.play(multiplier.animate.set_opacity(0), run_time=2)
        self.play(Restore(multiplier))
        self.play(FadeOut(shift_lbl), FadeOut(shift_arrows))
        # endregion implement shift

        # region setup accumulator
        # --- Accumulator box under the underline ---

        # place it one row below the hline, aligned to the same right edge as the multiplier

        # initialize accumulator
        acc_num = 0
        acc_val = Text(f"{acc_num:09b}", font="Menlo", color=WHITE).scale(0.9)
        acc_val.next_to(hline, DOWN, buff=1.30).align_to(multiplier, RIGHT)
        acc_box = SurroundingRectangle(acc_val, buff=0.15, corner_radius=0.15)
        # acc_val.move_to(acc_box)

        # label under the box
        acc_label = Text("Accumulator", font="Menlo", color=GREY_B).scale(0.5)
        acc_label.next_to(acc_box, DOWN, buff=0.2)

        # show them
        self.play(Create(acc_box), FadeIn(acc_val), FadeIn(acc_label))

        # endregion setup accumulator
        # region run algo setup

        # region algo run
        algo_lines = [
            MarkupText("1) If LSB is <span foreground=\"yellow\">1</span>\n<b>add</b> "
                       "<i>multiplicand</i> to <b>accumulator</b>.", color=GREEN, font="Menlo").scale(0.5),
            # MarkupText("      <b>add</b> <i>multiplicand</i> to <b>accumulator</b>.", color=GREEN, font="Menlo").scale(0.5),
            MarkupText("2) Shift <i>multiplier</i> <b>right</b>", color=WHITE, font="Menlo").scale(0.5),
            MarkupText("3) Shift <i>multiplicand</i> <b>left</b>", color=WHITE, font="Menlo").scale(0.5),
        ]
        algo_group = VGroup(*algo_lines)

        def set_algo_text_for_lsb_0():
            new_markup = MarkupText("1) LSB is <span foreground=\"yellow\">1</span>\n — <b>add</b> "
                       "<i>multiplicand</i> to <b>accumulator</b>.", color=YELLOW, font="Menlo").scale(0.5)
            # new_markup.next_to(acc_label, DOWN, buff=0.2)
            new_markup.move_to(algo_lines[0], aligned_edge=LEFT)
            self.play(TransformMatchingShapes(algo_lines[0], new_markup), run_time=0.4)
            self.play(Indicate(new_markup, scale_factor=1.10), run_time=TIME.algo_indicates)
            algo_lines[0] = new_markup

        def set_algo_text_for_lsb_1():
            new_markup = MarkupText("1) If LSB is <span foreground=\"yellow\">0</span>\n<b>pass</b>.",
                                    color=YELLOW, font="Menlo").scale(0.5)
            new_markup.move_to(algo_lines[0], aligned_edge=LEFT)
            self.play(TransformMatchingShapes(algo_lines[0], new_markup), run_time=0.4)
            self.play(Indicate(new_markup, scale_factor=1.10), run_time=TIME.algo_indicates)
            algo_lines[0] = new_markup

        for i, line in enumerate(algo_lines):
            if i == 0:
                line.next_to(acc_label, DOWN, buff=0.2)
            else:
                line.next_to(algo_lines[i-1], DOWN, buff=0.2)
                line.align_to(algo_lines[i-1], LEFT)
            self.play(Write(line))

        # endregion run algo setup
        self.wait(TIME.algo_wait)

        def pulse_n(mobj, n=3, rt=0.4, gap=0.1, **kw):
            for i in range(n):
                self.play(Indicate(mobj, run_time=rt, **kw))
                if i < n - 1 and gap:
                    self.wait(gap)

        # pulse_n(lsb_box, n=5, scale_factor=1.5, width_pulse=4)
        # self.sec("working")
        # animate adding multiplicand
        for i in range(4):
            print("i = ", i, "multiplier_text:", multiplier.text[-(i+1)])
            if multiplier.text[-(i+1)] == "1":
                pulse_n(lsb_box, n=2, scale_factor=1.3, width_pulse=3)
                lsb_box.set_stroke(YELLOW)
                set_algo_text_for_lsb_0()
                # Make adding to accumulator animations
                # Make a copy that starts at the exact same spot as the original
                mcopy = multiplicand.copy().set_color(color_cycle[i])  # color optional to distinguish
                mcopy.move_to(multiplicand)  # same position
                # + a copy of the multiplicand, start just under the line (your "equals" line)
                plus = Text("+", font="Menlo", color=WHITE).scale(scale)
                plus.next_to(mcopy, LEFT, buff=0.25).match_y(mcopy)
                # (Optional) show the copy appearing FROM the original
                self.play(TransformFromCopy(multiplicand, mcopy), FadeIn(plus), run_time=0.4)

                row = VGroup(plus, mcopy)
                # Target: just above the accumulator, right-aligned to its column
                row.generate_target()
                row.target.next_to(acc_box, UP, buff=0.12).align_to(acc_val, RIGHT)

                # Move down as a unit
                self.play(MoveToTarget(row), run_time=0.6)
                # make an arrow from bin_partials_short[i] to mcopy
                def make_arrow(color= WHITE):
                    src = bin_partials_short[i]
                    dst = mcopy
                    arrow = Arrow(
                        src.get_edge_center(LEFT),  # tail near the row
                        dst.get_edge_center(RIGHT),  # head near the copy
                        buff=0.12,  # little gap from the text
                        stroke_width=2,
                        color=color,
                    )
                    arrow.set_stroke(width=6)  # ← thicker line
                    self.play(Create(arrow), run_time=TIME.algo_arrow_between)
                    return arrow

                arrow = make_arrow(color_cycle[i])
                # Now change accumulator number
                acc_num += multiplicand_value
                new_acc = Text(f"{acc_num:0{9}b}", font="Menlo", color=WHITE
                               ).scale(0.9).move_to(acc_val)
                row.target.move_to(acc_box).align_to(acc_val, RIGHT)
                self.play(MoveToTarget(row), run_time=0.6)
                # self.play(row.ani1.4mate.move_to(new_acc), aligned_edge=RIGHT, run_time=0.5)
                self.play(FadeTransformPieces(acc_val, new_acc),
                          # row.animate.move_to(new_acc),
                          FadeOut(arrow),
                          FadeOut(row), run_time=1)
                acc_val = new_acc

            elif multiplier.text[-(i+1)] == "0":  # is zero
                lsb_box.set_stroke(RED)
                pulse_n(lsb_box, n=2, scale_factor=1.3, width_pulse=3)
                set_algo_text_for_lsb_1()

                self.play(Indicate(bin_partials_short[i]))
                self.wait(TIME.lsb_0_wait)
            else:
                break

            # self.play(Indicate(new_markup, scale_factor=1.15), run_time=TIME.algo_indicates)
            dx=0
            if len(multiplier) > i+1:
                print("dx for i= ", i, len(multiplier))
                dx = multiplier[-(i+1)].get_center()[0] - multiplier[-(i + 2)].get_center()[0]
            col_step = abs(dx)
            right_x = multiplier[-(i+1)].get_right()[0]
            print("right_x: ", right_x, multiplier.get_center(), multiplier.get_right())

            print("i2 = ", i, col_step)
            self.play(FadeIn(shift_arrows),
                      multiplier.animate.shift(RIGHT * col_step),
                      multiplier[-(i + 1)].animate.set_opacity(0),
                      Indicate(algo_lines[1], scale_factor=1.15),
                      run_time=TIME.algo_indicates)
            self.play(FadeOut(shift_arrows))
            if i == 3:
                break

            self.play(Write(shift_arrows_left),
                      Indicate(algo_lines[2], scale_factor=1.15),
                      run_time=TIME.algo_indicates)

            # shift multiplier
            multiplicand_value = multiplicand_value << 1
            print("i3 = ", i, multiplicand_value)
            orig_str = format(multiplicand_value, f"0{5+i}b")

            # later, to reset instantly:
            orig = Text(orig_str, font="Menlo", color=dark).scale(scale).move_to(multiplicand)
            orig.align_to(multiplicand, RIGHT)
            # self.play(Write(shift_arrows_left))
            multiplicand.become(
                Text(orig_str, font="Menlo", color=dark
                     ).scale(scale
                             ).next_to(title, DOWN, buff=0.5
                                       ).align_to(bin_title, RIGHT)
            )
            self.play(# ReplacementTransform(multiplicand, orig),
                      FadeOut(shift_arrows_left), run_time=0.8)  # replaces content in place

        # endregion algo run
        # end the algo
        finish = Text("End on last bit of multiplier").scale(1.1*scale)
        finish.next_to(hline, DOWN)
        dim_all_except()
        self.play(Write(finish))
        self.wait(TIME.wait_compare)

        self.play(Indicate(result_short), Indicate(acc_val),
                  run_time=TIME.end_indicate)

        # endregion binary with shift
        self.wait(1)
        return


class Intro(Scene):
    def construct(self):
        self.camera.background_color = BLACK
        title = Text("Binary Multiplication", font="Menlo", color=WHITE).scale(1.2)
        group = VGroup(title).arrange(DOWN, buff=0.3).move_to(ORIGIN)

        self.play(FadeIn(group, shift=UP, run_time=0.8))
        self.wait(3)  # <- length of the hold
        self.play(FadeOut(group, run_time=0.5))


if __name__ == '__main__':
    print(f"{27:b}")