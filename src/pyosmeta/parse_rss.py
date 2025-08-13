from pathlib import Path

import feedparser

from .utils_clean import slugify


def parse_rss_feed(url: str) -> list[dict]:
    """Fetch and parse an RSS feed from a URL."""
    parsed_feed = feedparser.parse(url)
    return [
        {key: entry.get(key) for key in entry.keys()}
        for entry in parsed_feed.entries
    ]


def make_md_stub(index: int, title: str, summary: str, link: str) -> str:
    """Create a Markdown stub for an entry."""
    return f'''
---
title: "{index}. {title}"
excerpt: "
  {summary}"
link:  {link}
btn_label: View Tutorial
btn_class: btn--success btn--large
---
'''


def fetch_rss_feed_as_stubs(url: str) -> dict[str, str]:
    """Fetch an RSS feed and return a dictionary of Markdown stubs.

    The keys of the dictionary are filenames, and the values are the Markdown content.
    """
    items = parse_rss_feed(url)

    stubs = {}
    for i, item in enumerate(items):
        title = item.get("title", None)
        if not title:
            # WARN
            continue
        filename = f"{i:02d}-{slugify(title)}.md"
        content = make_md_stub(
            index=i,
            title=title,
            summary=item.get("summary", ""),
            link=item.get("link", "#"),
        )
        stubs[filename] = content
    return stubs


def create_rss_feed_stubs(url: str, output_dir: str) -> None:
    """Create markdown stubs from an RSS feed URL into a directory."""
    stubs = fetch_rss_feed_as_stubs(url)
    for filename, content in stubs.items():
        # TODO: should we wipe existing files?
        path = Path(output_dir) / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            f.write(content)
