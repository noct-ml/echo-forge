#!/usr/bin/env python3
# ╔══════════════════════════════════════════════════════════════════════════╗
# ║                 EchoForge v1.1.7 — "Echo Signed" Update                  ║
# ║         "Forging echoes into clarity — from chat to art."                ║
# ║                                                                          ║
# ║  Changes in v1.1.7:                                                      ║
# ║    • Fixes Markdown output for <pre><code> blocks (fenced + indent-safe) ║
# ║    • Preserves indentation inside extracted code blocks                  ║
# ║    • Standalone artifact; no behavior change to JSONL output             ║

import re
import sys
import html
import json
import textwrap
import unicodedata as ud
from argparse import ArgumentParser
from pathlib import Path

VERSION = "1.1.7"
PROJECT_URL = "https://github.com/noct-ml/echo-forge"

TAG_BLOCKS_RE = re.compile(
    r"<!--.*?-->|<script\b[^>]*>.*?</script>|<style\b[^>]*>.*?</style>",
    flags=re.IGNORECASE | re.DOTALL,
)
TAG_RE = re.compile(r"<[^>]+>")

# --- <pre><code> extraction (preserve indentation) ---
PRE_CODE_RE = re.compile(r"(?is)<pre\b[^>]*>\s*<code\b[^>]*>(.*?)</code>\s*</pre>")
CODE_MARKER_PREFIX = "__ECHOFORGE_CODEBLOCK_"
CODE_MARKER_RE = re.compile(r"__ECHOFORGE_CODEBLOCK_(\d+)__")
BREAKERS_RE = re.compile(
    r"</?(?:p|br|li|div|h[1-6]|section|article|blockquote|tr|th|td)\b[^>]*>",
    flags=re.IGNORECASE,
)
ROLE_BLOCK_RE = re.compile(
    r'data-message-author-role="(user|assistant)".*?(?=data-message-author-role="(?:user|assistant)"|$)',
    flags=re.DOTALL | re.IGNORECASE,
)

# ---- Emoji helpers (no external deps) ----
def is_emoji(ch: str) -> bool:
    cp = ord(ch)
    return (
        0x1F600 <= cp <= 0x1F64F
        or 0x1F300 <= cp <= 0x1F5FF
        or 0x1F680 <= cp <= 0x1F6FF
        or 0x1F700 <= cp <= 0x1F77F
        or 0x1F780 <= cp <= 0x1F7FF
        or 0x1F800 <= cp <= 0x1F8FF
        or 0x1F900 <= cp <= 0x1F9FF
        or 0x1FA70 <= cp <= 0x1FAFF
        or 0x2600  <= cp <= 0x26FF
        or 0x2700  <= cp <= 0x27BF
        or 0x1F1E6 <= cp <= 0x1F1FF
        or 0x1F3FB <= cp <= 0x1F3FF
    )

_EMOJI_JOINERS = {0x200D, 0xFE0E, 0xFE0F, 0x20E3}
_EXTRA_KEEP = {"\u2192", "\u2190", "\u2194", "\u21A0", "\u21A9", "\u21D2", "\u21D4", "–", "—", "―"}
_SO_MATHY = {"°", "‰", "‱"}

def is_allowed_char(ch: str) -> bool:
    if ch in (" ", "\t", "\n", "\r"):
        return True
    cp = ord(ch)
    if ch in _EXTRA_KEEP:
        return True
    if cp in _EMOJI_JOINERS or is_emoji(ch):
        return True
    cat = ud.category(ch)
    if cat[0] in ("L", "N", "P"):
        return True
    if cat == "Zs":
        return True
    if cat in ("Sm", "Sc"):
        return True
    if ch in _SO_MATHY:
        return True
    return False



def _collapse_ws_preserve_indent(s: str) -> str:
    """
    Collapse runs of horizontal whitespace WITHOUT destroying leading indentation.
    This helps preserve Python/block indenting for code-like lines that are not
    wrapped in <pre><code> in the source HTML.
    """
    out_lines = []
    for ln in s.splitlines():
        m = re.match(r'^([ \t]+)(.*)$', ln)
        if m:
            lead, rest = m.group(1), m.group(2)
            rest = re.sub(r"[ \t\r\f\v]+", " ", rest)
            out_lines.append(lead + rest)
        else:
            out_lines.append(re.sub(r"[ \t\r\f\v]+", " ", ln))
    return "\n".join(out_lines)


