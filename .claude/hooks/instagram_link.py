#!/usr/bin/env python3
"""UserPromptSubmit hook: xabarda Instagram link bo'lsa, Claude'ga instagram-tahlil skillini ishlatishni eslatadi."""
import json
import re
import sys

data = json.load(sys.stdin)
links = re.findall(r"https?://(?:www\.)?instagram\.com/\S+", data.get("prompt", ""))
if links:
    ctx = (
        "Foydalanuvchi Instagram link yubordi: " + ", ".join(links) + ". "
        "instagram-tahlil skillini ishlat: har bir linkni scripts/insta_tahlil.py bilan yuklab ol, "
        "caption, transkript va kadrlarni ko'rib chiq, skilldagi shablon bo'yicha tahlil qil, "
        "goyalar/ papkasiga saqla. Link yonidagi izohi bo'lsa, o'shanga e'tibor ber."
    )
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext": ctx}}))
