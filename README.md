# 🜂 EchoForge  
*“Forging echoes into clarity.”*  
> A lightweight, offline converter for ChatGPT HTML exports → structured Markdown or JSONL.

---

## 📘 Overview

**EchoForge** transforms your saved ChatGPT conversations (“Save Page As…” HTML) into readable, organized Markdown or JSONL.  

It’s local, private, and elegant — no API keys, no cloud dependencies.  
Just your words, your way.  

🜄 *Every echo deserves to be reforged.*

---

## 🧩 Core Features

| Feature | Description |
|----------|--------------|
| **HTML Purification** | Removes scripts, invisible elements, and UI clutter — leaving only text, code, and structure. |
| **Speaker Separation** | Detects user vs ChatGPT turns with labeled output. |
| **Code Block Support** | Converts “Copy code” areas into fenced Markdown blocks. |
| **Pretty Mode** | Adds clean formatting, numbered turns, headers, and TOC. |
| **Theme Support** | Choose from `light`, `dark`, `auto`, or `obsidian`. |
| **Obsidian Link Rewriting** | Converts anchors into `[[#Header|Label]]` format for vault integration. |
| **JSONL Export** | Generates structured datasets for analysis or model training. |
| **Emoji & Symbol Preservation** | Keeps emoji, arrows, and em-dashes intact. |
| **Signature Mode** | Optionally appends a closing mark — *“Forged by EchoForge vX.X.X.”* |

---

## ⚙️ Installation

```bash
git clone https://github.com/noct-ml/echo-forge.git
cd echo-forge
chmod +x echoforge_v115.py
```

No dependencies. No nonsense.  
Run directly via Python 3.

---

## 🧠 Usage Examples

Convert your ChatGPT export into Markdown:

```bash
python3 echoforge_v115.py chat.html out.md
```

Make it Obsidian-ready with labeled turns and a table of contents:

```bash
python3 echoforge_v115.py chat.html conversation.md   --by-speaker --user-label "James" --pretty-md   --max-width 90 --theme obsidian --obsidian-links
```

Generate a JSONL dataset:

```bash
python3 echoforge_v115.py chat.html chat.jsonl --by-speaker --jsonl
```

---

## 🧾 Command Options

| Flag | Description |
|------|--------------|
| `--by-speaker` | Split output by user/assistant turns |
| `--jsonl` | Export structured JSONL |
| `--pretty-md` | Enable structured Markdown mode |
| `--max-width` | Wrap text to a custom width |
| `--toc-depth` | Control table-of-contents depth |
| `--title` | Set a custom document title |
| `--theme` | Choose output theme (`light`, `dark`, `auto`, `obsidian`) |
| `--obsidian-links` | Convert anchors to Obsidian format |
| `--no-toc` | Skip table of contents |
| `--no-signature` | Remove the footer mark |

---

## 🏗️ Internal Architecture

**Single-file design. No imports beyond Python’s standard library.**

1. **HTML Parser** — cleans & normalizes markup.  
2. **Speaker Labeler** — identifies user and assistant turns.  
3. **Renderer** — applies Markdown formatting, headings, and wrapping.  
4. **Exporter** — writes Markdown or JSONL.  
5. **Link Rewriter** — supports Obsidian vault linking.

🜁 The entire forge is a **standalone script** — fast, auditable, and future-proof.

---

## 🜄 Design Philosophy

EchoForge is not just a utility — it’s a declaration:

> *Your words belong to you.*  
> *Conversations are artifacts, not exhaust.*  
> *Memory deserves structure.*

It’s built to counter data lock-in and transient AI interfaces — a forge for reclaiming permanence and authorship.

---

## ⚠️ Limitations

- Works only on ChatGPT HTML exports (“Save Page As”).  
- Parsing may break if OpenAI changes HTML structure.  
- Complex UI embeds or media may not render perfectly.  
- Currently single-script; modular version in consideration.

---

## 🧪 Future Directions

- Modular parser / renderer split  
- Plugin system for new output formats (CSV, XML, archive)  
- GUI or web interface  
- Multi-chat batch processing  
- Support for other LLM exports (Claude, Gemini, etc.)

---

## 🪞 Example Output

```markdown
# Dream Dialogue: Coil vs World

### Turn 001 — James
John Balance understood.

### Turn 002 — ChatGPT
In Love’s Secret Domain!

---

> Forged by EchoForge v1.1.5 — “Forging echoes into clarity.” 🜏
```

---

## 🧙 Credits

- **Author:** [noct-ml](https://github.com/noct-ml)  
- **Language:** Python 3  
- **License:** MIT  
- **Repository:** [github.com/noct-ml/echo-forge](https://github.com/noct-ml/echo-forge)

---

## 🕯️ Final Thought

EchoForge is what happens when you refuse to let your words dissolve into server logs.  
It’s the hammer and anvil of digital memory —  
the place where conversation becomes creation.

---
