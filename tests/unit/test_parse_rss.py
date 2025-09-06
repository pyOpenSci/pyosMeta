from pyosmeta.parse_rss import fetch_rss_feed_as_stubs, parse_rss_feed


def test_rss_feed_parse(rss_feed_url):
    feed = parse_rss_feed(rss_feed_url)
    assert feed is not None
    assert len(feed) > 0
    for entry in feed:
        assert isinstance(entry, dict)
        assert "title" in entry
        assert "link" in entry
        assert "summary" in entry


def test_fetch_rss_feed_as_stubs(rss_feed_url):
    stubs = fetch_rss_feed_as_stubs(rss_feed_url)
    assert isinstance(stubs, dict)
    assert len(stubs) > 0
    for filename, content in stubs.items():
        assert filename.endswith(".md")
        assert isinstance(content, str)
        assert "title:" in content
        assert "excerpt:" in content
        assert "link:" in content
