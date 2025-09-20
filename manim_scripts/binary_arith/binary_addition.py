# Copyright (c) 2025 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""

"""

__author__ = "Kyle Vitautas Lopin"

from manim import *

class BinaryAdditionStepByStep(Scene):
    def construct(self):
        # Example binary numbers (change here if desired)
        A = "1011"
        B = "1101"
        n = len(A)
        result_val = int(A, 2) + int(B, 2)
        result = bin(result_val)[2:].zfill(n+1)  # pad to show carries

        # Position helpers
        y_vals = [2, 1, 0]
        x_vals = [i for i in range(n)]

        # Create the binary numbers
        a_bits = [Text(bit, font_size=48) for bit in A]
        b_bits = [Text(bit, font_size=48) for bit in B]
        res_bits = [Text("_", font_size=48) for _ in range(n+1)]  # Initially blanks/underscores
        carry_bits = [Text("0", font_size=32, color=GREY) for _ in range(n+1)]

        # Position bits
        for i, bit in enumerate(a_bits):
            bit.move_to([i - (n)/2 + 1.5, y_vals[0], 0])
        for i, bit in enumerate(b_bits):
            bit.move_to([i - (n)/2 + 1.5, y_vals[1], 0])
        for i, bit in enumerate(res_bits):
            bit.move_to([i - (n+1)/2 + 1, y_vals[2] - 1, 0])
        for i, bit in enumerate(carry_bits):
            bit.move_to([i - (n+1)/2 + 1, y_vals[0] + 1, 0])

        # Add labels
        self.add(Text("A:", font_size=36).next_to(a_bits[0], LEFT))
        self.add(Text("B:", font_size=36).next_to(b_bits[0], LEFT))
        self.add(Text("Sum:", font_size=36).next_to(res_bits[0], LEFT, buff=0.5))
        self.add(Text("Carry:", font_size=28).move_to([-n/2 - 1, y_vals[0]+1, 0]))

        # Add all bits
        self.add(*a_bits, *b_bits, *res_bits, *carry_bits)

        # Position for the intermediate sum (between B and Sum)
        inter_sum_y = (b_bits[0].get_center()[1] + res_bits[0].get_center()[1]) / 2
        inter_sum_bits = []
        for i in range(n + 1):
            x_shift = i - (n+1)/2 + 1
            txt = Text(" ", font_size=40).move_to([x_shift, inter_sum_y, 0])
            inter_sum_bits.append(txt)
            self.add(txt)  # Add empty placeholder

        carry = 0
        for i in range(n-1, -1, -1):
            a_bit = int(A[i])
            b_bit = int(B[i])
            total = a_bit + b_bit + carry
            sum_bit = total % 2
            new_carry = 1 if total >= 2 else 0
            # new_carry = total // 2

            # Highlight the current bits being added
            self.play(
                a_bits[i].animate.set_color(YELLOW),
                b_bits[i].animate.set_color(YELLOW),
                carry_bits[i+1].animate.set_color(ORANGE),
                run_time=3
            )

            # === Show intermediate sum (e.g., "10") ===
            intermediate_sum_str = bin(total)[2:]  # e.g., 2 -> "10"
            # intermediate_sum_text = Text(intermediate_sum_str, font_size=40, color=BLUE).move_to(
            #     inter_sum_bits[i + 1].get_center())
            intermediate_sum_text = Text(
                intermediate_sum_str, font_size=40, color=BLUE
            ).next_to(b_bits[i], DOWN, buff=0.3)
            self.play(ReplacementTransform(inter_sum_bits[i + 1], intermediate_sum_text), run_time=0.4)
            inter_sum_bits[i + 1] = intermediate_sum_text

            # Pause briefly to show the intermediate sum
            self.wait(0.3)

            # Show the carry that will result from this addition
            # Animate carry out (for next left bit)
            new_carry_text = Text(str(new_carry), font_size=32, color=RED if new_carry else GREY)
            new_carry_text.move_to(carry_bits[i].get_center())
            self.play(ReplacementTransform(carry_bits[i], new_carry_text), run_time=0.4)
            carry_bits[i] = new_carry_text

            # Fill in the calculated sum bit
            sum_pos = i + 1  # result is n+1 bits, rightmost is last index
            new_sum = Text(str(sum_bit), font_size=48, color=GREEN).move_to(res_bits[sum_pos].get_center())
            self.play(
                ReplacementTransform(res_bits[sum_pos], new_sum),
                run_time=3
            )
            res_bits[sum_pos] = new_sum

            # Unhighlight
            self.play(
                a_bits[i].animate.set_color(WHITE),
                b_bits[i].animate.set_color(WHITE),
                carry_bits[i+1].animate.set_color(GREY),
                run_time=0.3
            )
            blank = Text(" ", font_size=40).move_to(inter_sum_bits[i + 1].get_center())
            self.play(ReplacementTransform(inter_sum_bits[i + 1], blank), run_time=0.3)
            inter_sum_bits[i + 1] = blank
            carry = new_carry

        # Show leftmost carry (if any)
        new_sum = Text(str(carry), font_size=48, color=GREEN).move_to(res_bits[0].get_center())
        self.play(ReplacementTransform(res_bits[0], new_sum))
        res_bits[0] = new_sum

        self.wait(2)
