# oklabconv

A command-line converter between sRGB hex colors and OKLab.

OKLab is the perceptually uniform color space behind CSS Color 4's
`oklab()` and `oklch()` functions. Unlike raw RGB, equal steps in OKLab
correspond to roughly equal steps in perceived color, which makes it a
much better space for generating gradients, tinting/shading a palette,
or measuring how different two colors look. Design tools increasingly
expose it directly, but if you just have a list of hex codes and need
their OKLab coordinates (or the other way around), this does that
conversion without pulling in a graphics library.

## Usage

Convert hex to OKLab:

```
$ echo "#ff0000" | python -m oklabconv --to oklab
oklab(0.6280 0.2249 0.1258)
```

Convert OKLab back to hex:

```
$ echo "oklab(0.6280 0.2249 0.1258)" | python -m oklabconv --to srgb
#ff0000
```

Convert hex to OKLCH, the polar (lightness/chroma/hue) form of OKLab
used by CSS Color 4's `oklch()`:

```
$ echo "#ff0000" | python -m oklabconv --to oklch
oklch(0.6280 0.2576 29.23)
```

`--to srgb` accepts either `oklab(...)` or `oklch(...)` lines, and
picks the right inverse conversion automatically:

```
$ echo "oklch(0.6280 0.2576 29.23)" | python -m oklabconv --to srgb
#ff0000
```

Read from one or more files instead of stdin, one color per line:

```
$ cat palette.txt
#000000
#ffffff
#3366ff

$ python -m oklabconv --to oklab palette.txt
oklab(0.0000 0.0000 0.0000)
oklab(1.0000 0.0000 0.0000)
oklab(0.5726 -0.0190 -0.2330)
```

A path of `-` means stdin, so you can mix piped input with files:

```
$ cat extra.txt | python -m oklabconv --to oklab palette.txt -
```

Lines that fail to parse are reported on stderr and skipped, rather
than aborting the whole run.

## Input formats

- `--to oklab` and `--to oklch` expect sRGB hex colors, with or
  without a leading `#`, in either 3-digit (`#f0a`) or 6-digit
  (`#ff00aa`) form.
- `--to srgb` expects an `oklab(L a b)` or `oklch(L C H)` line, or
  three bare numbers separated by spaces or commas (bare numbers are
  read as OKLab).

## Running tests

```
$ python -m unittest discover
```

## Status

Early. The core sRGB <-> OKLab math is implemented and matches the
reference values published alongside the OKLab color space, and is
covered by unit tests. OKLCH (polar OKLab) is supported. Not yet
covered: gamut clipping options.

## License

MIT, see LICENSE.
