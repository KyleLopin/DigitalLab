# Copyright (c) 2025 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""
Function to make state diagrams
"""

__author__ = "Kyle Vitautas Lopin"

# pip install schemdraw
import math
import schemdraw
import schemdraw.flow as flow

# map an octant (0..7) to (from_anchor_name, to_anchor_name)
# 0:E, 1:NE, 2:N, 3:NW, 4:W, 5:SW, 6:S, 7:SE  (direction from A to B)
octant_anchor_pairs = [
    ("E", "NW"),  # E
    ("NE", "W"),  # NE
    ("N", "SW"),  # N
    ("NW", "S"),  # NW
    ("SW", "SE"),  # W
    ("S", "NE"),  # SW
    ("S", "N"),  # S
    ("SE", "N"),  # SE
]


def octant(ax, ay, bx, by):
    ang = math.atan2(by - ay, bx - ax)  # -pi..pi
    o = int(round((ang % (2 * math.pi)) / (math.pi / 4))) % 8
    return o

def draw_counter_fsm(states,
                     edge_labels=None,
                     layout: str = 'circle',   # 'circle' or 'line'
                     radius: float = 3.0,
                     spacing: float = 4.0,
                     fontsize: int = 12,
                     filename: str | None = None):
    n = len(states)
    if n == 0:
        raise ValueError("states must be non-empty")
    if edge_labels is not None and len(edge_labels) != n:
        raise ValueError("edge_labels must be same length as states (one per edge, including wrap).")

    with schemdraw.Drawing(fontsize=fontsize, unit=1) as d:
        # 1) Place states
        nodes = []
        if layout == 'circle':
            for i, s in enumerate(states):
                theta = 2 * math.pi * i / n
                x = radius * math.cos(theta)
                y = -radius * math.sin(theta)
                nodes.append(d.add(flow.State().at((x, y)).label(str(s))))
        elif layout == 'line':
            # place left-to-right on a line
            y = 0
            for i, s in enumerate(states):
                x = i * spacing
                nodes.append(d.add(flow.State().at((x, y)).label(str(s))))
        # else:
        #     raise ValueError("layout must be 'circle' or 'line'.")

        # 2) Draw transitions i -> i+1 (wrap at end)
        for i in range(n):
            a = nodes[i]
            b = nodes[(i + 1) % n]
            ax, ay = a.center
            bx, by = b.center

            o = octant(ax, ay, bx, by)
            from_name, to_name = octant_anchor_pairs[o]

            # get the actual anchor objects by attribute (N, NE, E, SE, …)
            from_anchor = getattr(a, from_name)
            to_anchor = getattr(b, to_name)

            arc = flow.Arc2(arrow='->').at(from_anchor).to(to_anchor)
            print(f"i = {i}, state = {states[i]}, o = {o}, arc = {arc}")
            elem = d.add(arc)
            if edge_labels:
                elem.label(edge_labels[i])

            if edge_labels:
                elem.label(edge_labels[i])
    if filename:
        d.save(filename)


if __name__ == '__main__':
    # states = ['000', '001', '011', '010', '110', '111', '101', '100']
    # draw_counter_fsm(states, layout='circle', radius=3.2)


    states = ["0000", "0001", "0011", "0010", "0110",
    "1110", "1111", "1101", "0101", "0100", "1100"]
    # states = ["0", "1", "3", "7", "6", "4",
    #           "C", "D", "F", "B", "A", "8", "9"]
    draw_counter_fsm(states, layout='circle', radius=5.5,
                     filename="images/states_4_bits_students.pdf")

