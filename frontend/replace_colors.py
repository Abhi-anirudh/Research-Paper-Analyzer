import os
import re

CSS_DIR = r"c:\Users\aniru\.gemini\antigravity\scratch\research-paper-analyzer\frontend\src\app\components"

REPLACEMENTS = [
    (r"#6C63FF", "var(--accent)"),
    (r"(?i)#E8E6F0", "var(--text-primary)"),
    (r"(?i)#D4D2E0", "var(--text-primary)"),
    (r"(?i)#B8B5CC", "var(--text-secondary)"),
    (r"(?i)#9B97B0", "var(--text-secondary)"),
    (r"(?i)#C8C6D8", "var(--text-secondary)"),
    (r"(?i)#6B6880", "var(--text-muted)"),
    (r"(?i)#4A4760", "var(--text-dim)"),
    (r"(?i)#4ADE80", "var(--success)"),
    (r"(?i)#FBBF24", "var(--warning)"),
    (r"(?i)#FF5252", "var(--error)"),
    (r"(?i)rgba\(\s*22\s*,\s*20\s*,\s*35\s*,\s*[0-9.]+\s*\)", "var(--bg-card)"),
]

def replace_rgba_accent(match):
    alpha = float(match.group(1))
    perc = int(alpha * 100)
    return f"color-mix(in srgb, var(--accent) {perc}%, transparent)"

def process_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    for old, new in REPLACEMENTS:
        content = re.sub(old, new, content)

    # specially handle rgba for accent
    content = re.sub(r"(?i)rgba\(\s*108\s*,\s*99\s*,\s*255\s*,\s*([0-9.]+)\s*\)", replace_rgba_accent, content)
    # specially handle rgba for success
    content = re.sub(r"(?i)rgba\(\s*74\s*,\s*222\s*,\s*128\s*,\s*([0-9.]+)\s*\)", lambda m: f"color-mix(in srgb, var(--success) {int(float(m.group(1))*100)}%, transparent)", content)
    # specially handle rgba for warning
    content = re.sub(r"(?i)rgba\(\s*251\s*,\s*191\s*,\s*36\s*,\s*([0-9.]+)\s*\)", lambda m: f"color-mix(in srgb, var(--warning) {int(float(m.group(1))*100)}%, transparent)", content)
    # specially handle rgba for error
    content = re.sub(r"(?i)rgba\(\s*255\s*,\s*82\s*,\s*82\s*,\s*([0-9.]+)\s*\)", lambda m: f"color-mix(in srgb, var(--error) {int(float(m.group(1))*100)}%, transparent)", content)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

for root, dirs, files in os.walk(CSS_DIR):
    for fl in files:
        if fl.endswith(".css"):
            process_file(os.path.join(root, fl))

print("CSS variables applied everywhere.")
