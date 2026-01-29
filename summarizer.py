import re


def format_transcript(transcript: str) -> str:
    """Format the transcript with proper paragraphs - NO AI, just formatting."""
    # Split into sentences (roughly)
    text = transcript.strip()

    # Add paragraph breaks every 3-4 sentences for readability
    sentences = re.split(r'(?<=[.!?])\s+', text)

    paragraphs = []
    current = []

    for i, sentence in enumerate(sentences):
        current.append(sentence)
        # Create paragraph every 4 sentences or at natural breaks
        if len(current) >= 4:
            paragraphs.append(' '.join(current))
            current = []

    if current:
        paragraphs.append(' '.join(current))

    return '\n\n'.join(paragraphs)


def process_transcript(transcript: str) -> dict:
    """Process transcript - just formatting, no AI."""
    formatted = format_transcript(transcript)

    return {
        "summary": "*No AI summary - transcript only mode for speed*",
        "notes": formatted
    }
