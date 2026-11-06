# LocalImageAI

Generates images and print-ready typography posters (18×24 in, 5400×7200 px, 300 dpi) on your Mac, entirely locally.

- **Images** are made by the [Draw Things](https://drawthings.ai) app.
- **Prompts** can be improved automatically by a local Qwen model running in [Ollama](https://ollama.com).
- **Poster text** is drawn by Python (Pillow), so your quote and author always come out exactly as you typed them.

![Example poster: "Keep it simple, stupid." — Kelly Johnson](docs/example.png)

## Setup

You need Python 3.10 or newer.

```sh
cd LocalImageAI
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

The Inter fonts are already included in `fonts/`. The rest depends on what you make:

| You want to… | You need |
| --- | --- |
| Generate an image, or a poster with an AI background | Draw Things open, with its HTTP API server on port **7860**. Use a FLUX model; the refined prompts are written for it. |
| Have Qwen improve your prompt | Ollama running, with the model downloaded: `ollama pull qwen3.5:4b` |
| Make a poster on a flat colour | Nothing else |

## Usage

Start the app and answer its questions:

```sh
.venv/bin/python main.py
```

```
What do you want to make? [image/poster]: image
Prompt (paste, then Ctrl-D on an empty line):
a fox in snow
Refine the prompt with Qwen? [Y/n]: y
Asking Qwen to refine the prompt...

Refined prompt:
  A solitary red fox crouches low in a field of fresh, powdery snow, ...

[U]se it / use [o]riginal / [r]etry: u
```

To finish a prompt, press **Ctrl-D** on an empty line. Prompts can span several lines.

When Qwen shows the refined prompt, you can:

- **use it**: press Enter or **u**
- **use your original prompt instead**: press **o**
- **ask for another version**: press **r**

If Ollama isn't running, the app says so and uses your prompt unchanged.

Finished files go to:

- `outputs/generated/`: images from Draw Things
- `outputs/posters/`: finished posters

### Skipping the questions

Any option you give on the command line skips that question:

```sh
# Image, refined by Qwen, at a set size
.venv/bin/python main.py --mode image --prompt "a fox in snow" --refine --width 832 --height 1248

# Poster on a flat colour
.venv/bin/python main.py --mode poster --quote "Keep it simple,\nstupid." --author "Kelly Johnson" --emphasis-last

# Poster on an AI background
.venv/bin/python main.py --mode poster --quote "Stay curious." --author "Unknown" \
  --prompt "misty mountain lake at dawn" --refine --text-color "#FFFFFF" --author-color "#FFFFFF"
```

If you run it without a terminal (for example from another script), it asks nothing. It uses the defaults, does not refine unless you pass `--refine`, and stops with an error if `--mode`, `--prompt` or `--quote` is missing.

### Options

| Option | Mode | Default | What it does |
| --- | --- | --- | --- |
| `--mode image` / `--mode poster` | both | asked | What to make. |
| `--prompt` | both | asked | The image prompt. In poster mode, it's the background prompt; leave it out for a flat colour. |
| `--refine` / `--no-refine` | both | asked | Whether Qwen improves the prompt. |
| `--width`, `--height` | image | Draw Things' setting | Image size in multiples of 64, e.g. 832×1248 for a 2:3 portrait. Pass both or neither. |
| `--quote` | poster | asked | The quote. Type `\n` for a new line. |
| `--author` | poster | asked | Shown as "— Author" under the quote. |
| `--emphasis-last` | poster | asked | Sets the last line in a heavier weight. |
| `--bg` | poster | `#F2EBDD` (cream) | Background colour when there's no prompt. |
| `--text-color` | poster | `#252525` (charcoal) | Quote colour. |
| `--author-color` | poster | `#A66B52` (terracotta) | Colour of the author and the thin accent line. |

Run `.venv/bin/python main.py --help` to see the same list in your terminal.

### Poster notes

- **Only your background prompt goes to Qwen.** Your quote and author are never sent, so they can't be changed.
- **The quote fills the poster's width.** It's sized automatically and drawn exactly as you type it, so add your own quotation marks if you want them.
- **Text colour doesn't adjust to an AI background.** Pick `--text-color` and `--author-color` to stand out against the image.

## Tests

```sh
.venv/bin/python test_poster_maker.py    # prints "ok"
.venv/bin/python test_prompt_refiner.py  # prints "ok" (the "Qwen unavailable" line is expected)
```
