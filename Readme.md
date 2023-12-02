# █ kwbar – Print Keywords as a Bar Chart

[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/charliermarsh/ruff)
[![GitMoji](https://img.shields.io/badge/gitmoji-%20😜%20😍-FFDD67.svg)](https://gitmoji.dev)
[![image](https://img.shields.io/pypi/v/kwbar.svg)](https://pypi.python.org/pypi/kwbar)
[![image](https://img.shields.io/pypi/l/kwbar.svg)](https://pypi.python.org/pypi/kwbar)
[![image](https://img.shields.io/pypi/pyversions/kwbar.svg)](https://pypi.python.org/pypi/kwbar)
[![Continuous Integration](https://github.com/John-P/kwbar/actions/workflows/ci.yml/badge.svg)](https://github.com/John-P/kwbar/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/John-P/kwbar/graph/badge.svg?token=AYTCMEYTCU)](https://codecov.io/gh/John-P/kwbar)

Easily create a bar chart with `kwbar`; pass keyword arguments that can be converted to float.

![kwbar](https://github.com/John-P/kwbar/raw/main/images/kwbar-solarized-dark.svg)

I made this for fun, but then I thought other people might actually find it useful.

## Features

`kwbar` several useful features:

- Pure Python and zero dependencies.
- Minimal implementation which can be audited in a few minutes.
- Prints the names of the passed keyword arguments.
- Plots any object that can be converted to float (SupportsFloat).
- Customizable width, but it uses the entire terminal width by default.
- Prints the values of the passed keyword arguments in scientific notation.
- Customizable significant figures.
- Shows value labels inside bars, making the output width predictable. If the bars are too small, the value labels appear outside of them.
- Handles inf and NaN values.
- Negative values are [(ANSI) colored](https://en.wikipedia.org/wiki/ANSI_escape_code#Colors) red and can be customized.
- Respects the [`NO_COLOR` environment variable](https://no-color.org).
- Has an ASCII mode, enabled on import when stdout is not TTY.
- Warns on stderr (can be disabled) if the output will have to overrun the configured width.
- Fixed output width. This is done by setting `TRUNCATE` and `WIDTH` to satisfy: `WIDTH` - `TRUNCATE` - `SF` - 17 >= 0.

## Options

`kwbar` supports the following options, which are set by modifying module variables:

```python
import kwbar

kwbar.WIDTH = -1  # Set the output width, -1 = use the terminal width.
kwbar.SF = 2  # The number of sig figs to show.
kwbar.SHOW_VAL = True  # Show values inside the bars
kwbar.TRUNCATE = 0.25  # Truncate long keys (<=1 = % of WIDTH, >1 = columns).
kwbar.BAR_CHARS = " ▏▎▍▌▋▊▉█"  # Characters to use for the bars.
kwbar.POS = ""  # ANSI escape code for positive values.
kwbar.NEG = "\x1b[31m"  # ANSI escape code for negative values.
kwbar.WARN = True  # Show a warning if the output will overrun the configured width.
kwbar.PAD = " "  # Padding characters shown before finite and non-finite values.
kwbar.BEFORE = False  # Show the value labels before the bar instead of inside.
```

## Convenience Functions

There are also a couple of functions to set multiple options at once:

### ASCII Mode

Sets `BAR_CHARS` and `PAD` to ASCII characters. Also disables all ANSI escape codes and sets `BEFORE` true.

```python
import kwbar
kwbar.WIDTH = 50
kwbar.ascii()
kwbar.kwbar(one=1, two=2, three=3, four=4)
```

```plain
  one +1.00e+00 XXXXXXXX
  two +2.00e+00 XXXXXXXXXXXXXXXXX
three +3.00e+00 XXXXXXXXXXXXXXXXXXXXXXXXX
 four +4.00e+00 XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

### Hotdog Mode

```python
import kwbar
kwbar.WIDTH = 33
kwbar.hotdog()
kwbar.kwbar(one=1, two=2, three=3, four=4)
```

```plain
  one 🌭🌭🌭🌭🌭🌭¾
  two 🌭🌭🌭🌭🌭🌭🌭🌭🌭🌭🌭🌭🌭½
three 🌭🌭🌭🌭🌭🌭🌭🌭🌭🌭🌭🌭🌭🌭🌭🌭🌭🌭🌭🌭¼
 four 🌭🌭🌭🌭🌭🌭🌭🌭🌭🌭🌭🌭🌭🌭🌭🌭🌭🌭🌭🌭🌭🌭🌭🌭🌭🌭🌭
```

## How do I...?

### Reset All Options

```python
import kwbar

kwbar.ascii()

# Reset to defaults.
import importlib

importlib.reload(kwbar)
```

### Use Keys That Are Not Valid Python Keywords

```python
import kwbar

kwbar.ascii()
kwbar.kwbar(**{"one": 1, "-2": -2, "pi": 3.14})
```

```plain
one +1.00e+00 XXXXXX
 -2 -2.00e+00 XXXXXXXXXXXX
 pi +3.14e+00 XXXXXXXXXXXXXXXXXXX
```

### Print Dogs Instead of Hotdogs

```python
import kwbar
kwbar.hotdog()
kwbar.BAR_CHARS = kwbar.BAR_CHARS[:-1] + "🐶" # Replace the last character.
kwbar.kwbar(one=1, two=2, pi=3.14)
```

```plain
one 🐶🐶🐶🐶🐶🐶🐶🐶🐶¼
two 🐶🐶🐶🐶🐶🐶🐶🐶🐶🐶🐶🐶🐶🐶🐶🐶🐶🐶½
 pi 🐶🐶🐶🐶🐶🐶🐶🐶🐶🐶🐶🐶🐶🐶🐶🐶🐶🐶🐶🐶🐶🐶🐶🐶🐶🐶🐶🐶🐶
```

## Themes

Just some ideas for how you could customize the output.

### Lines

```python
import kwbar
kwbar.hotdog()
kwbar.BAR_CHARS = "╸━"
```

![Red and blue lines in Solarized Dark colorscheme](https://github.com/John-P/kwbar/raw/main/images/images/lines-solarized-dark.svg)

### Blue Red Lines

```python
import kwbar
kwbar.hotdog()
kwbar.BAR_CHARS = "╸━"
kwbar.POS = "\x1b[34m"
kwbar.NEG = "\x1b[31m"
```

![Red and blue lines in Solarized Dark colorscheme](https://github.com/John-P/kwbar/raw/main/images/images/rb-lines-solarized-dark.svg)

### Slices

```python
import kwbar
kwbar.hotdog()
kwbar.BAR_CHARS = "◔◑◕●"
```

![Slices in Solarized Dark colorscheme](https://github.com/John-P/kwbar/raw/main/images/images/slices-solarized-dark.svg)

### Quater Tally

```python
import kwbar
kwbar.hotdog()
kwbar.BAR_CHARS = " ¼½¾1"
```

![Quater tally in Solarized Dark colorscheme](https://github.com/John-P/kwbar/raw/main/images/images/quater-tally-solarized-dark.svg)

### Eighths

```python
kwbar.hotdog()
kwbar.BAR_CHARS = " ⅛¼⅜½⅝¾⅞1"
```

![Eighths in Solarized Dark colorscheme](https://github.com/John-P/kwbar/raw/main/images/images/eighths-solarized-dark.svg)

### Hatching

```python
kwbar.hotdog()
kwbar.BAR_CHARS = "🥚🐣🐥"
```

![Hatching in Solarized Dark colorscheme](https://github.com/John-P/kwbar/raw/main/images/images/hatching-solarized-dark.svg)
