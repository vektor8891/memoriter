#!/usr/bin/env python3
"""
Create a memorization summary from a passage of text.
Extracts the first letter(s) of each word to aid memorization (e.g., for Bible verses).
Supports Hungarian digraphs (cs, gy, ly, ny, sz, ty, zs). Removes verse numbers.
Keeps hyphenation and punctuation. Output can be saved to the output folder.
"""

import argparse
import re
import sys
from pathlib import Path

# Hungarian digraphs: two characters that count as one letter
HUNGARIAN_DIGRAPHS = ("cs", "gy", "ly", "ny", "sz", "ty", "zs")

# Verse number at start of line: e.g. "1 ", "2 ", "3:16 ", "1. "
VERSE_NUMBER_RE = re.compile(r"^\s*\d+(?::\d+)?[.\s]*", re.IGNORECASE)


def first_letter_or_digraph(word: str) -> str:
    """Return the first letter (or Hungarian digraph) of a word, preserving case."""
    if not word:
        return ""
    word_lower = word.lower()
    for digraph in HUNGARIAN_DIGRAPHS:
        if word_lower.startswith(digraph):
            return word[:2]
    return word[0]


def remove_verse_numbers(line: str) -> str:
    """Remove leading Bible verse numbers from a line (e.g. '1 ', '3:16 ')."""
    return VERSE_NUMBER_RE.sub("", line).strip()


def get_first_letters(
    text: str,
    preserve_structure: bool = True,
    remove_verses: bool = True,
) -> str:
    """
    Extract the first letter (or Hungarian digraph) of each word.
    Keeps hyphenation and punctuation. Optionally removes verse numbers from lines.
    """
    lines = text.strip().splitlines()
    result_lines = []

    for line in lines:
        line = line.strip()
        if remove_verses:
            line = remove_verse_numbers(line)
        if not line:
            result_lines.append("")
            continue

        # Tokenize: words (including hyphenated) and punctuation
        tokens = re.findall(r"\w+(?:-\w+)*|[^\w\s]+", line)
        parts = []

        for token in tokens:
            if re.match(r"^\w", token):
                # Word token; may be hyphenated
                segments = token.split("-")
                first_letters = [
                    first_letter_or_digraph(seg) for seg in segments if seg
                ]
                parts.append("-".join(first_letters))
            else:
                # Punctuation: keep as-is
                parts.append(token)

        # Join with spaces, but no space before punctuation (e.g. comma, period)
        no_space_before = ".!?,"
        out_parts = []
        for i, p in enumerate(parts):
            if i > 0 and p not in no_space_before:
                out_parts.append(" ")
            out_parts.append(p)
        result_lines.append("".join(out_parts))

    return "\n".join(result_lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create a memorization summary (first letters of each word) from a passage.",
        epilog="Examples:\n  %(prog)s 'In the beginning...' -o out\n  %(prog)s -f passage.txt -o out\n  %(prog)s -f verse.txt",
    )
    parser.add_argument(
        "text",
        nargs="?",
        help="Passage text. If omitted, read from -f FILE or stdin.",
    )
    parser.add_argument(
        "-f",
        "--file",
        metavar="FILE",
        dest="input_file",
        help="Read passage from FILE (e.g. -f passage.txt).",
    )
    parser.add_argument(
        "-o",
        "--output",
        metavar="NAME",
        help="Save summary to output/NAME.txt (creates output folder if needed).",
    )
    parser.add_argument(
        "--no-structure",
        action="store_true",
        help="Treat entire text as one line (single string of first letters).",
    )
    args = parser.parse_args()

    if args.input_file:
        path = Path(args.input_file)
        if not path.exists():
            raise SystemExit(f"File not found: {path}")
        text = path.read_text(encoding="utf-8")
    elif args.text:
        text = args.text
    else:
        text = sys.stdin.read()

    if not text.strip():
        raise SystemExit("No text provided.")

    summary = get_first_letters(text, preserve_structure=not args.no_structure)

    print(summary)

    if args.output:
        out_dir = Path(__file__).parent / "output"
        out_dir.mkdir(exist_ok=True)
        name = args.output if args.output.endswith(".txt") else f"{args.output}.txt"
        out_path = out_dir / name
        out_path.write_text(summary, encoding="utf-8")
        print(f"\nSaved to {out_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
