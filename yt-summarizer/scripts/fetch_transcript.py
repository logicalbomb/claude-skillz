#!/usr/bin/env python3
"""
Fetch YouTube video transcript with timestamps.
Supports both manual and auto-generated captions.
"""

import sys
import json
import re
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound


def extract_video_id(url):
    """Extract video ID from various YouTube URL formats."""
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
        r'youtube\.com\/watch\?.*v=([^&\n?#]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    # If no pattern matches, assume it's already a video ID
    return url


def fetch_transcript(video_url):
    """
    Fetch transcript for a YouTube video.
    
    Args:
        video_url: YouTube URL or video ID
        
    Returns:
        dict with 'success', 'transcript' (list of entries), and optional 'error'
    """
    try:
        video_id = extract_video_id(video_url)
        
        # Create API instance and fetch transcript
        api = YouTubeTranscriptApi()
        transcript_data = api.fetch(video_id, languages=['en'])

        # Convert to list of dicts for JSON serialization
        transcript_list = [
            {'text': item.text, 'start': item.start, 'duration': item.duration}
            for item in transcript_data
        ]

        return {
            'success': True,
            'video_id': video_id,
            'transcript': transcript_list
        }
        
    except TranscriptsDisabled:
        return {
            'success': False,
            'error': 'Transcripts are disabled for this video'
        }
    except NoTranscriptFound:
        return {
            'success': False,
            'error': 'No transcript found for this video'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Error fetching transcript: {str(e)}'
        }


def format_timestamp(seconds):
    """Convert seconds to MM:SS or HH:MM:SS format."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python fetch_transcript.py <youtube_url_or_video_id>")
        sys.exit(1)
    
    video_url = sys.argv[1]
    result = fetch_transcript(video_url)
    
    # Output as JSON for easy parsing
    print(json.dumps(result, indent=2))
