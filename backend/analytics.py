"""
Analytics engine — computes stats from parsed messages and caches to JSON.
"""

import json
import re
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Optional

from config import settings

# Simple English + Hindi stop words to exclude from word counts
STOP_WORDS = {
    "the", "a", "an", "is", "it", "in", "on", "at", "to", "for", "of", "and",
    "or", "but", "not", "this", "that", "i", "you", "he", "she", "we", "they",
    "me", "my", "your", "our", "his", "her", "was", "are", "be", "been", "have",
    "has", "had", "do", "did", "will", "would", "can", "could", "should", "just",
    "so", "up", "out", "no", "yes", "ok", "okay", "hi", "hello", "bye",
    # common Hinglish
    "hai", "ho", "hain", "tha", "thi", "the", "ko", "se", "ne", "ka", "ki",
    "ke", "kya", "bhi", "nahi", "nhi", "toh", "ab", "aur", "haan", "na",
    "ek", "ye", "wo", "woh", "mera", "tera", "apna", "koi", "kuch", "agar",
    "par", "pe", "mai", "mein", "tu", "tum", "aap", "hum", "yaar", "bhai",
}

EMOJI_PATTERN = re.compile(
    "["
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F300-\U0001F5FF"  # symbols & pictographs
    "\U0001F680-\U0001F6FF"  # transport & map
    "\U0001F1E0-\U0001F1FF"  # flags
    "\U00002700-\U000027BF"  # dingbats
    "\U0001F900-\U0001F9FF"  # supplemental symbols
    "\U00002600-\U000026FF"  # misc symbols
    "\u2764\u2665\u2661"     # hearts
    "]+",
    flags=re.UNICODE,
)


def _extract_emojis(text: str) -> list[str]:
    return EMOJI_PATTERN.findall(text)


def _words(text: str) -> list[str]:
    cleaned = EMOJI_PATTERN.sub(" ", text.lower())
    tokens = re.findall(r"\b[a-zA-Z\u0900-\u097F]{2,}\b", cleaned)
    return [t for t in tokens if t not in STOP_WORDS]


def _parse_ts(iso: Optional[str]) -> Optional[datetime]:
    if not iso:
        return None
    try:
        return datetime.fromisoformat(iso)
    except ValueError:
        return None


def compute_analytics(messages: list[dict]) -> dict:
    """
    Compute full analytics from the message list and write to JSON.
    Returns the analytics dict.
    """
    if not messages:
        return {}

    u1, u2 = settings.user1_name, settings.user2_name

    msg_count: dict[str, int] = {u1: 0, u2: 0}
    char_count: dict[str, int] = {u1: 0, u2: 0}
    emoji_counter: Counter = Counter()
    word_counter: dict[str, Counter] = {u1: Counter(), u2: Counter()}
    initiations: dict[str, int] = {u1: 0, u2: 0}
    response_times_sec: list[float] = []
    hourly: dict[str, list[int]] = {u1: [0] * 24, u2: [0] * 24}
    monthly: dict[str, dict[str, int]] = {u1: {}, u2: {}}

    prev_msg: Optional[dict] = None

    for msg in messages:
        sender = msg["sender"]
        text = msg["message"]
        ts = _parse_ts(msg.get("timestamp_iso"))

        if sender not in (u1, u2):
            continue

        msg_count[sender] += 1
        char_count[sender] += len(text)
        word_counter[sender].update(_words(text))

        for emoji in _extract_emojis(text):
            emoji_counter[emoji] += 1

        if ts:
            hour = ts.hour
            hourly[sender][hour] += 1
            month_key = ts.strftime("%Y-%m")
            monthly[sender][month_key] = monthly[sender].get(month_key, 0) + 1

        # Initiations: sender switches from the other person after a gap
        if prev_msg and prev_msg["sender"] != sender:
            prev_ts = _parse_ts(prev_msg.get("timestamp_iso"))
            if ts and prev_ts:
                delta = (ts - prev_ts).total_seconds()
                if delta >= 0:
                    # Response time (cap at 6 hours for meaningful responses)
                    if delta <= 21600:
                        response_times_sec.append(delta)
                    # Initiation if gap > 3 hours
                    if delta > 10800:
                        initiations[sender] += 1

        prev_msg = msg

    # Compute response time stats
    rt_stats: dict = {}
    if response_times_sec:
        sorted_rt = sorted(response_times_sec)
        n = len(sorted_rt)
        rt_stats = {
            "avg_seconds": round(sum(sorted_rt) / n),
            "median_seconds": round(sorted_rt[n // 2]),
            "min_seconds": round(sorted_rt[0]),
            "max_seconds": round(sorted_rt[-1]),
            "sample_count": n,
        }

    total = sum(msg_count.values()) or 1

    analytics = {
        "message_count": msg_count,
        "character_count": char_count,
        "message_percentage": {
            k: round(v / total * 100, 1) for k, v in msg_count.items()
        },
        "top_emojis": dict(emoji_counter.most_common(15)),
        "top_words": {
            u1: dict(word_counter[u1].most_common(20)),
            u2: dict(word_counter[u2].most_common(20)),
        },
        "response_time": rt_stats,
        "initiations": initiations,
        "activity_by_hour": hourly,
        "messages_by_month": monthly,
        "total_messages": sum(msg_count.values()),
    }

    _save_analytics(analytics)
    return analytics


def _save_analytics(data: dict) -> None:
    with open(settings.analytics_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_analytics() -> dict:
    path = Path(settings.analytics_file)
    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)
