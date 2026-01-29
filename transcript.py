import re
from youtube_transcript_api import YouTubeTranscriptApi


def extract_video_id(url: str) -> str:
    """Extract YouTube video ID from various URL formats."""
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})',
        r'(?:youtube\.com\/shorts\/)([a-zA-Z0-9_-]{11})',
        r'^([a-zA-Z0-9_-]{11})$'  # Direct video ID
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    raise ValueError(f"Could not extract video ID from URL: {url}")


def get_transcript(video_id: str) -> list[dict]:
    """Fetch transcript from YouTube."""
    api = YouTubeTranscriptApi()
    try:
        transcript = api.fetch(video_id)
        # Convert to list of dicts for compatibility
        return [{"text": snippet.text, "start": snippet.start, "duration": snippet.duration}
                for snippet in transcript]
    except Exception as e:
        error_msg = str(e).lower()
        if "disabled" in error_msg:
            raise ValueError("Transcripts are disabled for this video")
        elif "no transcript" in error_msg:
            raise ValueError("No transcript found for this video")
        else:
            raise ValueError(f"Failed to fetch transcript: {e}")


def clean_transcript(transcript: list[dict]) -> str:
    """Clean and format the transcript."""
    # Filler words to remove
    fillers = [
        r'\b(um|uh|er|ah|like|you know|i mean|basically|actually|literally)\b',
    ]

    # Combine all text segments
    full_text = ' '.join(segment['text'] for segment in transcript)

    # Remove filler words (case insensitive)
    for filler in fillers:
        full_text = re.sub(filler, '', full_text, flags=re.IGNORECASE)

    # Clean up whitespace
    full_text = re.sub(r'\s+', ' ', full_text).strip()

    # Fix common transcript issues
    full_text = re.sub(r'\s+([.,!?])', r'\1', full_text)  # Remove space before punctuation

    # Split into sentences and rejoin with proper formatting
    sentences = re.split(r'(?<=[.!?])\s+', full_text)

    # Group sentences into paragraphs (roughly 3-5 sentences each)
    paragraphs = []
    current_paragraph = []

    for sentence in sentences:
        current_paragraph.append(sentence)
        if len(current_paragraph) >= 4:
            paragraphs.append(' '.join(current_paragraph))
            current_paragraph = []

    if current_paragraph:
        paragraphs.append(' '.join(current_paragraph))

    return '\n\n'.join(paragraphs)


def get_clean_transcript(url: str) -> tuple[str, str]:
    """Main function to get and clean transcript from a YouTube URL.

    Returns:
        tuple: (video_id, cleaned_transcript)
    """
    video_id = extract_video_id(url)
    raw_transcript = get_transcript(video_id)
    cleaned = clean_transcript(raw_transcript)
    return video_id, cleaned
