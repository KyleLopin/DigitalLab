# Copyright (c) 2025 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""

"""

__author__ = "Kyle Vitautas Lopin"

# standard libraries
import heapq
from dataclasses import dataclass
from typing import Dict, List, Tuple

# from local files
from base import draw_signals, make_clock


LogicValue = int  # 0 or 1
Time = float

@dataclass
class Gate:
    name: str
    gate_type: str           # "AND", "OR", "NOT", ...
    inputs: List[str]        # names of input signals
    output: str              # name of output signal
    delay: Time              # propagation delay


@dataclass
class DFF:
    name: str
    d: str        # input signal name
    clk: str      # clock signal name
    q: str        # output signal name
    delay: Time   # clk→Q propagation delay


def eval_gate(gate: Gate, signals: Dict[str, LogicValue]) -> LogicValue:
    ins = [signals[name] for name in gate.inputs]
    g = gate.gate_type.upper()

    if g == "AND":
        return int(all(ins))
    elif g == "OR":
        return int(any(ins))
    elif g == "NOT":
        return int(not ins[0])
    elif g == "NAND":
        return int(not all(ins))
    elif g == "NOR":
        return int(not any(ins))
    elif g == "XOR":
        return int(sum(ins) % 2)
    else:
        raise ValueError(f"Unknown gate type: {gate.gate_type}")


def simulate_circuit(
    gates: List[Gate],
    dffs: List[DFF],
    initial_signals: Dict[str, LogicValue],
    input_transitions: Dict[str, List[Tuple[Time, LogicValue]]],
    end_time: Time,
) -> Dict[str, List[Tuple[Time, LogicValue]]]:
    """
    returns: dict signal_name -> list of (time, value) transitions
    suitable for your draw_signals() function
    """
    # Copy initial signals so we can mutate
    signals = dict(initial_signals)

    # Event queue: (time, signal_name, new_value)
    event_queue: List[Tuple[Time, str, LogicValue]] = []

    # Record of transitions for plotting
    history: Dict[str, List[Tuple[Time, LogicValue]]] = {
        name: [(0, val)] for name, val in signals.items()
    }

    # Build fanout: which gates depend on a given signal
    fanout: Dict[str, List[Gate]] = {}
    for g in gates:
        for inp in g.inputs:
            fanout.setdefault(inp, []).append(g)

        # Ensure output exists in signals/history
        if g.output not in signals:
            signals[g.output] = 0
            history[g.output] = [(0, 0)]

    # --- DFF bookkeeping
    # Map clock signal -> list of DFFs triggered by that clock
    dffs_by_clk: Dict[str, List[DFF]] = {}
    last_clk: Dict[str, LogicValue] = {}  # last clock value per DFF

    for ff in dffs:
        dffs_by_clk.setdefault(ff.clk, []).append(ff)
        # ensure Q in signals/history
        if ff.q not in signals:
            signals[ff.q] = 0
            history[ff.q] = [(0, 0)]
        # initialize last clock value from current signals (default 0)
        last_clk[ff.name] = signals.get(ff.clk, 0)

    # Schedule input transitions
    for sig_name, trans_list in input_transitions.items():
        for t, v in trans_list:
            if t <= end_time:
                heapq.heappush(event_queue, (t, sig_name, v))

    # Main event loop
    while event_queue:
        time, sig_name, new_val = heapq.heappop(event_queue)
        if time > end_time:
            break

        old_val = signals.get(sig_name, 0)
        if old_val == new_val:
            continue  # no change

        # Update signal value
        signals[sig_name] = new_val
        history.setdefault(sig_name, [(0, old_val)])
        history[sig_name].append((time, new_val))

        # For each gate that uses this signal, recompute output
        for gate in fanout.get(sig_name, []):
            out_name = gate.output
            old_out = signals[out_name]
            new_out = eval_gate(gate, signals)

            if new_out != old_out:
                # Schedule output change at time + gate.delay
                event_time = time + gate.delay
                if event_time <= end_time:
                    heapq.heappush(event_queue, (event_time, out_name, new_out))

        # --- 2) DFFs that use this signal as their clock
        for ff in dffs_by_clk.get(sig_name, []):
            prev_clk = last_clk[ff.name]
            last_clk[ff.name] = new_val

            # rising edge: 0 -> 1
            if prev_clk == 0 and new_val == 1:
                q_name = ff.q
                d_val = signals.get(ff.d, 0)  # sample D at clock edge
                old_q = signals[q_name]
                if d_val != old_q:
                    event_time = time + ff.delay
                    if event_time <= end_time:
                        heapq.heappush(event_queue,
                                       (event_time, q_name, d_val))
    return history


def test_sim():
    gates = [
        Gate(name="G1", gate_type="AND", inputs=["A", "B"], output="X", delay=3),
        Gate(name="G2", gate_type="NOT", inputs=["X"], output="Y", delay=2),
    ]

    initial_signals = {
        "A": 0,
        "B": 0,
    }

    input_transitions = {
        "A": [(5, 1), (20, 0)],  # A=1 at t=5, A=0 at t=20
        "B": [(10, 1)],  # B=1 at t=10
    }

    end_time = 40

    history = simulate_circuit(
        gates=gates,
        initial_signals=initial_signals,
        input_transitions=input_transitions,
        end_time=end_time,
    )
    return history


def mealy_1(period):
    input_transitions = {
        "CLK": make_clock(period, 8, 1),
        "X": [(0, 0), (55, 1), (105, 0), (155, 1), (205, 0),
              (295, 1), (335, 0)]
    }
    gates = [
        Gate(name="G1", gate_type="NOT", inputs=["X"], output="X_bar", delay=10),
        Gate(name="G2", gate_type="OR", inputs=["X_bar", "B"], output="A+", delay=15),
        Gate(name="G3", gate_type="AND", inputs=["X", "A"], output="B+", delay=15),
    ]
    dffs = [
        DFF(name="DFF A", d="A+", clk="CLK", q="A", delay=20),
        DFF(name="DFF B", d="B+", clk="CLK", q="B", delay=20),
    ]
    initial_signals = {
        "CLK": 1,
        "X": 0,
        "X_bar": 1,
        "A": 1,
        "A+": 1
    }
    hist = simulate_circuit(
        gates=gates,
        dffs=dffs,
        initial_signals=initial_signals,
        input_transitions=input_transitions,
        end_time=425,
    )
    print(hist)
    return hist


if __name__ == '__main__':
    period = 50
    hist = mealy_1(period)
    print(hist)
    draw_signals(hist, end_time=420, x_label="Time (ps)",
                 dt=period//2, minor_ticks=10, filename="timing_diagrams.svg")

    # hist = test_sim()
    # print(hist)
    # # Pick which signals to plot
    # signals_for_plot = {
    #     name: transitions
    #     for name, transitions in hist.items()
    #     if name in ["A", "B", "X", "Y"]
    # }
    #
    # draw_signals(signals_for_plot, end_time=50, x_label="Time (ns)")
