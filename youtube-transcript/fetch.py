#!/usr/bin/env python3
"""
YouTube Transcript Fetcher
Fetches transcripts from YouTube videos using youtube-transcript-api
"""

import sys
import re
import argparse
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter


def extract_video_id(url_or_id: str) -> str:
    """Extract video ID from YouTube URL or return as-is if already an ID."""
    # Common YouTube URL patterns
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})',
        r'^([a-zA-Z0-9_-]{11})$'  # Direct video ID
    ]

    for pattern in patterns:
        match = re.search(pattern, url_or_id)
        if match:
            return match.group(1)

    # Return as-is and let the API handle validation
    return url_or_id


def list_transcripts(video_id: str) -> None:
    """List all available transcripts for a video."""
    try:
        ytt_api = YouTubeTranscriptApi()
        transcript_list = ytt_api.list(video_id)

        print(f"Available transcripts for video {video_id}:\n")

        for transcript in transcript_list:
            transcript_type = "Manual" if not transcript.is_generated else "Auto-generated"
            translatable = "Yes" if transcript.is_translatable else "No"
            print(f"  - {transcript.language} ({transcript.language_code})")
            print(f"    Type: {transcript_type}, Translatable: {translatable}")

    except Exception as e:
        print(f"Error listing transcripts: {e}", file=sys.stderr)
        sys.exit(1)


def fetch_transcript(video_id: str, languages: list = None) -> str:
    """Fetch transcript for a video."""
    try:
        ytt_api = YouTubeTranscriptApi()

        if languages:
            transcript = ytt_api.fetch(video_id, languages=languages)
        else:
            # Try English first, then any available
            try:
                transcript = ytt_api.fetch(video_id, languages=['en', 'en-US', 'en-GB'])
            except:
                # Fall back to any available transcript
                transcript_list = ytt_api.list(video_id)
                first_transcript = next(iter(transcript_list))
                transcript = first_transcript.fetch()

        # Format as plain text
        formatter = TextFormatter()
        text = formatter.format_transcript(transcript)

        return text

    except Exception as e:
        print(f"Error fetching transcript: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description='Fetch YouTube video transcripts',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s "https://www.youtube.com/watch?v=VIDEO_ID"
  %(prog)s VIDEO_ID
  %(prog)s VIDEO_ID --lang de
  %(prog)s VIDEO_ID --list
        '''
    )

    parser.add_argument('video', help='YouTube URL or video ID')
    parser.add_argument('--lang', '-l', help='Preferred language code (e.g., en, de, fr)')
    parser.add_argument('--list', action='store_true', help='List available transcripts')

    args = parser.parse_args()

    video_id = extract_video_id(args.video)

    if args.list:
        list_transcripts(video_id)
    else:
        languages = [args.lang] if args.lang else None
        transcript = fetch_transcript(video_id, languages)
        print(transcript)


if __name__ == '__main__':
    main()
