# Copyright (c) 2025 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""

"""

__author__ = "Kyle Vitautas Lopin"


import heapq
from dataclasses import dataclass
from typing import Dict, List, Tuple, Callable

LogicValue = int  # 0 or 1
Time = float

@dataclass
class Gate:
    name: str
    gate_type: str           # "AND", "OR", "NOT", ...
    inputs: List[str]        # names of input signals
    output: str              # name of output signal
    delay: Time              # propagation delay


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

        # Ignore if no actual change
        if signals.get(sig_name, 0) == new_val:
            continue

        # Update signal value
        signals[sig_name] = new_val
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

    return history


gates = [
    Gate(name="G1", gate_type="AND", inputs=["A", "B"], output="X", delay=3),
    Gate(name="G2", gate_type="NOT", inputs=["X"],      output="Y", delay=2),
]

initial_signals = {
    "A": 0,
    "B": 0,
}

input_transitions = {
    "A": [(5, 1), (20, 0)],   # A=1 at t=5, A=0 at t=20
    "B": [(10, 1)],           # B=1 at t=10
}

end_time = 40

history = simulate_circuit(
    gates=gates,
    initial_signals=initial_signals,
    input_transitions=input_transitions,
    end_time=end_time,
)
