# Copyright (c) 2025 Kyle Lopin (Naresuan University) <kylelopin@gmail.com>

"""

"""

__author__ = "Kyle Vitautas Lopin"

# installed libraries
from manim import *

# local files
from gates import *

class GateCheatSheet(Scene):
    def make_tile(self, gate_mob: Mobject, code_text: str, font_size=30, gap=0.25):
        """Return a VGroup(tile) = gate on top + code label underneath."""
        label = Text(code_text, font_size=font_size)
        label.next_to(gate_mob, DOWN, buff=gap).align_to(gate_mob, LEFT)
        return VGroup(gate_mob, label)

    def construct(self) -> None:
        # and1 = AndGate(leads=["A", "B"])
        # lbl = Text('AndGate(leads=["A", "B"])', font_size=36)
        # lbl.next_to(and1, DOWN, buff=0.3)
        # self.play(Create(and1), Create(lbl))
        # --- Build tiles (gate + label) ---
        tiles = []

        and1 = AndGate(leads=["A", "B"])
        tiles.append(self.make_tile(and1, 'AndGate(leads=["A", "B"])'))

        nand1 = NandGate(leads=["A", "B"])
        tiles.append(self.make_tile(nand1, 'NandGate(leads=["A", "B"])'))

        not1 = NotGate(leads=["A"])
        tiles.append(self.make_tile(not1, 'NotGate(leads=["A"])'))

        or1 = OrGate(leads=["A", "B"])
        tiles.append(self.make_tile(or1, 'OrGate(leads=["A", "B"])'))

        nor1 = NorGateSD(leads=["A", "B"])
        tiles.append(self.make_tile(nor1, 'NorGateSD(leads=["A", "B"])'))

        # --- Arrange as a left column (top-aligned) ---
        col = VGroup(*tiles).arrange(DOWN, buff=0.55, aligned_edge=LEFT)

        # Put the first tile at UL, then everything follows below
        col.scale(0.6)
        col.to_corner(UL)

        col2_tiles = []
        and3 = AndGate(leads=["A", "B", "C"])  # <-- 3 inputs inferred from leads
        # or: and3 = AndGate(leads=["A","B","C"], n_inputs=3)

        tile_and3 = self.make_tile(and3, 'AndGate(leads=["A", "B", "C"])')
        col2_tiles.append(tile_and3)
        # make SOP form
        builder = CircuitBuilder(var_order=("A", "B", "C"))

        sop = [
            [("A", 1), ("B", 0), ("C", 1)],  # A B' C
            [("A", 0), ("B", 1), ("C", 1)],  # A' B C
        ]
        sop_circ = builder.build_sop(sop, output_label="X").to_corner(UL, buff=0.6).scale(0.9)
        self.play(Create(sop_circ))
        sop_circ.gates[0].set_color(RED)
        sop_circ.wires[1].set_color(PURE_BLUE)
        tile_sop = self.make_tile(sop_circ, """
        builder = CircuitBuilder(var_order=("A", "B", "C"))
        sop = [
            [("A", 1), ("B", 0), ("C", 1)],  # A B' C
            [("A", 0), ("B", 1), ("C", 1)],  # A' B C
        ]
        sop_circ = builder.build_sop(sop, output_label="X")
        sop_circ.gates[0].set_color(RED)
        sop_circ.wires[1].set_color(PURE_BLUE)
        """)
        col2_tiles.append(tile_sop)

        col2 = VGroup(*col2_tiles).arrange(DOWN, buff=0.55, aligned_edge=LEFT)
        col2.scale(0.6)
        col2.next_to(col, RIGHT)
        # (Optional) scale to fit if you add many gates
        # col.scale(0.9)

        # --- Animate in (tile by tile) ---
        for tile in tiles:
            gate, label = tile
            self.play(Create(gate), run_time=0.6)
            self.play(FadeIn(label), run_time=0.25)
        for tile in col2_tiles:
            gate, label = tile
            self.play(Create(gate), run_time=0.6)
            self.play(FadeIn(label), run_time=0.25)


        self.wait(1)

