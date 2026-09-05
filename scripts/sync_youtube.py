#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "youtube-transcript-api",
#     "yt-dlp",
#     "faster-whisper",
# ]
# ///
"""
Universal YouTube Transcript & Live Chat Correlator
Extracts spoken transcripts and live chat replays from any YouTube channel, playlist, or video,
and synchronizes them into formatted, timestamp-correlated Markdown / JSON documents.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from youtube_transcript_api import YouTubeTranscriptApi

def format_time(seconds: float) -> str:
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    hours = int(mins // 60)
    mins = int(mins % 60)
    if hours > 0:
        return f"{hours:02d}:{mins:02d}:{secs:02d}"
    return f"{mins:02d}:{secs:02d}"

def sanitize_filename(name: str) -> str:
    return re.sub(r'[\\/*?:"<>|]', "", name).strip().replace(" ", "_")

def get_video_list(url: str, limit: int = 5) -> list[dict]:
    """Uses yt-dlp to extract video metadata for single URLs, playlists, or channels."""
    cmd = [
        "yt-dlp",
        "--flat-playlist",
        "--print", "%(id)s\t%(upload_date)s\t%(title)s\t%(channel)s",
        url
    ]
    if limit > 0:
        cmd.extend(["-I", f"1:{limit}"])
        
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    videos = []
    for line in res.stdout.strip().splitlines():
        parts = line.split("\t")
        if len(parts) >= 3:
            vid_id = parts[0]
            upload_date = parts[1] if parts[1] != "NA" else "unknown-date"
            title = parts[2]
            channel = parts[3] if len(parts) > 3 else "YouTube Channel"
            videos.append({
                "id": vid_id,
                "url": f"https://www.youtube.com/watch?v={vid_id}",
                "title": title,
                "date": upload_date,
                "channel": channel
            })
    return videos

def fetch_transcript_api(video_id: str) -> list[dict]:
    """Attempts to fetch transcripts via YouTubeTranscriptApi."""
    api = YouTubeTranscriptApi()
    fetched = api.fetch(video_id)
    snippets = []
    for s in fetched.snippets:
        snippets.append({
            "start": float(s.start),
            "duration": float(s.duration),
            "text": s.text.strip()
        })
    return snippets

def fetch_transcript_whisper(video_url: str, model_size: str = "base.en") -> list[dict]:
    """Fallback: downloads audio stream and performs local Whisper transcription."""
    from faster_whisper import WhisperModel
    with tempfile.TemporaryDirectory() as tmpdir:
        audio_path = os.path.join(tmpdir, "audio.m4a")
        print(f"  [Whisper] Downloading audio stream for {video_url}...")
        subprocess.run([
            "yt-dlp",
            "-f", "ba[ext=m4a]/ba",
            "-o", audio_path,
            video_url,
            "--force-overwrites"
        ], capture_output=True, check=True)
        
        print(f"  [Whisper] Transcribing with model '{model_size}'...")
        model = WhisperModel(model_size, device="cpu", compute_type="int8")
        segments, _ = model.transcribe(audio_path, beam_size=5, language="en")
        snippets = []
        for seg in segments:
            snippets.append({
                "start": float(seg.start),
                "duration": float(seg.end - seg.start),
                "text": seg.text.strip()
            })
        return snippets

def fetch_live_chat(video_url: str, output_dir: str, video_id: str) -> list[dict]:
    """Downloads live chat replay JSON and extracts timestamped messages."""
    chat_file = os.path.join(output_dir, f"{video_id}.live_chat.json")
    if not os.path.exists(chat_file):
        print(f"  [Chat] Fetching live chat replay for {video_id}...")
        subprocess.run([
            "yt-dlp",
            "--write-subs",
            "--sub-lang", "live_chat",
            "--skip-download",
            "-o", os.path.join(output_dir, "%(id)s.%(ext)s"),
            video_url
        ], capture_output=True)
        
    messages = []
    if not os.path.exists(chat_file):
        return messages
        
    with open(chat_file, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                data = json.loads(line)
            except Exception:
                continue
            replay = data.get("replayChatItemAction", {})
            actions = replay.get("actions", [])
            offset_msec = int(replay.get("videoOffsetTimeMsec", 0))
            sec = max(0.0, offset_msec / 1000.0)
            
            for act in actions:
                item = act.get("addChatItemAction", {}).get("item", {})
                renderer = item.get("liveChatTextMessageRenderer") or item.get("liveChatPaidMessageRenderer")
                if renderer:
                    author = renderer.get("authorName", {}).get("simpleText", "User")
                    runs = renderer.get("message", {}).get("runs", [])
                    msg_parts = []
                    for r in runs:
                        if "text" in r:
                            msg_parts.append(r["text"])
                        elif "emoji" in r:
                            emoji_obj = r["emoji"]
                            shortcuts = emoji_obj.get("shortcuts") or []
                            msg_parts.append(shortcuts[0] if shortcuts else (emoji_obj.get("accessibility", {}).get("accessibilityData", {}).get("label") or ":emoji:"))
                    msg = "".join(msg_parts).strip()
                    if msg:
                        messages.append({
                            "seconds": sec,
                            "timestamp": format_time(sec),
                            "author": author,
                            "message": msg
                        })
                        
    messages.sort(key=lambda x: x["seconds"])
    return messages

def group_and_correlate(snippets: list[dict], chat_messages: list[dict], interval_seconds: int = 90) -> list[dict]:
    paragraphs = []
    current_block = []
    current_start = None
    last_end = 0.0
    
    chat_idx = 0
    total_chat = len(chat_messages)
    
    for item in snippets:
        start = item.get("start", 0.0)
        dur = item.get("duration", 0.0)
        end = start + dur
        text = item.get("text", "").strip()
        if not text:
            continue
            
        if current_start is None:
            current_start = start
            
        current_block.append(text)
        last_end = max(last_end, end)
        
        if (start - current_start) >= interval_seconds:
            window_start = current_start
            window_end = last_end
            
            matched_chats = []
            while chat_idx < total_chat and chat_messages[chat_idx]["seconds"] < window_end:
                if chat_messages[chat_idx]["seconds"] >= window_start:
                    matched_chats.append(chat_messages[chat_idx])
                chat_idx += 1
                
            paragraphs.append({
                "start_time": format_time(window_start),
                "end_time": format_time(window_end),
                "start_sec": window_start,
                "end_sec": window_end,
                "text": " ".join(current_block),
                "chat_messages": matched_chats
            })
            current_block = []
            current_start = None
            
    if current_block:
        window_start = current_start or 0.0
        window_end = last_end
        matched_chats = []
        while chat_idx < total_chat:
            if chat_messages[chat_idx]["seconds"] >= window_start:
                matched_chats.append(chat_messages[chat_idx])
            chat_idx += 1
            
        paragraphs.append({
            "start_time": format_time(window_start),
            "end_time": format_time(window_end),
            "start_sec": window_start,
            "end_sec": window_end,
            "text": " ".join(current_block),
            "chat_messages": matched_chats
        })
        
    return paragraphs

def write_markdown_doc(video: dict, paragraphs: list[dict], chat_count: int, output_filepath: str):
    with open(output_filepath, "w", encoding="utf-8") as f:
        f.write(f"# {video.get('title', 'YouTube Broadcast')}\n\n")
        f.write(f"- **Channel:** {video.get('channel', 'N/A')}\n")
        f.write(f"- **Date:** {video.get('date', 'N/A')}\n")
        f.write(f"- **Video URL:** [{video['url']}]({video['url']})\n")
        f.write(f"- **Broadcast Segments:** {len(paragraphs)}\n")
        f.write(f"- **Live Chat Messages:** {chat_count}\n\n")
        f.write("---\n\n")
        f.write("## Correlated Broadcast & Live Chat Stream\n\n")
        
        for p in paragraphs:
            f.write(f"### `[{p['start_time']} - {p['end_time']}]`\n\n")
            f.write(f"**🎙️ Host Transcript:**\n")
            f.write(f"> {p['text']}\n\n")
            
            if p["chat_messages"]:
                f.write(f"<details>\n")
                f.write(f"<summary>💬 <b>Live Chat Replay ({len(p['chat_messages'])} messages)</b></summary>\n\n")
                for c in p["chat_messages"]:
                    clean_msg = c['message'].replace('\n', ' ')
                    f.write(f"- **`[{c['timestamp']}]` `{c['author']}`**: {clean_msg}\n")
                f.write(f"\n</details>\n\n")
            else:
                f.write(f"*(No live chat messages recorded during this window)*\n\n")
            f.write("---\n\n")

def process_video(video: dict, output_dir: str, interval: int = 90, enable_whisper: bool = True) -> dict:
    vid_id = video["id"]
    print(f"\n▶ Processing: {video['title']} ({video['url']})")
    
    # 1. Fetch transcript
    snippets = []
    try:
        snippets = fetch_transcript_api(vid_id)
        print(f"  ✓ Fetched {len(snippets)} snippets via YouTube Captions API")
    except Exception as e:
        print(f"  ⚠ Captions API unavailable ({e})")
        if enable_whisper:
            try:
                snippets = fetch_transcript_whisper(video["url"])
                print(f"  ✓ Generated {len(snippets)} snippets via local Whisper")
            except Exception as we:
                print(f"  ✖ Whisper transcription failed: {we}")
                return {"success": False, "error": str(we), "video": video}
        else:
            return {"success": False, "error": str(e), "video": video}
            
    # 2. Fetch Chat Replay
    chat_messages = fetch_live_chat(video["url"], output_dir, vid_id)
    print(f"  ✓ Loaded {len(chat_messages)} live chat replay messages")
    
    # 3. Correlate
    paragraphs = group_and_correlate(snippets, chat_messages, interval_seconds=interval)
    
    # 4. Save markdown
    filename = f"{sanitize_filename(video['date'])}_{sanitize_filename(video['title'])}_{vid_id}.md"
    filepath = os.path.join(output_dir, filename)
    write_markdown_doc(video, paragraphs, len(chat_messages), filepath)
    print(f"  ✓ Saved document to: {filepath}")
    
    return {
        "success": True,
        "video": video,
        "filename": filename,
        "filepath": filepath,
        "paragraphs": len(paragraphs),
        "chats": len(chat_messages)
    }

def main():
    parser = argparse.ArgumentParser(description="Synchronize YouTube transcripts with live chat replay into correlated Markdown.")
    parser.add_argument("url", help="YouTube video URL, playlist URL, or channel URL (e.g. @Channel/videos, @Channel/streams)")
    parser.add_argument("--limit", type=int, default=5, help="Max number of videos to process when URL is a playlist/channel (default: 5, 0 for all)")
    parser.add_argument("--output-dir", default="./output", help="Directory to save generated files")
    parser.add_argument("--interval", type=int, default=90, help="Timestamp window size in seconds (default: 90)")
    parser.add_argument("--no-whisper", action="store_true", help="Disable Whisper fallback if captions are disabled")
    parser.add_argument("--consolidate", action="store_true", help="Generate a single consolidated master markdown for all videos")
    
    args = parser.parse_args()
    os.makedirs(args.output_dir, exist_ok=True)
    
    print(f"Scanning target: {args.url}")
    videos = get_video_list(args.url, limit=args.limit)
    if not videos:
        print("No videos found.")
        sys.exit(1)
        
    print(f"Found {len(videos)} video(s) to process.")
    results = []
    for v in videos:
        res = process_video(v, args.output_dir, interval=args.interval, enable_whisper=not args.no_whisper)
        results.append(res)
        
    if args.consolidate and len(results) > 1:
        master_file = os.path.join(args.output_dir, "Consolidated_Master_Transcripts.md")
        with open(master_file, "w", encoding="utf-8") as out:
            out.write("# Consolidated YouTube Transcripts & Live Chat Replays\n\n")
            out.write("## Table of Contents\n\n")
            for r in results:
                if r.get("success"):
                    v = r["video"]
                    anchor = f"{v['id']}".lower()
                    out.write(f"- [{v['title']} ({v['date']})](#{anchor})\n")
            out.write("\n---\n\n")
            
            for r in results:
                if r.get("success"):
                    v = r["video"]
                    out.write(f'<a id="{v["id"].lower()}"></a>\n\n')
                    with open(r["filepath"], "r", encoding="utf-8") as f:
                        content = f.read()
                    out.write(content)
                    out.write("\n\n---\n\n")
        print(f"\n✓ Generated Consolidated Master File: {master_file}")
        
    print(f"\nAll operations complete! Output directory: {os.path.abspath(args.output_dir)}")

if __name__ == "__main__":
    main()
