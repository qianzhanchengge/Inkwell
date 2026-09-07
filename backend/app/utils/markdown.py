"""Markdown 工具：转 HTML 与字数统计。"""
import re

import bleach
import markdown


def markdown_to_html(text: str) -> str:
    """Markdown 转 HTML，并用 bleach 过滤危险标签（防 XSS，§12.2）。"""
    raw_html = markdown.markdown(text or "", extensions=["extra", "codehilite", "tables"])
    allowed_tags = list(bleach.sanitizer.ALLOWED_TAGS) + [
        "p", "pre", "code", "h1", "h2", "h3", "h4", "h5", "h6",
        "table", "thead", "tbody", "tr", "th", "td", "blockquote",
        "hr", "img", "br", "span", "div",
    ]
    allowed_attrs = {
        **bleach.sanitizer.ALLOWED_ATTRIBUTES,
        "img": ["src", "alt", "title"],
        "a": ["href", "title", "target", "rel"],
        "code": ["class"],
        "span": ["class"],
    }
    return bleach.clean(raw_html, tags=allowed_tags, attributes=allowed_attrs, strip=True)


def count_words(text: str) -> int:
    """按中英文混合统计字数。"""
    if not text:
        return 0
    # 英文单词
    en_words = len(re.findall(r"[A-Za-z0-9_]+", text))
    # 中文字符
    cn_chars = len(re.findall(r"[\u4e00-\u9fff]", text))
    return en_words + cn_chars


def estimate_reading_time(word_count: int) -> int:
    """按每分钟约 300 字估算阅读分钟数。"""
    return max(1, round(word_count / 300))
