# Whisper Fallback Design

## Overview

When `fetch_transcript.py` fails (captions disabled/unavailable), a new script `transcribe_audio.py` downloads the video's audio track and transcribes it locally using whisper.cpp.

## Decisions

| Decision | Choice |
|----------|--------|
| Transcription engine | Local whisper.cpp |
| Model size | Configurable, default: base |
| Audio download | yt-dlp (existing dependency) |
| Temp file location | System temp dir |
| whisper.cpp location | PATH first, `WHISPER_CPP_PATH` env var override |
| Audio format | WAV 16kHz mono (whisper.cpp native) |
| Missing whisper.cpp | Fail with install instructions |

## New Script: `scripts/transcribe_audio.py`

**Inputs:**
- YouTube URL or video ID
- Optional: model size (tiny/base/small/medium/large), defaults to `base`

**Process:**
1. Check whisper.cpp availability (PATH, then `WHISPER_CPP_PATH` env var)
2. If not found -> fail with install instructions
3. Download audio via yt-dlp as WAV 16kHz mono to system temp dir
4. Run whisper.cpp with specified model
5. Parse output, format as timestamped transcript matching existing format
6. Clean up temp audio file
7. Return JSON with `success`, `video_id`, `transcript` (same structure as fetch_transcript.py)

**Output format:** Matches `fetch_transcript.py` so the skill workflow is unchanged.

## Workflow Changes to SKILL.md

### Step 1 modification

1. Run fetch_transcript.py
2. If fails -> run transcribe_audio.py as fallback
3. If both fail -> inform user (with reason)

### Error messages

- No captions + no whisper: "No captions available. Install whisper.cpp to enable audio transcription fallback: [install link]"
- No captions + whisper failed: "Transcription failed: [error details]"

### Step 5 modification

**Old:** `/mnt/user-data/outputs/[sanitized_video_title]_summary.md`
**New:** `./<sanitized_video_title>_summary.md` (current working directory)

## Dependencies

**Existing (no changes):**
- yt-dlp
- youtube-transcript-api

**New optional dependency (for fallback):**
- whisper.cpp with model files

## Environment Variables

| Variable | Purpose |
|----------|---------|
| `WHISPER_CPP_PATH` | Override whisper binary location |
| `WHISPER_MODEL` | Override default model (base) |

## Files Changed

| File | Change |
|------|--------|
| `scripts/transcribe_audio.py` | **New** - whisper.cpp audio transcription |
| `scripts/fetch_transcript.py` | No changes |
| `scripts/fetch_metadata.py` | No changes |
| `SKILL.md` | Update Step 1 (fallback flow), Step 5 (output path), error handling |
