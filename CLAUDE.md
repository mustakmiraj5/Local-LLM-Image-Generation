# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Makes print-ready typography posters (18×24 in, 5400×7200 px, 300 dpi). The core rule: **image models draw artwork, Pillow draws text** — models garble lettering, so quote and author text is always rendered with Pillow, never put in the image prompt.

## Setup and commands

```sh
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt   # Pillow only

.venv/bin/python main.py --quote "Keep it simple,\nstupid." --author "Kelly Johnson" --emphasis-last
.venv/bin/python main.py --quote "..." --bg-prompt "misty lake at dawn"   # AI background
.venv/bin/python image_generator.py < prompt.txt                          # plain image generation
.venv/bin/python test_poster_maker.py                                     # the only test; prints "ok"
```

`--bg-prompt` (and `image_generator.py`) need the **Draw Things** app running with its HTTP API on `127.0.0.1:7860`. Flat-colour posters don't.

## Architecture

- `main.py` — argparse CLI. Optionally calls `generate_image()` for a 768×1024 background (appends "no text" to the prompt plus a negative prompt), then `make_poster()`, and saves to `outputs/posters/`. A literal `\n` in `--quote` becomes a line break.
- `image_generator.py` — POSTs to Draw Things' A1111-compatible `/sdapi/v1/txt2img`; saves raw images to `outputs/generated/`. Payload fields left unset fall back to whatever is selected in the Draw Things UI.
- `poster_maker.py` — layout. All quote lines share one size: the largest at which the widest line fills the width inside the 10% side margins (`fit_size`). Lines are left-aligned on ink (left bearing compensated), and the quote + accent rule + author block is centred vertically using an approximate Inter cap height (0.73 em). Background images are cover-cropped with `ImageOps.fit`.
- `fonts/` — Inter v4.1 static TTFs (Light, Bold, Black) + OFL licence; loaded by weight name via `font(weight, size)`.

Paths are relative to the script directory. `outputs/` and `.venv/` are gitignored.
