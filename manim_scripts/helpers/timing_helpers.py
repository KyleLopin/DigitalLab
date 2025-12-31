# Copyright (c) 2025 Kyle Lopin (Naresuan University) <kylelopin@gmail.com>

"""
Reusable timing utilities for Manim scenes.

This module provides the `TimingHelpers` mixin, which lets you drive a scene using
named *time cues* rather than hard-coded `wait()` calls sprinkled throughout your
animation code.

Cue table format
----------------
A cue table is a dict mapping string keys to either:

- a number (int/float): a single absolute time in seconds
- a list/tuple of numbers: multiple absolute times under one cue name

If the value is a list/tuple, call `wait_to(..., list_index=i)`.

Example
-------
Basic use (scene-specific cue table):

    from manim import Scene
    from timing import TimingHelpers

    TIMES_INTRO = {
        "START": 0.0,
        "SHOW_TABLE": 2.4,
        "HITS": [5.1, 6.7, 8.2],
    }

    class KMapIntro(Scene, TimingHelpers):
        def construct(self):
            # Attach cue table for this scene
            self.attach_times(TIMES_INTRO)

            # Jump to named times
            self.wait_to("START")
            self.wait_to("SHOW_TABLE")

            # If a cue is a list, specify which entry
            self.wait_to("HITS", list_index=1)

            # Relative timing helper:
            t0 = self.mark()
            # ... play some animations ...
            self.wait_since(t0, 1.5)  # ensure 1.5s elapsed since mark()

Notes
-----
- `wait_to()` waits until an *absolute* time (seconds since the scene started).
- If the cue time is in the past, `wait_to()` will wait a minimal amount (0.07s)
  so you still get a stable frame/tick and your scene doesn't stall oddly.
- `set_cue()` updates an on-screen label (bottom-left) without animation so it
  does not affect your timing.
"""

__author__ = "Kyle Vitautas Lopin"


# installed libraries
from manim import Text, UL, DL


class TimingHelpers:
    """
    Scene mixin that provides:
      - attach_times(times_dict)
      - mark(), wait_since()
      - wait_to("CUE") or wait_to("CUE", list_index=...)
    """

    def attach_times(self, times: dict, *, set_default: bool = True) -> None:
        """
        Attach a cue->time mapping to this Scene instance.

        times values may be:
          - float/int
          - list/tuple of float/int (use list_index in wait_to)

        If set_default=True, stores also in self.times for convenience.
        """
        if not isinstance(times, dict):
            raise TypeError(f"times must be dict, got {type(times).__name__}")
        self._times = times
        if set_default:
            self.times = times  # optional public alias

    def init_timing_helpers(self) -> None:
        if getattr(self, "_timing_helpers_inited", False):
            return
        self._timing_helpers_inited = True

        # If caller forgot to attach times, fail loudly *early*
        if not hasattr(self, "_times"):
            self._times = {}

        self._cue = Text("", font_size=26).to_corner(UL, buff=0.30)
        self._cue.set_opacity(0.85)
        self._cue.set_z_index(100)
        self.add(self._cue)

    def mark(self) -> float:
        return float(self.renderer.time)

    def wait_since(self, mark_time: float, duration: float) -> None:
        """Ensure duration seconds have passed since mark_time."""
        target = float(mark_time) + float(duration)
        self.wait(max(0.0, target - float(self.renderer.time)))

    def wait_to(self, time_cue: str, list_index: int | None = None, *, set_cue: bool = True) -> None:
        """Wait until absolute scene time specified by a cue name."""
        self.init_timing_helpers()

        times = getattr(self, "_times", None)
        if not isinstance(times, dict) or not times:
            raise RuntimeError(
                "No times attached. Call self.attach_times(TIMES) before using wait_to()."
            )

        if time_cue not in times:
            raise KeyError(f"Unknown time cue '{time_cue}'. Valid keys: {list(times.keys())}")

        v = times[time_cue]

        # Handle list/tuple cue times
        if isinstance(v, (list, tuple)):
            if list_index is None:
                raise ValueError(
                    f"times['{time_cue}'] is a list/tuple; pass list_index=0..{len(v) - 1}"
                )
            if not isinstance(list_index, int):
                raise TypeError(f"list_index must be int, got {type(list_index).__name__}")
            if list_index < 0 or list_index >= len(v):
                raise IndexError(
                    f"list_index {list_index} out of range for times['{time_cue}'] "
                    f"(len={len(v)}; valid 0..{len(v) - 1})"
                )
            t = float(v[list_index])
            cue_label = f"{time_cue}[{list_index}]"
        else:
            t = float(v)
            cue_label = time_cue

        if set_cue:
            self.set_cue(f"{cue_label}  @ {t:0.2f}s")

        self.wait(max(0.07, t - float(self.renderer.time)))

    def set_cue(self, text: str) -> None:
        new = Text(text, font_size=40).to_corner(DL, buff=0.80)
        new.set_opacity(0.85)
        new.set_z_index(100)
        self._cue.become(new)

# Example usage:
# from manim import Scene
# from timing import TimingHelpers
#
# TIMES_INTRO = {
#     "START": 0.0,
#     "SHOW_TABLE": 2.4,
#     "HITS": [5.1, 6.7, 8.2],
# }
#
# class KMapIntro(Scene, TimingHelpers):
#     def construct(self):
#         self.attach_times(TIMES_INTRO)   # <- no global TIMES needed anymore
#         self.wait_to("START")
#         self.wait_to("SHOW_TABLE")
#         self.wait_to("HITS", list_index=1)