import click

from core import crawler


@click.command()
@click.argument("url", type=str)
@click.argument("dst_filepath", type=click.Path(), default="google_ads_data.csv")
@click.option("--limit", "-l", type=int, default=10, help="Limit for page crawling.")
def crawler_cli(url: str, limit: int, dst_filepath: str) -> None:
    """Command line interface for crawler URL and saves processed data & summary to DST_FILEPATH in csv format"""
    crawler(url, limit, dst_filepath)


if __name__ == "__main__":
    crawler_cli()
