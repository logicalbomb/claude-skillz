#!/usr/bin/env python3
"""
Fetch YouTube video metadata including chapters, title, and description.
Uses yt-dlp to extract this information.
"""

import sys
import json
import subprocess
import re


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
    
    return url


def fetch_metadata(video_url):
    """
    Fetch metadata for a YouTube video including chapters.
    
    Args:
        video_url: YouTube URL or video ID
        
    Returns:
        dict with 'success', metadata fields, and optional 'error'
    """
    try:
        video_id = extract_video_id(video_url)
        
        # Use yt-dlp to extract metadata
        cmd = [
            'yt-dlp',
            '--dump-json',
            '--no-download',
            f'https://www.youtube.com/watch?v={video_id}'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            return {
                'success': False,
                'error': f'Failed to fetch metadata: {result.stderr}'
            }
        
        metadata = json.loads(result.stdout)
        
        # Extract relevant fields
        return {
            'success': True,
            'video_id': video_id,
            'title': metadata.get('title', 'Unknown'),
            'duration': metadata.get('duration', 0),
            'description': metadata.get('description', ''),
            'chapters': metadata.get('chapters', []),
            'uploader': metadata.get('uploader', 'Unknown')
        }
        
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'error': 'Timeout while fetching metadata'
        }
    except json.JSONDecodeError:
        return {
            'success': False,
            'error': 'Failed to parse metadata JSON'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Error fetching metadata: {str(e)}'
        }


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python fetch_metadata.py <youtube_url_or_video_id>")
        sys.exit(1)
    
    video_url = sys.argv[1]
    result = fetch_metadata(video_url)
    
    print(json.dumps(result, indent=2))
