# Copyright (c) 2025 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""

"""

__author__ = "Kyle Vitautas Lopin"

# installed libraries
import matplotlib.pyplot as plt
import numpy as np

def draw_timing_grid(t_end,
                     row_height=1.0,
                     n_rows=6,
                     column_length=5,
                     minor_ticks = None,
                     x_label=None):
    """
    Draw a blank timing-diagram grid suitable for adding signals later.

    Parameters
    ----------
    t_end : float
        Final time on the x-axis (use whatever units you like: ns, ps, cycles).
    filename : str or None, optional
        If given, save to this path (PDF/PNG/etc).
        If None, display the figure with plt.show().
    dt : float, optional
        Time resolution reserved for later signal sampling (default 5 ps = 5e-12).
        Not used yet, but kept in signature for future extension.
    row_height : float, optional
        Vertical spacing between signal rows.
    n_rows : int, optional
        Number of rows (tracks) to leave space for.
    grid_spacing : float, optional
        Spacing for major gridlines along x and y.
    """

    # Figure and axes
    fig, ax = plt.subplots(figsize=(5, (n_rows+1)*row_height))  # landscape letter

    # X/Y limits
    ax.set_xlim(0, t_end)
    # y_min = -row_height
    y_min = 0
    y_max = n_rows * row_height
    ax.set_ylim(y_min, y_max)
    print(y_min, y_max, (n_rows+1)*row_height)

    # Major grid (graph paper look)
    ax.set_xticks(np.arange(0, t_end, column_length), minor=False)
    ax.set_yticks(np.arange(0, y_max, row_height), minor=False)
    if minor_ticks:
        ax.set_xticks(np.arange(0, t_end, minor_ticks), minor=True)
        # Major grid = thick
        ax.grid(which='major', color='lightgray', linestyle='-', linewidth=1.5)

        # Minor grid = thin
        ax.grid(which='minor', color='lightgray', linestyle='-', linewidth=0.3)
    else:
        ax.grid(which='major', linestyle='-', linewidth=0.3, color='lightgrey')

    print("a: ", np.arange(0, y_max, row_height), y_max)


    # No labels / frame (clean worksheet look)
    # ax.set_xticklabels([])
    print("lll", ax.get_xticklabels())
    ax.set_xticks(np.arange(0, t_end, column_length*2))
    ax.set_yticklabels([])
    # ax.set_frame_on(False)

    # Optional: light row separators for where signals will go later
    for i in range(n_rows):
        y = i * row_height
        ax.hlines(y, 0, t_end, linestyle=':', linewidth=0.4, color='gray')
        print("y = ", y)

    if x_label is not None:
        ax.set_xlabel(x_label, fontsize=10)

    for spine in ('top', 'right'):
        ax.spines[spine].set_visible(False)

    plt.tight_layout()
    return fig, ax


def draw_signals(signals: dict, end_time=50,
                 row_height = 0.45, dt = 5, x_label="Time (ns)",
                 filename=None, start_signals ={}, **kwargs):
    print("bb", len(signals))
    fig, ax = draw_timing_grid(end_time, n_rows=len(signals),
                               row_height=row_height, column_length=dt,
                               x_label=x_label, **kwargs)

    num_signals = len(signals)
    amp = 0.6 * row_height  # height of logic 1 above base line

    for idx, (name, points) in enumerate(signals.items()):
        print(name, points)
        row_idx = num_signals - 1 - idx
        base_y = row_idx * row_height + 0.2 * row_height  # offset from actual 0

        # Label the signal on the left
        ax.text(-0.5, base_y + 0.5 * amp, name,
                ha='right', va='center')
        # print(points)
        # if not points:
        #     continue  # make blank for students
        #
        # pts = sorted(points, key=lambda p: p[0])  # incase out of order
        #
        # if pts and pts[0][0] > 0:  # assume values hold from 0 at start
        #     pts = [(0, pts[0][1])] + pts
        # print("pts", pts)

        # If no transitions but we have a start_signal: draw only that initial chunk
        if (not points) and (name in start_signals):
            t_stop, level = start_signals[name]  # (time, level)
            times = [0, t_stop]
            levels = [level, level]

            y = base_y + np.array(levels) * amp
            ax.plot(times, y, drawstyle='steps-post')
            continue  # don't extend to end_time

        # If no points and no start_signal: leave blank for students
        if not points:
            continue

        # Sort any transition points
        pts = sorted(points, key=lambda p: p[0])

        # Initial value logic
        start_val = start_signals.get(name, None)

        if not pts:
            # No transitions, but we have a starting value
            pts = [(0, start_val), (end_time, start_val)]
        else:
            # We have transitions; make sure we define value at t=0
            if pts[0][0] > 0:
                # Prefer explicit start_val if given, else assume first value
                if start_val is None:
                    start_val = pts[0][1]
                pts = [(0, start_val)] + pts
            elif start_val is not None:
                # If the first point is at t=0 but you want to override its value:
                t0, _v0 = pts[0]
                pts[0] = (t0, start_val)


        times = []
        levels = []

        # Build piecewise-constant segments
        last_t = pts[0][0]
        last_v = pts[0][1]

        for (t_i, v_i) in pts[1:]:
            # Hold last_v from last_t to t_i
            times.extend([last_t, t_i])
            levels.extend([last_v, last_v])
            last_t, last_v = t_i, v_i

        # Extend last value to end_time
        times.extend([last_t, end_time])
        levels.extend([last_v, last_v])

        # Map 0/1 to y coordinate
        levels = np.array(levels)
        y = base_y + levels * amp

        # Draw step waveform
        ax.plot(times, y, drawstyle='steps-post')

    for signal in start_signals:
        print(signal)  # how to fill in


    if filename:
        fig.savefig(filename, bbox_inches='tight')
    plt.show()


def make_clock(period: int | float,
               n_cycles: int,
               start_level: int = 1) -> list[tuple[float, int]]:
    """
    Make a clock waveform as a list of (time, level) points.

    Parameters
    ----------
    period : int or float
        Clock period in the same time units as your timing diagram.
    n_cycles : int
        Number of full clock cycles to generate.
    start_level : int, optional
        Initial level at t=0 (1 or 0). Default is 1 (start high).

    Returns
    -------
    clk : list of (time, level)
        Sequence of (time, level) transitions suitable for draw_signals().
    """
    half = period / 2
    clk = [(0, start_level)]
    level = start_level

    for i in range(n_cycles):
        # toggle at half-period
        t_mid = i * period + half
        level = 1 - level
        clk.append((t_mid, level))

        # toggle again at full period boundary
        t_end = (i + 1) * period
        level = 1 - level
        clk.append((t_end, level))

    return clk
