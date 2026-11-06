# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

A single-script Python client (`main.py`, stdlib only — no dependencies) that sends a text prompt to a locally running **Draw Things** app via its Automatic1111-compatible HTTP API and saves the returned image.

## Running

Draw Things must be running with its HTTP API server enabled on `127.0.0.1:7860`.

```sh
python3 main.py                 # paste prompt, then Ctrl-D on an empty line
python3 main.py < prompt.txt    # prompt from file
```

There are no tests, linter, or build step.

## How it works

- `generate_image()` POSTs `{"prompt": ...}` to `/sdapi/v1/txt2img`, decodes `images[0]` (base64, optional `data:` prefix stripped), and writes `outputs/image_<timestamp>.png`.
- Only `prompt` is sent, so size, steps, sampler, seed, and model all come from whatever is currently selected in the Draw Things UI. Add fields such as `width`/`height`/`seed` to the payload to control them.
- Prompt input uses `sys.stdin.read()` (not `input()`) so multi-line prompts work.
- `OUTPUT_DIR` is an absolute path to `/Volumes/limitbreak/LocalImageAI/outputs` (external volume).

## Directories

- `outputs/` — generated images (gitignored).
- `models/` — model weights (gitignored); currently empty.
- `workflows/` — currently empty.
