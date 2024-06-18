from unittest.mock import MagicMock, patch
import pandas as pd
from core import crawl_website, get_meta_tags, crawler
from const import CrawlerResultColumn


def test_crawl_website():
    url = "http://example.com"
    limit = 5
    pages = crawl_website(url, limit)
    assert len(pages) <= limit


def test_get_meta_tags():
    page_url = "http://example.com/page1"
    scraper = MagicMock()
    scraper.get.return_value.content = "<html><head><title>Page Title</title><meta name='description' content='Page Description'></head></html>"

    title, description = get_meta_tags(page_url, scraper)
    assert title == "Page Title"
    assert description == "Page Description"


@patch("core.generate_summary")
@patch("core.get_meta_tags")
@patch("core.crawl_website")
def test_crawler(mock_crawl_website, mock_get_meta_tags, mock_generate_summary):
    url = "http://example.com"
    limit = 2
    dst_filepath = "test.csv"
    mock_crawl_website.return_value = ["http://example.com/page1", "http://example.com/page2"]
    mock_get_meta_tags.side_effect = [("Page 1 Title", "Page 1 Description"), ("Page 2 Title", "Page 2 Description")]
    mock_generate_summary.side_effect = ["Summary 1", "Summary 2"]

    crawler(url, limit, dst_filepath)

    mock_crawl_website.assert_called_once_with(url, limit)
    assert mock_get_meta_tags.call_count == 2
    assert mock_generate_summary.call_count == 2

    df = pd.read_csv(dst_filepath)
    assert len(df) == 2
    assert df[CrawlerResultColumn.TITLE].tolist() == ["Page 1 Title", "Page 2 Title"]
    assert df[CrawlerResultColumn.DESCRIPTION].tolist() == ["Page 1 Description", "Page 2 Description"]
    assert df[CrawlerResultColumn.SUMMARY].tolist() == ["Summary 1", "Summary 2"]