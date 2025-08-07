import click

from pyosmeta.parse_rss import create_rss_feed_stubs


@click.command()
@click.argument("url")
@click.argument("output_dir")
def main(url: str, output_dir: str):
    """Create markdown stubs from an RSS feed URL into a directory."""
    create_rss_feed_stubs(url, output_dir)


if __name__ == "__main__":
    main()
