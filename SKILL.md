---
name: youtube-transcript-chat-sync
description: "Extracts video transcripts and live chat replays from any YouTube channel, livestream, video URL, or playlist, and synchronizes them into timestamp-correlated Markdown or JSON documents. Handles live streams, auto-captions, and local Whisper fallback for newly ended broadcasts."
---

<!--
Cross-agent notes (informational; ignored by host agents):
  - Compatible skill roots:
      * Hermes Agent: $HERMES_HOME/skills, ~/.hermes/skills, .hermes/skills, ~/.agents/skills, .agents/skills
      * OpenClaw: ~/.openclaw/skills, .openclaw/skills, ~/.agents/skills, .agents/skills
      * Google Antigravity / Gemini CLI: ~/.gemini/config/skills/
      * Claude Code: ~/.claude/skills, .claude/skills, ~/.agents/skills
      * GitHub Copilot CLI: ~/.copilot/skills, .github/skills, ~/.agents/skills
      * Amp: ~/.config/amp/skills, ~/.config/agents/skills, .agents/skills
  - Prerequisites: `uv` (or `python3` with `yt-dlp` and `youtube-transcript-api`), `ffmpeg` (for audio fallback).
-->

# YouTube Transcript & Live Chat Synchronizer

Extracts full spoken audio transcripts alongside live community chat replays for any YouTube video, livestream, playlist, or entire channel feed, synchronizing both streams into timestamp-aligned Markdown documents.

---

## Capabilities & Architecture

1. **Multi-Source Input Support**:
   - Single video URLs (`https://www.youtube.com/watch?v=...`)
   - Channel live streams (`https://www.youtube.com/@Channel/streams`)
   - Channel video feeds (`https://www.youtube.com/@Channel/videos`)
   - Playlists (`https://www.youtube.com/playlist?list=...`)
2. **Dual-Stream Extraction & Alignment**:
   - **Spoken Audio Transcript**: Pulled via official/community YouTube captions API, or auto-transcribed locally using `faster-whisper` if captions are not yet processed.
   - **Live Chat Replay**: Full timestamped audience messages, emojis, moderator announcements, and interactions parsed from the live replay.
   - **Timestamp Window Alignment**: Groups host spoken segments into coherent paragraph intervals (default: 90 seconds) and nests the corresponding live chat messages inside interactive, collapsible `<details>` blocks.
3. **Consolidation**:
   - Outputs individual clean Markdown documents for each broadcast.
   - Optionally merges multi-episode series into a unified Master Markdown file with an interactive Table of Contents.

---

## Quick Usage

The skill includes a self-contained, zero-configuration Python script in `scripts/sync_youtube.py` with PEP 723 metadata. When run via `uv run`, all dependencies (`youtube-transcript-api`, `yt-dlp`, `faster-whisper`) are resolved automatically in an isolated runtime without modifying the host system.

### 1. Single Video / Livestream
```bash
uv run scripts/sync_youtube.py "https://www.youtube.com/watch?v=VIDEO_ID" --output-dir ./transcripts
```

### 2. Channel Recent Streams (e.g., Top 5 Episodes)
```bash
uv run scripts/sync_youtube.py "https://www.youtube.com/@SimplyCyber/streams" --limit 5 --output-dir ./transcripts --consolidate
```

### 3. Adjust Timestamp Window (e.g. 60-second blocks)
```bash
uv run scripts/sync_youtube.py "https://www.youtube.com/watch?v=VIDEO_ID" --interval 60 --output-dir ./transcripts
```

### 4. Fast Mode (Disable Whisper fallback)
```bash
uv run scripts/sync_youtube.py "https://www.youtube.com/watch?v=VIDEO_ID" --no-whisper --output-dir ./transcripts
```

---

## CLI Options Reference

| Argument | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `url` | Positional | *Required* | YouTube URL (video, playlist, `@channel/streams`, `@channel/videos`) |
| `--limit` | Integer | `5` | Maximum number of videos to process when URL is a feed/playlist (`0` for all) |
| `--output-dir` | String | `./output` | Output directory where markdown and chat JSON files are saved |
| `--interval` | Integer | `90` | Time window length in seconds per paragraph block |
| `--no-whisper` | Flag | `False` | Disables local speech-to-text fallback if YouTube captions are missing |
| `--consolidate` | Flag | `False` | Generates a single unified `Consolidated_Master_Transcripts.md` with TOC |

---

## Document Output Format

Each generated Markdown file follows this structured schema:

```markdown
# Episode Title

- **Channel:** Channel Name
- **Date:** YYYY-MM-DD
- **Video URL:** [https://www.youtube.com/watch?v=...](...)
- **Broadcast Segments:** 62
- **Live Chat Messages:** 1,208

---

## Correlated Broadcast & Live Chat Stream

### `[00:01 - 01:30]`

**🎙️ Host Transcript:**
> Spoken host audio commentary transcribed and grouped into coherent paragraphs...

<details>
<summary>💬 <b>Live Chat Replay (15 messages)</b></summary>

- **`[00:10]` `@Viewer1`**: Good morning everyone! :coffee:
- **`[00:45]` `@Viewer2`**: Is there an advisory published for this CVE?
- **`[01:15]` `@Moderator`**: Link to show notes: https://example.com

</details>

---
```

---

## Agent Execution Workflow

When an AI agent is asked to pull transcripts or live chats:
1. **Target Discovery**: Run `yt-dlp --flat-playlist --print "%(id)s | %(upload_date)s | %(title)s" "<URL>" -I 1:<N>` to confirm target episodes.
2. **Execute Sync Script**: Run `uv run <path_to_skill>/scripts/sync_youtube.py "<URL>" --output-dir <DIR> --consolidate`.
3. **Verify Output**: Inspect the resulting markdown files in the output directory.
4. **Present Results**: Provide direct clickable file links and summaries of the topics discussed.
