# 🜂 **EchoForge**
### *Transcriber of the Machine’s Whisper*
—
A lightweight, offline converter for ChatGPT HTML exports → clean Markdown or JSONL.
Private, portable, precise — a tool for reclaiming your words from the void.

> *Memory deserves structure.*

---

## 🜂 Overview

**EchoForge** transforms ChatGPT’s “Save Page As…” HTML into durable, human-readable artifacts:

- Markdown for notes, vaults, and documents  
- JSONL for datasets, training corpora, and analysis
- Works under Windows/Linux/macOS

No APIs.  
No servers.  
No cloud.  
Just your conversations, reforged exactly how *you* want them.

---

## 🜍 Core Features

- **HTML purification** — removes scripts, UI clutter, hidden markup  
- **Speaker separation** — labels user vs assistant turns  
- **Code block preservation** — intact fenced Markdown  
- **Pretty Mode** — structured, numbered, formatted  
- **Themes** — `light`, `dark`, `auto`, `obsidian`  
- **Obsidian link rewriting**  
- **JSONL export**  
- **Emoji + symbol integrity**  
- **Signature mode** — optional footer mark  

---

## 🜏 Installation

```bash
git clone https://github.com/noct-ml/echo-forge.git
cd echo-forge
chmod +x echoforge.py
```

---

## 🜸 Usage Examples

### Convert HTML → Markdown  
```bash
python echoforge.py chat.html out.md
```

### Obsidian-Ready  
```bash
python echoforge.py chat.html conversation.md --by-speaker --user-label "James" --pretty-md --theme obsidian --obsidian-links
```

### JSONL Dataset  
```bash
python echoforge.py chat.html chat.jsonl --by-speaker --jsonl
```

---

## 🜍 Example Output

```markdown
# Dream Dialogue: Coil vs World

### Turn 001 — James
John Balance understood.

### Turn 002 — ChatGPT
In Love’s Secret Domain!

---

> Forged by EchoForge v1.1.7 — “Forging echoes into clarity.” 🜏
```

---

## 🜁 Command Options

| Flag | Description |
|------|-------------|
| `--by-speaker` | Label user/assistant turns |
| `--jsonl` | Export structured JSONL |
| `--pretty-md` | Structured Markdown mode |
| `--max-width` | Text wrapping |
| `--toc-depth` | TOC depth |
| `--title` | Custom document title |
| `--theme` | Theme selection |
| `--obsidian-links` | Vault-safe link format |
| `--no-toc` | Disable TOC |
| `--no-signature` | Disable final signature |

---

## 🜍 Architecture

1. **HTML Parser** — cleans + extracts  
2. **Speaker Labeler** — identifies turns  
3. **Renderer** — builds Markdown  
4. **Exporter** — writes Markdown/JSONL  
5. **Link Rewriter** — Obsidian-safe anchors  

Fast, minimal, future-proof.

---

## 🜛 Design Philosophy

> *Your conversations are artifacts, not exhaust.*  
> *Your words belong to you.*  
> *Memory should be shaped, not scattered.*

---

