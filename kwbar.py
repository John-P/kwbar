# /// pyproject
# [run]
# requires-python = ">=3.8"
# ///
"""Print keywords as a text bar chart on stdout respecting NO_COLOR and TTY."""

import importlib.metadata
import importlib.util
import sys
from math import isfinite, isinf
from os import getenv
from shutil import get_terminal_size as term_size
from typing import SupportsFloat
from warnings import warn

__version__ = importlib.metadata.version(__name__)  # Get kwbar version string.

SF: int = 2
"""Number of significant figures to use in scientific notation value string."""
SHOW_VALS: bool = True
"""Whether to display the value as a string in a scientific notation format."""
TRUNCATE: float = 0.25
"""% of width to truncate keys after. If >1, the floor is used as max length."""
WIDTH: int = -1
"""Width of the bar chart. If <= 0, then the terminal width is used instead."""
BAR_CHARS: str = "▏▎▍▌▋▊▉█"  # Using Unicode block elements (U+2580 to U+2588).
"""Characters used to show bars. Chars 0 to -2 print for partial bar chunks."""
R: str = "\x1b[0m"
"""Escape sequence to reset all terminal formatting (foreground/background)."""
POS: str = ""
"""Escape sequence to set the foreground color when showing positive values."""
NEG: str = "" if getenv("NO_COLOR") else "\x1b[31m"  # Red.
"""Escape sequence to set the foreground color when showing negative values."""
INV: str = "\x1b[7m"
"""Escape sequence to invert/reverse the foreground/background value colors."""
WARN: bool = True
"""Whether to warn on stderr when width is too narrow to fit all the output."""
PAD: str = "  "
"""Padding characters to use for values. First char for finite, else second."""
_ASCII_: bool = False
"""Whether currently using ASCII instead of Unicode block elements to print."""


def hotdog() -> None:
    """Make a chart using hotdog emoji. Defaults to allow 2 cols per emoji."""
    global BAR_CHARS, POS, NEG, INV, R, WIDTH, SHOW_VALS  # Oh no not a global!
    BAR_CHARS, POS, NEG, INV, R, SHOW_VALS = "⅛¼⅜½⅝¾⅞🌭", "", "", "", "", False
    WIDTH = WIDTH if WIDTH > 0 else term_size()[0] // 2  # Use 2 cols for a 🌭.


def ascii() -> None:
    """Set kwbar to ASCII mode. Called when writing out to a non-TTY stdout."""
    global BAR_CHARS, POS, NEG, INV, R, PAD, _ASCII_  # More global horrors! :O
    BAR_CHARS, POS, NEG, INV, R, PAD, _ASCII_ = "X", "", "", "", "", "+X", True


# Tell kwbar to use ASCII text if stdout is not a TTY (ANSI color safe...ish?).
ascii() if not sys.stdout.isatty() else ...


def kwbar(**kwargs: SupportsFloat) -> None:
    """Keyword Bar -- Plot kwargs keys and values as floats to the terminal."""
    cols = WIDTH if WIDTH > 0 else term_size()[0]  # Get columns (fallback 80).
    # Truncate any long kwargs keys (>1/4 of the requested columns by default).
    truncate_len = int(cols * TRUNCATE) if TRUNCATE <= 1 else int(TRUNCATE)  ##
    kwargs = {  # Truncate keys longer than truncate_len, otherwise leave them.
        f"{k:>{int(TRUNCATE)}}"  # Right pad with spaces to fit TRUNCATE (> 0).
        if len(k) <= truncate_len  # Only adds padding when a key is too short.
        else f"{k[:truncate_len - 1]}…": v  # Truncate and add an ellipsis (…),
        for k, v in kwargs.items()  # for any key longer than our truncate_len.
    }  # This uses quite a bit of space but makes the output look a lot better.
    max_val = max(abs(float(v)) for v in kwargs.values())  # Get the max value.
    max_key_len = max(len(k) for k in kwargs.keys())  # Get the max key length.
    val_str_len = 7 + SF  # Format = r"[ -]\d\.\d{DP}e[+-]\d\d" = 7 + SF chars.
    # Overflow the width if truncated keys, bars, and value strings do not fit.
    cols = max(cols, max_key_len + 1 + val_str_len * (_ASCII_ != 0))  # +1 " ".
    # Find the maximum possible length of bars after the key and the pad space.
    max_bar_len = cols - max_key_len - 1 - _ASCII_  # -1 for a space after key.
    for key, val in kwargs.items():  # <---- The main loop! Where the magic is.
        bar_len = (  # Calculate the bar length, checking for: NaN, +inf, -inf.
            (abs(float(val)) / max_val) * max_bar_len  # The length of the bar,
            if isfinite(val)  # for finite floats (not NaN, inf, or -inf). Plot
            else max_bar_len * (isinf(val) or float(val) > 0)  # an inf as max,
        )  # NaN as 0, and negatives as abs(value). Negatives are also colored.
        col = POS if float(val) >= 0 else NEG  # Color negatives (eg ANSI red).
        # Print value strings which fit inside of the bar with inverted colors.
        inside = post = ""  # Value strs to be shown, inside and after the bar.
        pad = PAD[0] if isfinite(val) else PAD[1]  # Pad char to use for value.
        if bar_len >= val_str_len and SHOW_VALS:  # Print value inside the bar.
            inside = f"{val:{pad}>{val_str_len}.{SF}e}" + f"{'': <{_ASCII_:d}}"
            bar_len -= val_str_len  # Subtract the inside val str from the bar.
        elif SHOW_VALS:  # For short bars print the value stings after instead.
            post = f"{val:{pad}>{val_str_len}.{SF}e}"  # Post bar value string.
        bar = BAR_CHARS[-1] * int(bar_len)  # Build a bar string of full chars.
        if part_index := round((bar_len % 1) * len(BAR_CHARS)):  # Partial bit?
            bar += BAR_CHARS[part_index - 1]  # Add a partial char (1-indexed).
        if WARN and max_key_len + len(f" {inside}{bar}{post}") > cols:  # Oops!
            warn("Unable to fit in the requested width, overflowing!")  # Warn!
        print(f"{col}{key:>{max_key_len}} {INV}{inside}{R}{col}{bar}{post}{R}")
