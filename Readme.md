# █ kwbar – Print Keywords as a Bar Chart

Easily create a bar chart with `kwbar`; pass keyword arguments that can be converted to float.

![kwbar](kwbar.png)

## Features

`kwbar` several useful features:

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
```

There are also a couple of functions to set multiple options at once:

```python
>>> import kwbar
>>> kwbar.WIDTH = 50
>>> kwbar.ascii()
>>> kwbar.kwbar(one=1, two=2, three=3, four=4)
  one +1.00e+00XX
  two +2.00e+00XXXXXXXXXXXXX
three +3.00e+00XXXXXXXXXXXXXXXXXXXXXXXX
 four +4.00e+00XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

Hotdog mode:

````python
>>> import kwbar
>>> kwbar.WIDTH = 33
>>> kwbar.hotdog()
>>> kwbar.kwbar(one=1, two=2, three=3, four=4)
 one 🌭🌭🌭🌭🌭🌭🌭🌭🌭
 two 🌭🌭🌭🌭🌭🌭🌭🌭🌭🌭🌭🌭🌭🌭🌭🌭🌭¾
  pi 🌭🌭🌭🌭🌭🌭🌭🌭🌭🌭🌭🌭🌭🌭🌭🌭🌭🌭🌭🌭🌭🌭🌭🌭🌭🌭🌭🌭
 neg 🌭🌭🌭🌭🌭🌭🌭🌭🌭
half 🌭🌭🌭🌭¼
 nan
````
