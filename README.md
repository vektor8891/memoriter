# Memoriter

Creates a memorization summary from a passage of text by extracting the **first letter(s)** of each word. Useful for learning Bible verses or any text by heart.

## Features

- **First letter (or digraph) per word** — e.g. “In the beginning God created” → `ITBGC`
- **Hungarian support** — digraphs **cs, gy, ly, ny, sz, ty, zs** are treated as one letter (e.g. *csend* → `CS`, *szép* → `SZ`)
- **Verse numbers removed** — leading numbers like `1 ` or `3:16 ` at the start of lines are stripped
- **Hyphenation kept** — e.g. *word-one* → `W-O`
- **Punctuation kept** — commas, periods, etc. stay in the summary

## Usage

### Run script (recommended)

Edit parameters at the top of `run`, then execute:

```bash
./run
```

In `run` you can set:
- **INPUT_FILE** — path to a passage file (e.g. `passage.txt`)
- **TEXT** — passage text inline (if not using a file)
- **OUTPUT_NAME** — save summary to `output/OUTPUT_NAME.txt` (leave empty to only print)
- **NO_STRUCTURE** — set to `yes` to treat the whole text as one line

The script creates a `.venv` if missing, then runs `create_summary.py` with your parameters.

### Command line

```bash
# Read from file (recommended for longer passages)
python3 create_summary.py -f passage.txt -o my_verse
python3 create_summary.py -f verse.txt                    # print only, no save

# Text as argument, save to output folder
python3 create_summary.py "In the beginning God created the heaven and the earth." -o genesis_1_1

# With verse number (it will be removed from the summary)
python3 create_summary.py "3:16 For God so loved the world." -o john_3_16

# From stdin
echo "For God so loved the world" | python3 create_summary.py -o john_3_16
```

## Options

| Option | Description |
|--------|-------------|
| `-f`, `--file FILE` | Read passage from FILE (e.g. `-f passage.txt`) |
| `-o`, `--output NAME` | Save summary to `output/NAME.txt` (adds `.txt` if omitted) |
| `--no-structure` | Treat entire text as one line (single string of first letters) |

## Examples

| Input | Output |
|-------|--------|
| `1 In the beginning, God created.` | `I t b, G c.` |
| `3:16 For God so loved the world, that he gave his only begotten Son.` | `F G s l t w, t h g h o b S.` |
| `word-one two-three` | `w-o t-t` |

Output is printed to stdout and, when `-o NAME` is used, also saved to `output/NAME.txt`.
