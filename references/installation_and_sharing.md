# Cross-Agent Installation & Sharing Guide

This skill follows standard Agent Skills specification and works seamlessly across multiple AI agent runtimes:

---

## 1. Hermes Agent
Copy the skill folder into Hermes's skill search directory:
```bash
mkdir -p ~/.hermes/skills
cp -r youtube-transcript-chat-sync ~/.hermes/skills/
```
Or for workspace-specific skills:
```bash
mkdir -p .hermes/skills
cp -r youtube-transcript-chat-sync .hermes/skills/
```

---

## 2. OpenClaw
Copy the skill into the OpenClaw skill directory:
```bash
mkdir -p ~/.openclaw/skills
cp -r youtube-transcript-chat-sync ~/.openclaw/skills/
```
Or for project-level usage:
```bash
mkdir -p .openclaw/skills
cp -r youtube-transcript-chat-sync .openclaw/skills/
```

---

## 3. Claude Code
Copy into your global or local Claude skills folder:
```bash
mkdir -p ~/.claude/skills
cp -r youtube-transcript-chat-sync ~/.claude/skills/
```

---

## 4. Universal Agent Root (`.agents/skills`)
Most modern autonomous agents (including Amp, Copilot CLI, Hermes, OpenClaw) automatically scan `~/.agents/skills` or `./.agents/skills`:
```bash
mkdir -p ~/.agents/skills
cp -r youtube-transcript-chat-sync ~/.agents/skills/
```

---

## 5. Google Antigravity / Gemini CLI
Installed in your user config:
```bash
mkdir -p ~/.gemini/config/skills/
cp -r youtube-transcript-chat-sync ~/.gemini/config/skills/
```

---

## Packaging & Sharing with Others

### Option A: Distribute as a Git Repository
```bash
cd youtube-transcript-chat-sync
git init
git add .
git commit -m "feat: initial release of youtube-transcript-chat-sync skill"
# Push to GitHub or GitLab
```
Other users can clone it directly into their agent skills directory:
```bash
git clone https://github.com/<your-username>/youtube-transcript-chat-sync.git ~/.agents/skills/youtube-transcript-chat-sync
```

### Option B: Distribute as a ZIP archive
```bash
zip -r youtube-transcript-chat-sync.zip youtube-transcript-chat-sync/
```
Users simply extract it into their respective agent skills folder.
