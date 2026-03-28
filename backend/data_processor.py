"""
WhatsApp chat parser.
Handles iOS format: [DD/MM/YY, HH:MM:SS AM/PM] Sender: message
Also handles multi-line messages and cleans media/system messages.
"""

import re
import json
from datetime import datetime
from pathlib import Path
from typing import Optional
from config import settings

# iOS WhatsApp format: [25/06/25, 11:57:13 AM] Sender Name: message
LINE_PATTERN = re.compile(
    r"^\[(\d{1,2}/\d{1,2}/\d{2,4}),\s+(\d{1,2}:\d{2}:\d{2}\s*[APap][Mm])\]\s+([^:]+?):\s+(.*)"
)

# Android format fallback: 25/06/2025, 11:57 - Sender: message
LINE_PATTERN_ANDROID = re.compile(
    r"^(\d{1,2}/\d{1,2}/\d{2,4}),\s+(\d{1,2}:\d{2})\s*-\s+([^:]+?):\s+(.*)"
)

# Media / system message patterns to drop
SKIP_PATTERNS = [
    re.compile(r"^\u200e?(image|video|audio|sticker|document|GIF|Contact card) omitted$", re.IGNORECASE),
    re.compile(r"^\u200e?Messages and calls are end-to-end encrypted", re.IGNORECASE),
    re.compile(r"^\u200e?This message was deleted", re.IGNORECASE),
    re.compile(r"^\u200e?You deleted this message", re.IGNORECASE),
    re.compile(r"^\u200e?<Media omitted>", re.IGNORECASE),
    re.compile(r"^\u200e?null$", re.IGNORECASE),
    re.compile(r"^\u200e?Missed voice call", re.IGNORECASE),
    re.compile(r"^\u200e?Missed video call", re.IGNORECASE),
]


def _normalize_sender(name: str) -> str:
    """Normalize sender name: 'Krishna❤️' → 'Krishna', 'Shivang Singh' → 'Shivang'."""
    name = name.strip()
    # Map known names
    if "krishna" in name.lower():
        return settings.user2_name
    if "shivang" in name.lower():
        return settings.user1_name
    return name


def _is_skippable(text: str) -> bool:
    clean = text.strip().lstrip("\u200e")
    for pattern in SKIP_PATTERNS:
        if pattern.match(clean):
            return True
    return False


def _parse_timestamp(date_str: str, time_str: str) -> Optional[datetime]:
    """Parse date+time into a datetime object."""
    # Normalize AM/PM spacing
    time_str = re.sub(r"\s+", " ", time_str.strip())
    formats = [
        "%d/%m/%y, %I:%M:%S %p",
        "%d/%m/%Y, %I:%M:%S %p",
        "%m/%d/%y, %I:%M:%S %p",
        "%m/%d/%Y, %I:%M:%S %p",
        "%d/%m/%y, %I:%M %p",
        "%d/%m/%Y, %I:%M %p",
    ]
    combined = f"{date_str.strip()}, {time_str}"
    for fmt in formats:
        try:
            return datetime.strptime(combined, fmt)
        except ValueError:
            continue
    return None


def process_whatsapp_chat(text: str) -> list[dict]:
    """
    Parse raw WhatsApp export text into a list of message dicts.
    Each dict: {date, time, sender, message, timestamp_iso}
    """
    lines = text.splitlines()
    messages = []
    current: Optional[dict] = None

    for line in lines:
        # Try iOS format first
        m = LINE_PATTERN.match(line)
        if not m:
            m = LINE_PATTERN_ANDROID.match(line)

        if m:
            # Save previous message
            if current:
                messages.append(current)

            date_str, time_str, sender_raw, msg_text = m.groups()
            msg_text = msg_text.strip().lstrip("\u200e")

            if _is_skippable(msg_text):
                current = None
                continue

            ts = _parse_timestamp(date_str, time_str)
            current = {
                "date": date_str.strip(),
                "time": time_str.strip(),
                "sender": _normalize_sender(sender_raw),
                "message": msg_text,
                "timestamp_iso": ts.isoformat() if ts else None,
            }
        else:
            # Continuation line — append to current message
            if current:
                stripped = line.strip().lstrip("\u200e")
                if stripped:
                    current["message"] += "\n" + stripped

    if current:
        messages.append(current)

    return messages


def chunk_messages(messages: list[dict], chunk_size: int = None) -> list[dict]:
    """
    Group messages into chunks of `chunk_size` for embedding.
    Each chunk has a combined text + metadata.
    """
    if chunk_size is None:
        chunk_size = settings.chunk_size

    chunks = []
    for i in range(0, len(messages), chunk_size):
        group = messages[i : i + chunk_size]
        text_lines = [f"{m['sender']}: {m['message']}" for m in group]
        combined = "\n".join(text_lines)

        start_ts = group[0]["timestamp_iso"] or group[0]["date"]
        end_ts = group[-1]["timestamp_iso"] or group[-1]["date"]
        senders = list({m["sender"] for m in group})

        chunks.append(
            {
                "id": f"chunk_{i}",
                "text": combined,
                "start_time": start_ts,
                "end_time": end_ts,
                "senders": senders,
                "message_count": len(group),
            }
        )
    return chunks


def save_messages(messages: list[dict], path: str = None) -> None:
    path = path or f"{settings.data_dir}/messages.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)


def load_messages(path: str = None) -> list[dict]:
    path = path or f"{settings.data_dir}/messages.json"
    if not Path(path).exists():
        return []
    with open(path, encoding="utf-8") as f:
        return json.load(f)
