# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Local image generation and print-ready typography posters (18×24 in, 5400×7200 px, 300 dpi). Core rule: **image models draw artwork, Pillow draws text**. Models garble lettering, so quote/author text is always rendered with Pillow and is never sent to Qwen or put in an image prompt.

## Setup and commands

```sh
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt   # Pillow only

.venv/bin/python main.py                       # interactive: asks mode, prompt, refine, ...
.venv/bin/python main.py --mode image --prompt "a fox" --refine --width 832 --height 1248
.venv/bin/python main.py --mode poster --quote "Keep it simple,\nstupid." --author "Kelly Johnson" --emphasis-last
.venv/bin/python test_poster_maker.py          # prints "ok"
.venv/bin/python test_prompt_refiner.py        # prints "ok"; needs nothing running
```

External services (stdlib `urllib`, no SDKs):
- **Draw Things** HTTP API on `127.0.0.1:7860` (A1111-compatible `/sdapi/v1/txt2img`). It is needed for image mode and AI poster backgrounds. The model is whatever is selected in the app; prompts target FLUX.
- **Ollama** on `127.0.0.1:11434` with `qwen3.5:4b` (`MODEL` constant). It is optional; on any failure `refine_prompt` returns `None` and the original prompt is used.

## Architecture

- `main.py` is the single entry point. Every option is a flag, and any flag left out is asked interactively. When stdin isn't a TTY (scripted run) nothing is asked: required flags error, `--refine` defaults off, and the refined prompt is auto-accepted. Multi-line prompts are read with `sys.stdin.read()` (Ctrl-D), and `input()` still works afterwards on a TTY. `--prompt` is the image prompt in image mode and the background prompt in poster mode (empty = flat colour).
- `prompt_refiner.py`: `refine_prompt(prompt, purpose)` calls Ollama `/api/chat` with `think: false` (this keeps it at ~6 s). `purpose="background"` adds poster rules (calm area for text, ends with "No text or lettering..."). `clean()` strips `<think>` blocks, "Prompt:" labels and wrapping quotes.
- `image_generator.py`: `generate_image(prompt, width, height, negative_prompt)` saves to `outputs/generated/`. Unset payload fields fall back to the Draw Things UI settings. Poster backgrounds request 768×1024 (3:4).
- `poster_maker.py` handles the layout. All quote lines share one size: the largest at which the widest line fills the width inside the 10% side margins (`fit_size`). Lines are left-aligned on ink (left bearing compensated), and the quote + accent rule + author block is centred vertically using an approximate Inter cap height (0.73 em). Background images are cover-cropped with `ImageOps.fit`.
- `fonts/` holds the Inter v4.1 static TTFs (Light, Bold, Black) and the OFL licence, loaded by weight name via `font(weight, size)`.

Paths are relative to the script directory. `outputs/` and `.venv/` are gitignored.
