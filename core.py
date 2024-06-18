import os

import cloudscraper
import pandas as pd
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from openai import OpenAI

from const import CrawlerResultColumn

load_dotenv()

client = OpenAI(api_key=os.getenv("API_KEY"))


def generate_summary(content: str) -> str:
    """Generates summary by openAI.

    Args:
        content: Source content to generate summary.

    Returns:
        response: Summary.

    """
    system = [{"role": "system", "content": "You are Summary AI."}]
    user = [{"role": "user", "content": f"Summarize this briefly:\n\n{content}"}]
    chat_history = []

    response = client.chat.completions.create(
        messages=system + chat_history + user,
        model="gpt-3.5-turbo",
        max_tokens=500,
        top_p=0.9,
    )
    return response.choices[0].message.content


def get_meta_tags(page_url: str, scraper: dict) -> (str, str):
    """Gets metadata for the tags.

    Args:
        page_url: Link to page url.
        scraper: cloudscraper.

    Returns:
        title: Title of pages.
        description: Description for the pages.

    """
    response = scraper.get(page_url)
    soup = BeautifulSoup(response.content, "html.parser")
    title = soup.find("title").text if soup.find("title") else "No title"
    title_tag = soup.find("h1", class_="product_title entry-title")
    title = title_tag.text.strip() if title_tag else title
    description_tag = soup.find("div", class_="woocommerce-product-details__short-description")
    description = description_tag.text.strip() if description_tag else "No description"
    print(f"Title: {title}, Description: {description}")
    return title, description


def crawl_website(url: str, limit: int) -> list:
    """Crawles pages of website.

    Args:
        url: Link to the base URL.
        limit: Count of processing pages.

    Returns:
        pages: sample uls to every single page.

    """
    scraper = cloudscraper.create_scraper()
    response = scraper.get(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    if response.status_code != 200:
        raise Exception(f"Failed to access {url}")

    soup = BeautifulSoup(response.content, "html.parser")
    pages = [url]

    for link in soup.find_all("a", class_="woocommerce-LoopProduct-link woocommerce-loop-product__link", href=True):
        href = link["href"]
        if href.startswith("/") and not href.startswith("//"):
            href = url + href
        if url in href and href not in pages:
            pages.append(href)
            if len(pages) >= limit:
                break

    return pages


def crawler(url: str, limit: int, dst_filepath: str) -> None:
    """Base processing for the generate summary and saves it to csv filepath.

    Args:
        url: Base url to website.
        limit: count of processing pages.
        dst_filepath: path to destination csv file.

    """
    pages = crawl_website(url, limit)
    scraper = cloudscraper.create_scraper()

    data = []
    for page in pages:
        print(f"Processing page: {page}")
        title, description = get_meta_tags(page, scraper)
        summary = generate_summary(description)
        data.append({
            CrawlerResultColumn.PAGE_URL: page,
            CrawlerResultColumn.TITLE: title,
            CrawlerResultColumn.DESCRIPTION: description,
            CrawlerResultColumn.SUMMARY: summary
        })

    df = pd.DataFrame(data)
    df.to_csv(dst_filepath, index=False, encoding="utf-8-sig")
    print(f"Data save to {dst_filepath}")