def clean_plain_text(s: str) -> str:
    """
    Convert HTML-ish transcript fragments into normalized plain text while
    preserving indentation inside code blocks.

    - Extracts <pre><code>...</code></pre> blocks into fenced Markdown code blocks.
    - Does NOT collapse spaces/tabs inside those code blocks.
    - Cleans remaining tags and normalizes whitespace outside code.
    """
    # 1) Extract <pre><code> blocks first (before tag-stripping)
    code_blocks: list[str] = []

    def _stash_code(m: re.Match) -> str:
        inner = m.group(1)
        # Drop any nested tags used for syntax highlighting; keep raw text
        inner = TAG_RE.sub("", inner)
        inner = html.unescape(inner)
        inner = ud.normalize("NFC", inner)
        # Normalize newlines, keep indentation/tabs intact
        inner = inner.replace("\r\n", "\n").replace("\r", "\n")
        # Strip only outer blank lines
        inner = inner.strip("\n")
        code_blocks.append(inner)
        return f"\n{CODE_MARKER_PREFIX}{len(code_blocks)-1}__\n"

    s = PRE_CODE_RE.sub(_stash_code, s)

    # 2) Regular HTML cleanup outside code
    s = BREAKERS_RE.sub("\n", s)
    s = TAG_BLOCKS_RE.sub("", s)
    s = TAG_RE.sub("", s)
    s = html.unescape(s)
    s = ud.normalize("NFC", s)
    s = re.sub(r"\b(?:div|span|section|article|header|footer|main|aside)\b", " ", s, flags=re.IGNORECASE)
    s = "".join(ch if is_allowed_char(ch) else " " for ch in s)
    s = _collapse_ws_preserve_indent(s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    s = s.strip()

    # 3) Re-insert code blocks as fenced Markdown
    def _unstash(m: re.Match) -> str:
        i = int(m.group(1))
        if i < 0 or i >= len(code_blocks):
            return m.group(0)
        code = code_blocks[i]
        return f"```\n{code}\n```"

    s = CODE_MARKER_RE.sub(_unstash, s)
    return s.strip()

_LANGS = [
    "kotlin","sql","scss","pgsql","bash","vbnet","python","py","javascript","js","typescript","ts",
    "html","css","json","xml","yaml","yml","toml","ini","go","rust","c","cpp","java","powershell","ps1",
    "sh","zsh","dockerfile","makefile","perl","r","lua","swift","php","objc","objective-c"
]
_LANGS_RX = "|".join(re.escape(x) for x in _LANGS)
CODE_OPEN_RE = re.compile(rf"(?mi)^((?:{_LANGS_RX}))\s*\n+Copy code\s*\n")
BOUNDARY_RE = re.compile(
    rf"""(?mx)
    ^(?=(?:{_LANGS_RX})\s*$) |       # another language header
    ^(?=---\s*\d+\s*\[) |            # transcript marker
    ^(?=You said:) |                 # speaker artifact
    ^(?=ChatGPT said:) |             # speaker artifact
    ^(?=</?details>) |               # HTML <details> tags
    ^(?=\s*\#{1,6}\s) |              # markdown heading (escaped # for verbose mode)
    ^(?=\s*(?:[-*+]|\d+\.)\s) |      # list bullets / numbered lists
    ^(?=\s*Quick extras?:) |         # prose marker like "Quick extras:"
    ^(?=```) |                       # next code fence
    \Z                               # end of file
    """
)

def apply_code_markdown(text: str) -> str:
    out = []
    i = 0
    while True:
        m = CODE_OPEN_RE.search(text, i)
        if not m:
            out.append(text[i:])
            break
        out.append(text[i:m.start()])
        lang = m.group(1)
        start = m.end()
        b = BOUNDARY_RE.search(text, start)
        end = b.start() if b else len(text)
        code_payload = text[start:end].rstrip("\n")
        out.append(f"```{lang}\n{code_payload}\n```\n")
        i = end
    return "".join(out)

# --- Anchors ---
def _md_anchor(label: str) -> str:
    a = label.lower()
    a = a.replace('[', '').replace(']', '')
    a = re.sub(r'[^a-z0-9\s\-]+', '', a)
    a = re.sub(r'\s+', '-', a).strip('-')
    return a

SAME_FILE_ANCHOR_RE = re.compile(r'\[([^\]]+)\]\(#([^)]+)\)')
def rewrite_samefile_heading_links_to_obsidian(s: str) -> str:
    def repl(m):
        text, head = m.group(1), m.group(2)
        return f"[[#{head}|{text}]]"
    return SAME_FILE_ANCHOR_RE.sub(repl, s)

# --- Wrapping & code collapse ---
def _wrap_non_code(text: str, width: int) -> str:
    if width <= 0:
        return text
    parts = re.split(r'(```.*?```)', text, flags=re.DOTALL)
    out = []
    for i, part in enumerate(parts):
        if i % 2 == 1 and part.startswith('```'):
            out.append(part)
        else:
            paras = part.split('\n\n')
            wrapped_paras = []
            for para in paras:
                lines = para.splitlines()
                joined = []
                for line in lines:
                    if re.match(r'^\s*([-*+]|\d+\.)\s', line):
                        prefix = re.match(r'^(\s*(?:[-*+]|\d+\.)\s)', line).group(1)
                        body = line[len(prefix):]
                        wrapped = textwrap.fill(body, width=width, subsequent_indent=' ' * len(prefix))
                        joined.append(prefix + wrapped if wrapped else prefix)
                    else:
                        joined.append(line)
                para_text = '\n'.join(joined)
                wrapped = textwrap.fill(para_text, width=width)
                wrapped_paras.append(wrapped)
            out.append('\n\n'.join(wrapped_paras))
    return ''.join(out)

def _collapse_long_code(text: str, threshold_lines: int = 14) -> str:
    def repl(m):
        fence = m.group(1)
        lines = fence.strip('\n').split('\n')
        if len(lines) <= 1:
            return fence
        lang_line = lines[0]
        content_lines = lines[1:]
        if len(content_lines) >= threshold_lines:
            lang = lang_line[3:].strip()
            summary = f"View {len(content_lines)} lines{(' of ' + lang) if lang else ''}"
            return f"<details>\n<summary>{summary}</summary>\n\n{fence}\n</details>\n"
        return fence
    return re.sub(r'(```[^\n]*\n.*?```)', repl, text, flags=re.DOTALL)

# --- Remove label artifacts ---
LABEL_JUNK_RE = re.compile(r'(?mi)^(?:You said:|ChatGPT said:)\s*(?:<\s*)?$')
LONE_LEFT_RE = re.compile(r'(?m)^\s*<\s*$')
def strip_label_artifacts(s: str) -> str:
    s = LABEL_JUNK_RE.sub('', s)
    s = LONE_LEFT_RE.sub('', s)
    s = re.sub(r'\n{3,}', '\n\n', s)
    return s.strip()

def render_pretty_md(blocks, user_label: str, max_width: int, toc_depth: int = 0,
                     title: str = "Chat Transcript", theme: str = "light",
                     obsidian_links: bool = False, signature: bool = True) -> str:
    md = []

    # Theme or front matter
    if theme == "dark":
        md.append('<style>\n'
                  'body { background-color: #0d1117; color: #c9d1d9; }\n'
                  'code, pre { background-color: #161b22; color: #58a6ff; }\n'
                  'a { color: #58a6ff; }\n'
                  'h1, h2, h3, h4 { color: #e6edf3; }\n'
                  'details > summary { cursor: pointer; }\n'
                  '</style>\n')
    elif theme == "auto":
        md.append('<style>\n'
                  '@media (prefers-color-scheme: dark) {\n'
                  '  body { background-color: #0d1117; color: #c9d1d9; }\n'
                  '  code, pre { background-color: #161b22; color: #58a6ff; }\n'
                  '  a { color: #58a6ff; }\n'
                  '  h1, h2, h3, h4 { color: #e6edf3; }\n'
                  '  details > summary { cursor: pointer; }\n'
                  '}\n'
                  '</style>\n')
    elif theme == "obsidian":
        md.append("---\ncssclass: dark-theme\n---\n")

    # Signature (HTML comment at top; footer comes later)
    md.append(f"<!-- Generated by EchoForge v{VERSION} -->\n")

    # Title
    md.append(f"# {title}\n")

    # Only render TOC if requested (>0)
    if toc_depth and toc_depth > 0:
        md.append("## Table of Contents\n")

        def _mk_toc_link(label: str) -> str:
            if theme == "obsidian":
                return f"[[#{label}|{label}]]"
            else:
                return f"[{label}](#{_md_anchor(label)})"

        toc_lines = []
        if toc_depth >= 1:
            toc_lines.append(f"- {_mk_toc_link(title)}")
        if toc_depth >= 2:
            toc_lines.append(f"- {_mk_toc_link('Turns')}")
        if toc_depth >= 3:
            for i, (role, _txt) in enumerate(blocks, 1):
                label = user_label if (role == "user" and user_label) else ("ChatGPT" if role == "assistant" else role.title())
                head = f"Turn {i:03d} — {label}"
                toc_lines.append(f"  - {_mk_toc_link(head)}")
        md.extend(toc_lines)
        md.append("")

    if toc_depth and toc_depth >= 2:
        md.append("## Turns")
        md.append("")

    # Body
    for i, (role, txt) in enumerate(blocks, 1):
        label = user_label if (role == "user" and user_label) else ("ChatGPT" if role == "assistant" else role.title())
        head = f"### Turn {i:03d} — {label}"
        md.append(head)
        md.append("")
        txt = strip_label_artifacts(txt)
        if obsidian_links:
            txt = rewrite_samefile_heading_links_to_obsidian(txt)
        if max_width and max_width > 0:
            txt = _wrap_non_code(txt, width=max_width)
        md.append(txt)
        md.append("")

    out = '\n'.join(md).strip() + '\n'
    out = _collapse_long_code(out, threshold_lines=14)

    # Footer signature (Markdown only; theme-friendly via blockquote)
    if signature:
        out += "\n---\n> Generated by [EchoForge v{ver}]({url}) — \"Forging echoes into clarity.\"\n".format(
            ver=VERSION, url=PROJECT_URL
        )

    return out

def extract_speaker_blocks(raw_html: str):
    matches = list(ROLE_BLOCK_RE.finditer(raw_html))
    if not matches:
        return [("unknown", clean_plain_text(raw_html))]
    blocks = []
    for m in matches:
        role = m.group(1).lower()
        chunk_html = re.sub(r'^[^>]*>', '', m.group(0), count=1)
        chunk_html = re.sub(r'\s*\b(?:data-[^=]+|class|dir|id|style|aria-[^=]+)="[^"]*"', '', chunk_html)
        chunk_text = clean_plain_text(chunk_html)
        if chunk_text.strip():
            blocks.append((role, chunk_text.strip()))
    return blocks

def _should_treat_as_markdown(output_path: str, pretty_md: bool) -> bool:
    # Pretty MD is always markdown. Otherwise, rely on filename extension.
    if pretty_md:
        return True
    return str(output_path).lower().endswith(".md")

def extract_text_only(input_file: str, output_file: str, by_speaker: bool, jsonl: bool,
                      user_label: str, markdown: bool, pretty_md: bool,
                      max_width: int, toc_depth: int, title: str, theme: str,
                      obsidian_links: bool, no_toc: bool, no_signature: bool):
    with open(input_file, "r", encoding="utf-8", errors="replace") as f:
        raw = f.read()

    # Honor flags
    if no_toc:
        toc_depth = 0
    add_signature = not no_signature

    if by_speaker:
        blocks = extract_speaker_blocks(raw)
        if jsonl:
            with open(output_file, "w", encoding="utf-8") as out:
                for role, text in blocks:
                    if markdown:
                        text = apply_code_markdown(text)
                    text = strip_label_artifacts(text)
                    if obsidian_links:
                        text = rewrite_samefile_heading_links_to_obsidian(text)
                    label = (user_label if (role == "user" and user_label) else ("ChatGPT" if role == "assistant" else role.title()))
                    out.write(json.dumps({"role": label, "text": text}, ensure_ascii=False) + "\n")
        else:
            if pretty_md:
                proc_blocks = []
                for role, text in blocks:
                    if markdown:
                        text = apply_code_markdown(text)
                    proc_blocks.append((role, text))
                doc = render_pretty_md(proc_blocks, user_label=user_label, max_width=max_width,
                                       toc_depth=toc_depth, title=title, theme=theme,
                                       obsidian_links=obsidian_links, signature=add_signature)
                with open(output_file, "w", encoding="utf-8") as out:
                    out.write(doc)
            else:
                with open(output_file, "w", encoding="utf-8") as out:
                    for i, (role, text) in enumerate(blocks, 1):
                        if markdown:
                            text = apply_code_markdown(text)
                        text = strip_label_artifacts(text)
                        if obsidian_links:
                            text = rewrite_samefile_heading_links_to_obsidian(text)
                        label = (user_label if (role == "user" and user_label) else ("ChatGPT" if role == "assistant" else role.title()))
                        if max_width and max_width > 0:
                            text = _wrap_non_code(text, width=max_width)
                        out.write(f"--- {i:03d} [{label}] ---\n{text}\n\n")
                # Append footer signature for Markdown outputs
                if add_signature and _should_treat_as_markdown(output_file, pretty_md=False):
                    with open(output_file, "a", encoding="utf-8") as out:
                        out.write("\n---\n> Generated by [EchoForge v{ver}]({url}) — \"Forging echoes into clarity.\"\n".format(
                            ver=VERSION, url=PROJECT_URL
                        ))
    else:
        cleaned = clean_plain_text(raw)
        if markdown:
            cleaned = apply_code_markdown(cleaned)
        cleaned = strip_label_artifacts(cleaned)
        if obsidian_links:
            cleaned = rewrite_samefile_heading_links_to_obsidian(cleaned)
        if pretty_md:
            blocks = [("unknown", cleaned)]
            doc = render_pretty_md(blocks, user_label=user_label, max_width=max_width,
                                   toc_depth=toc_depth, title=title, theme=theme,
                                   obsidian_links=obsidian_links, signature=add_signature)
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(doc)
        else:
            if max_width and max_width > 0:
                cleaned = _wrap_non_code(cleaned, width=max_width)
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(cleaned)
            # Append footer signature for Markdown outputs
            if add_signature and _should_treat_as_markdown(output_file, pretty_md=False):
                with open(output_file, "a", encoding="utf-8") as f:
                    f.write("\n---\n> Generated by [EchoForge v{ver}]({url}) — \"Forging echoes into clarity.\"\n".format(
                        ver=VERSION, url=PROJECT_URL
                    ))

def parse_args(argv):
    ap = ArgumentParser(description="EchoForge — Forging chat echoes into clean text or polished Markdown.")
    ap.add_argument("input_file", help="Path to saved .html (or cleaned text) file")
    ap.add_argument("output_file", help="Destination file")
    ap.add_argument("--by-speaker", action="store_true", help="Split into user/ChatGPT turns")
    ap.add_argument("--jsonl", action="store_true", help="Output JSONL format (with --by-speaker)")
    ap.add_argument("--user-label", default="", help='Custom label for the "user" role (e.g., "James")')
    ap.add_argument("--no-markdown", action="store_true", help="Disable Markdown code fence conversion")
    ap.add_argument("--pretty-md", action="store_true", help="Output a Markdown doc with headings/TOC; best with --by-speaker")
    ap.add_argument("--max-width", type=int, default=0, help="Soft-wrap non-code paragraphs to this width (0 = no wrap)")
    ap.add_argument("--toc-depth", type=int, default=0, help="TOC depth (0=off, 1=title, 2=+Turns, 3=+per-turn). Default 0")
    ap.add_argument("--title", type=str, default="Chat Transcript", help="Set custom Markdown document title")
    ap.add_argument("--theme", choices=["light", "dark", "auto", "obsidian"], default="light", help="Markdown theme style")
    ap.add_argument("--obsidian-links", action="store_true", help="Rewrite same-file heading links to [[#Heading|text]]")
    ap.add_argument("--no-toc", action="store_true", help="Suppress Table of Contents entirely (redundant when toc_depth=0)")
    ap.add_argument("--no-signature", action="store_true", help="Do not append the Markdown footer signature")
    return ap.parse_args(argv)

if __name__ == "__main__":
    args = parse_args(sys.argv[1:])
    try:
        extract_text_only(
            args.input_file,
            args.output_file,
            args.by_speaker,
            args.jsonl,
            args.user_label,
            markdown=(not args.no_markdown),
            pretty_md=args.pretty_md,
            max_width=args.max_width,
            toc_depth=args.toc_depth,
            title=args.title,
            theme=args.theme,
            obsidian_links=args.obsidian_links,
            no_toc=args.no_toc,
            no_signature=args.no_signature,
        )
        print(f"[+] EchoForge v{VERSION} wrote: {args.output_file}")
    except Exception as e:
        print(f"[!] EchoForge v{VERSION} error: {e}")
        sys.exit(1)
