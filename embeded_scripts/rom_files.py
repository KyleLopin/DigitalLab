# Copyright (c) 2025 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""
Make scripts to load into ROM of CircuitVerse for different files
"""

__author__ = "Kyle Vitautas Lopin"

def to_bcd_hex6(v: int) -> str:
    """
    Convert an 8-bit integer (0–255) to a packed 3-digit BCD string in 6-digit hex form.

    Each decimal digit (hundreds, tens, ones) is encoded as a 2-digit hex nibble:
        0  -> "0x000000"
        1  -> "0x000001"
        10 -> "0x000100"
        255-> "0x020505"

    Returns:
        str: Formatted hexadecimal string ("0xHHMMSS") suitable for EEPROM data lines
             in CircuitVerse or other ROM initialization files.
    """
    if not isinstance(v, int) and not 0 <= v <= 255:
        raise ValueError(f"Input must be between 0 and 255 inclusive.\n"
                         f"{v} is not valid input of type {type(v)}")
    h = v // 100
    t = (v // 10) % 10
    o = v % 10
    # return f"0x{h:02X}{t:02X}{o:02X}"
    return f"{(h<<8) | (t<<4) | o}"


def make_bcd_hex6(_start=0, _end=255):
    """
    Generate a list of 6-digit hexadecimal BCD strings for integers in a given range.

    Each value is converted using `to_bcd_hex6(v)`:
        0   -> "0x000000"
        1   -> "0x000001"
        10  -> "0x000100"
        255 -> "0x020505"

    Args:
        _start (int): Starting integer value (inclusive), default 0.
        _end   (int): Ending integer value (inclusive), default 255.

    Returns:
        list[str]: List of formatted hex strings in the form "0xHHTT00".

    Raises:
        ValueError: If either bound is invalid or outside 0–255.
    """
    # --- input validation ---
    if not (isinstance(_start, int) and isinstance(_end, int)):
        raise ValueError(
            f"Both _start and _end must be integers, got {_start!r} and {_end!r}"
        )
    if not (0 <= _start <= 255 and 0 <= _end <= 255):
        raise ValueError(f"Range must be between 0 and 255 inclusive: {_start=}, {_end=}")
    if _end < _start:
        raise ValueError(f"End value {_end} must be >= start value {_start}")

    # --- generate list ---
    lines = [to_bcd_hex6(v) for v in range(_start, _end + 1)]
    return lines


if __name__ == '__main__':
    # standard libraries
    import csv
    lines = make_bcd_hex6()
    print(lines)
    with open("rom_8bit_to_bcd6hex.csv", "w") as f:
        f.write(",".join(lines))

