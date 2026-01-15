#!/usr/bin/env python3
"""
Fallback transcription using whisper.cpp when YouTube captions are unavailable.
Downloads audio via yt-dlp and transcribes locally.
"""

import sys
import json
import os
import re
import shutil
import subprocess
import tempfile


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


def find_whisper():
    """
    Find whisper.cpp binary.
    Checks WHISPER_CPP_PATH env var first, then PATH.

    Returns:
        str: Path to whisper binary, or None if not found
    """
    # Check env var first
    env_path = os.environ.get('WHISPER_CPP_PATH')
    if env_path and os.path.isfile(env_path) and os.access(env_path, os.X_OK):
        return env_path

    # Check PATH for common names
    for name in ['whisper-cli', 'whisper', 'whisper-cpp', 'main']:
        path = shutil.which(name)
        if path:
            return path

    return None


def find_model(model_name='base'):
    """
    Find whisper model file.
    Checks WHISPER_MODEL_PATH env var first, then common locations.

    Args:
        model_name: Model name (tiny, base, small, medium, large)

    Returns:
        str: Path to model file, or None if not found
    """
    # Check env var for explicit path
    env_path = os.environ.get('WHISPER_MODEL_PATH')
    if env_path and os.path.isfile(env_path):
        return env_path

    # Common model filename patterns
    patterns = [
        f'ggml-{model_name}.bin',
        f'ggml-{model_name}-q8_0.bin',
        f'ggml-{model_name}-q5_0.bin',
    ]

    # Common locations
    locations = [
        '/opt/homebrew/Cellar/whisper-cpp/*/share/whisper-cpp/models',
        os.path.expanduser('~/.cache/whisper'),
        os.path.expanduser('~/whisper.cpp/models'),
        '/usr/local/share/whisper-cpp/models',
    ]

    import glob
    for loc_pattern in locations:
        for loc in glob.glob(loc_pattern):
            for pattern in patterns:
                model_path = os.path.join(loc, pattern)
                if os.path.isfile(model_path):
                    return model_path

    return None


def get_model_name():
    """Get whisper model name from env var or default to base."""
    return os.environ.get('WHISPER_MODEL', 'base')


def download_audio(video_id, output_path):
    """
    Download audio from YouTube as WAV 16kHz mono.

    Args:
        video_id: YouTube video ID
        output_path: Path to save the WAV file

    Returns:
        dict with 'success' and optional 'error'
    """
    try:
        cmd = [
            'yt-dlp',
            '-x',  # Extract audio
            '--audio-format', 'wav',
            '--postprocessor-args', 'ffmpeg:-ar 16000 -ac 1',
            '-o', output_path,
            f'https://www.youtube.com/watch?v={video_id}'
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

        if result.returncode != 0:
            return {
                'success': False,
                'error': f'Failed to download audio: {result.stderr}'
            }

        return {'success': True}

    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'error': 'Timeout while downloading audio'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Error downloading audio: {str(e)}'
        }


def transcribe_with_whisper(whisper_path, audio_path, model_path):
    """
    Transcribe audio using whisper.cpp.

    Args:
        whisper_path: Path to whisper binary
        audio_path: Path to WAV audio file
        model_path: Full path to model file

    Returns:
        dict with 'success', 'segments' list, and optional 'error'
    """
    try:
        cmd = [
            whisper_path,
            '-m', model_path,
            '-f', audio_path,
            '-oj',  # Output JSON
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)

        if result.returncode != 0:
            return {
                'success': False,
                'error': f'Whisper transcription failed: {result.stderr}'
            }

        # Parse JSON output
        output = json.loads(result.stdout)

        return {
            'success': True,
            'segments': output.get('transcription', [])
        }

    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'error': 'Timeout during transcription (>30 min)'
        }
    except json.JSONDecodeError:
        return {
            'success': False,
            'error': 'Failed to parse whisper output'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Error during transcription: {str(e)}'
        }


def convert_to_transcript_format(segments):
    """
    Convert whisper.cpp segments to match fetch_transcript.py format.

    Args:
        segments: List of whisper segments with timestamps

    Returns:
        List of transcript entries with 'text', 'start', 'duration'
    """
    transcript = []

    for segment in segments:
        # whisper.cpp JSON format has 'timestamps' with 'from' and 'to' in ms
        # and 'text' field
        start_ms = segment.get('offsets', {}).get('from', 0)
        end_ms = segment.get('offsets', {}).get('to', start_ms)

        transcript.append({
            'text': segment.get('text', '').strip(),
            'start': start_ms / 1000.0,
            'duration': (end_ms - start_ms) / 1000.0
        })

    return transcript


def transcribe_audio(video_url, model=None):
    """
    Main function to transcribe YouTube video audio.

    Args:
        video_url: YouTube URL or video ID
        model: Whisper model to use (default: base or WHISPER_MODEL env)

    Returns:
        dict with 'success', 'video_id', 'transcript', and optional 'error'
    """
    # Find whisper.cpp
    whisper_path = find_whisper()
    if not whisper_path:
        return {
            'success': False,
            'error': 'whisper.cpp not found. Install from https://github.com/ggerganov/whisper.cpp and ensure it is in PATH or set WHISPER_CPP_PATH'
        }

    video_id = extract_video_id(video_url)
    model_name = model or get_model_name()

    # Find model file
    model_path = find_model(model_name)
    if not model_path:
        return {
            'success': False,
            'error': f'Whisper model "{model_name}" not found. Set WHISPER_MODEL_PATH or download model to a standard location.'
        }

    # Create temp file for audio
    temp_dir = tempfile.mkdtemp()
    audio_path = os.path.join(temp_dir, f'{video_id}.wav')

    try:
        # Download audio
        download_result = download_audio(video_id, audio_path)
        if not download_result['success']:
            return download_result

        # Transcribe
        transcribe_result = transcribe_with_whisper(whisper_path, audio_path, model_path)
        if not transcribe_result['success']:
            return transcribe_result

        # Convert format
        transcript = convert_to_transcript_format(transcribe_result['segments'])

        return {
            'success': True,
            'video_id': video_id,
            'transcript': transcript,
            'source': 'whisper'
        }

    finally:
        # Clean up temp files
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python transcribe_audio.py <youtube_url_or_video_id> [model]")
        print("Models: tiny, base (default), small, medium, large")
        sys.exit(1)

    video_url = sys.argv[1]
    model = sys.argv[2] if len(sys.argv) > 2 else None

    result = transcribe_audio(video_url, model)
    print(json.dumps(result, indent=2))
