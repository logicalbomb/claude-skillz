---
name: yt-summarizer
description: Create structured, searchable summaries of educational YouTube videos with time-coded links. Use when the user provides a YouTube URL and wants to create a reference document, study guide, or searchable summary of the video content. Generates hierarchical markdown summaries with clickable timestamps for easy navigation back to specific video moments.
---

# YouTube Video Summarizer

Create hierarchical, time-coded summaries of educational YouTube videos for future reference and study.

## Workflow

**Note**: These scripts require network access to YouTube. If running in a restricted environment, ensure YouTube (www.youtube.com) is accessible.

### Step 1: Fetch Video Data

**Required**: Run the transcript script to get video content with timestamps:

```bash
python scripts/fetch_transcript.py <youtube_url>
```

**Fallback**: If captions are unavailable, use whisper.cpp to transcribe audio:

```bash
python scripts/transcribe_audio.py <youtube_url> [model]
```

Models: tiny, base (default), small, medium, large. Set `WHISPER_MODEL` env var to change default.

**Optional**: If available, fetch metadata for chapters and title:

```bash
python scripts/fetch_metadata.py <youtube_url>
```

The metadata script provides title, chapters (if available), and duration. If unavailable, ask the user for the video title or extract it from the URL.

**Error handling**:
- No captions + no whisper.cpp: "No captions available. Install whisper.cpp to enable audio transcription: https://github.com/ggerganov/whisper.cpp"
- No captions + whisper failed: Report the specific transcription error to the user

### Step 2: Analyze Structure

Review the video data to determine structure:

1. **Check for chapters**: If `metadata.chapters` exists and is non-empty, use these as the top-level structure
2. **Transcript analysis**: Review the transcript for natural topic transitions, key concepts, and information density
3. **Determine granularity**: Aim for approximately 1 timestamp entry per 2 minutes, adjusting based on content density

### Step 3: Generate Hierarchical Summary

Create a markdown document with this structure:

```markdown
# [Video Title]

**Channel**: [Uploader Name]
**Duration**: [Duration in HH:MM:SS]
**URL**: [Full YouTube URL]

---

## Summary

[2-3 sentence overview of the video's main topic and key takeaways]

---

## Detailed Contents

### [Chapter/Topic 1]
- **[MM:SS](youtube_url&t=XXs)** - Brief description of key point
- **[MM:SS](youtube_url&t=XXs)** - Brief description of key point

#### [Subtopic if needed]
- **[MM:SS](youtube_url&t=XXs)** - Brief description of key point

### [Chapter/Topic 2]
...
```

**Timestamp format**: Use `&t=XXs` format where XX is seconds (e.g., `&t=125s` for 2:05)
**Brief descriptions**: Each bullet should be 1-2 sentences capturing the key information at that timestamp
**Hierarchical structure**: Use chapters as H3, subtopics as H4, with timestamp bullets under each

### Step 4: Quality Check

Before finalizing:
- Verify all timestamps are clickable links
- Ensure granularity is appropriate (~1 entry per 2 minutes, adjusted for density)
- Confirm descriptions are searchable and informative
- Check that hierarchy reflects the video's natural structure

### Step 5: Output

Save the markdown summary to `./[sanitized_video_title]_summary.md` (current working directory) and present it to the user.

## Best Practices

- **Use existing chapters**: When available, YouTube chapters provide excellent top-level structure
- **Adjust density**: Dense technical content may need more timestamps; lighter content may need fewer
- **Searchable descriptions**: Write descriptions that capture keywords someone would search for later
- **Natural hierarchy**: Don't force subtopics if the content flows linearly
- **Link validation**: Always test that timestamp links work correctly

## Scripts

- `scripts/fetch_metadata.py` - Fetches video title, chapters, duration, and description using yt-dlp
- `scripts/fetch_transcript.py` - Fetches transcript with timestamps using youtube-transcript-api
- `scripts/transcribe_audio.py` - Fallback: downloads audio and transcribes with whisper.cpp

## Environment Variables

| Variable | Purpose |
|----------|---------|
| `WHISPER_CPP_PATH` | Override whisper.cpp binary location (default: search PATH) |
| `WHISPER_MODEL` | Override default model (default: base) |
