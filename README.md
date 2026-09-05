# 🎬 youtube-transcript-chat-sync

> **Universal YouTube Spoken Transcript & Live Chat Correlator for AI Agents & Humans**  
> *Compatible with Hermes Agent, OpenClaw, Claude Code, GitHub Copilot CLI, Amp, and Google Antigravity.*

[![Agent Skill](https://img.shields.io/badge/Agent%20Skill-Compatible-blueviolet.svg)](#cross-agent-integration)
[![Pair Programmed with Google Antigravity](https://img.shields.io/badge/Pair%20Programmed%20with-Google%20Antigravity%20(Gemini%203.7%20Flash)-8E75B2?logo=google&logoColor=white)](https://github.com/google-antigravity)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Fast Dependency Resolution with uv](https://img.shields.io/badge/uv-isolated%20sandbox-green.svg)](https://github.com/astral-sh/uv)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 💡 What Is This & What Is It For?

When studying or summarizing livestreams, webinars, town halls, breaking news broadcasts, or video podcasts on YouTube, **half the conversation happens in the live audience chat**. Viewers ask critical questions, share links, provide corrections, and react to specific talking points in real-time.

Existing transcript tools only dump raw subtitles or video audio, completely discarding the audience chat and context.

`youtube-transcript-chat-sync` bridges this gap:
1. **Pulls the spoken audio transcript** (via official/community captions API or local `faster-whisper` speech recognition fallback).
2. **Pulls the full live chat replay** (every message, reaction, moderator link, and timestamp).
3. **Synchronizes both streams** into timestamp-aligned Markdown documents with interactive `<details>` dropdowns.
4. **Operates as a universal Agent Skill** so autonomous AI agents (Hermes, OpenClaw, Claude Code, etc.) can discover, download, and analyze entire video libraries automatically.

---

## ⚡ Quick Features

- 🎯 **Universal Channel & Playlist Support**: Accepts single video URLs, playlists, `@channel/streams`, or `@channel/videos`.
- ⏱️ **Timestamp Correlation**: Groups speech into configurable paragraph blocks (default: 90s) and nests corresponding live chat messages inside collapsible `<details>` blocks.
- 🎙️ **Zero-Drop Auto-Whisper Fallback**: For freshly finished livestreams where YouTube's auto-captions haven't finished rendering, it automatically downloads the audio stream and transcribes locally using `faster-whisper`.
- 🚀 **Zero-Config Execution**: The script uses PEP 723 inline metadata (`uv run scripts/sync_youtube.py ...`), requiring no manual `pip install` or environment management.
- 📚 **Multi-Episode Master Consolidation**: Automatically merge multi-video series into a single master document with an interactive Table of Contents.

---

## 🛠️ CLI Quickstart

Prerequisites: [`uv`](https://github.com/astral-sh/uv) and `ffmpeg`.

### 1. Process 5 Recent Channel Livestreams + Master Document
```bash
uv run scripts/sync_youtube.py "https://www.youtube.com/@SimplyCyber/streams" \
  --limit 5 \
  --consolidate \
  --output-dir ./transcripts
```

### 2. Process a Single Video
```bash
uv run scripts/sync_youtube.py "https://www.youtube.com/watch?v=SI01t4Q7m98" \
  --output-dir ./transcripts
```

### 3. Custom Time Windows (e.g. 60-Second Blocks)
```bash
uv run scripts/sync_youtube.py "https://www.youtube.com/watch?v=SI01t4Q7m98" \
  --interval 60 \
  --output-dir ./transcripts
```

---

## 🤖 Cross-Agent Integration

This repository conforms to standard Agent Skills specifications (`SKILL.md`). You can drop it into any of the following agent environments:

| Agent Platform | Installation Location |
| :--- | :--- |
| **Hermes Agent** | `~/.hermes/skills/youtube-transcript-chat-sync/` or `.hermes/skills/` |
| **OpenClaw** | `~/.openclaw/skills/youtube-transcript-chat-sync/` or `.openclaw/skills/` |
| **Universal Agent Root** | `~/.agents/skills/youtube-transcript-chat-sync/` |
| **Claude Code** | `~/.claude/skills/youtube-transcript-chat-sync/` |
| **Google Antigravity / Gemini CLI** | `~/.gemini/config/skills/youtube-transcript-chat-sync/` |
| **GitHub Copilot CLI / Amp** | `~/.copilot/skills/` or `~/.config/amp/skills/` |

### Installing into an Agent
```bash
# Clone directly into your agent's skills directory:
git clone https://github.com/zmef/youtube-transcript-chat-sync.git ~/.agents/skills/youtube-transcript-chat-sync
```

---

## 📄 Output Document Example

Generated Markdown files present clean reading layouts with integrated chat context:

```markdown
# 🔴 Aug 31's Top Cyber News NOW! - Ep 1234

- **Channel:** Simply Cyber (@SimplyCyber)
- **Date:** 2026-08-31
- **Video URL:** https://www.youtube.com/watch?v=IGCoLJ248mw
- **Broadcast Segments:** 62
- **Live Chat Messages:** 1,208

---

## Correlated Broadcast & Live Chat Stream

### `[00:01 - 01:39]`

**🎙️ Host Transcript (Dr. Gerald Auger):**
> Good morning everybody, welcome to the party. Today is Monday, August 31st. We have eight cyber threat stories of the day. We'll go beyond the headlines to see what this means for you as a practitioner...

<details>
<summary>💬 <b>Live Chat Replay (31 messages)</b></summary>

- **`[00:02]` `@marlonj122`**: GM @DaLanShark
- **`[00:10]` `@Anthony-7919`**: GM ALL
- **`[00:11]` `@NeckBeard777`**: hey gm @DaLanShark :_CyberCoffee: hope all is well
- **`[00:43]` `@JamesMcQuiggan`**: #CoffeeCupCheers @SimplyCyber
- **`[01:30]` `@nightbot`**: Today's Headlines || https://cisoseries.com/category/podca...

</details>

---
```

---

## 👥 Contributors & Credits

<table>
  <tbody>
    <tr>
      <td align="center" valign="top" width="50%">
        <a href="https://github.com/zmef">
          <img src="https://avatars.githubusercontent.com/u/57723912?v=4" width="100px;" alt="Zac Fosdyck"/><br />
          <sub><b>Zac Fosdyck</b></sub>
        </a><br />
        🥩 <b>Meatproxy</b><br />
        <sub>(Prompt Instigation & Direction)</sub>
      </td>
      <td align="center" valign="top" width="50%">
        <a href="https://github.com/google-antigravity">
          <img src="https://avatars.githubusercontent.com/u/242056456?v=4" width="100px;" alt="Google Antigravity"/><br />
          <sub><b>Google Antigravity (<a href="https://github.com/google-antigravity">@google-antigravity</a>)</b></sub>
        </a><br />
        🤖 <b>Autonomous AI Coding Partner</b><br />
        <sub>(Gemini 3.7 Flash / Architecture, Code & Documentation)</sub>
      </td>
    </tr>
  </tbody>
</table>

See [CONTRIBUTORS.md](CONTRIBUTORS.md) and [CITATION.cff](CITATION.cff) for full details.

---

## 📜 CLI Options

```text
usage: sync_youtube.py [-h] [--limit LIMIT] [--output-dir OUTPUT_DIR]
                       [--interval INTERVAL] [--no-whisper] [--consolidate]
                       url

positional arguments:
  url                   YouTube video URL, playlist URL, or channel URL (e.g. @Channel/videos, @Channel/streams)

options:
  -h, --help            show this help message and exit
  --limit LIMIT         Max number of videos to process (default: 5, 0 for all)
  --output-dir DIR      Directory to save generated files (default: ./output)
  --interval SECONDS    Timestamp window size in seconds (default: 90)
  --no-whisper          Disable local speech-to-text fallback
  --consolidate         Generate a single consolidated master markdown file
```

---

## 📄 License

[MIT License](LICENSE) © 2026 Zac & Contributors
