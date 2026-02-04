"""
crawl_listopia.py

This script crawls a Goodreads Listopia list page (e.g. "Best Books Ever"),
collects book detail URLs, visits each book page, extracts structured book
information, and saves the results into a JSONL file.

Features:
- Pagination support
- Polite crawling with random delays
- JSON-LD + HTML fallback parsing
- Resume capability (skip already crawled books)
- Failed URL logging
"""

import json
import random
import re
import time
from dataclasses import dataclass
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm


# ============================================================
# Configuration
# ============================================================

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0 Safari/537.36"
    )
}

BASE_URL = "https://www.goodreads.com"

YEAR_RE = re.compile(r"\b(18|19|20)\d{2}\b")
PAGES_RE = re.compile(r"(\d+)\s+pages", re.IGNORECASE)

DATA_DIR = Path("data/raw")
DATA_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_JSONL = DATA_DIR / "goodreads_books.jsonl"
FAILED_URLS = DATA_DIR / "failed_urls.txt"


# ============================================================
# HTTP helpers
# ============================================================

def fetch_html(url: str, timeout: int = 25, retries: int = 3) -> str:
    """
    Fetch HTML content from a URL with retry support.
    """
    last_error = None
    for _ in range(retries):
        try:
            response = requests.get(url, headers=HEADERS, timeout=timeout)
            response.raise_for_status()
            return response.text
        except Exception as e:
            last_error = e
            time.sleep(random.uniform(1.0, 2.0))
    raise RuntimeError(f"Failed to fetch {url}: {last_error}")


def polite_sleep(min_seconds: float = 1.0, max_seconds: float = 3.0) -> None:
    """
    Sleep for a random duration to avoid hitting rate limits.
    """
    time.sleep(random.uniform(min_seconds, max_seconds))


# ============================================================
# Storage helpers
# ============================================================

def load_existing_urls(jsonl_path: Path) -> set[str]:
    """
    Load already crawled book URLs from an existing JSONL file.
    Used to support resume-after-interruption.
    """
    if not jsonl_path.exists():
        return set()

    urls = set()
    with jsonl_path.open("r", encoding="utf-8") as f:
        for line in f:
            try:
                obj = json.loads(line)
                if "book_url" in obj:
                    urls.add(obj["book_url"])
            except json.JSONDecodeError:
                continue
    return urls


def append_jsonl(path: Path, record: dict) -> None:
    """
    Append a single JSON record to a JSONL file.
    """
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def log_failed_url(path: Path, url: str, reason: str = "") -> None:
    """
    Log failed URLs for later inspection or re-crawling.
    """
    with path.open("a", encoding="utf-8") as f:
        f.write(f"{url}\t{reason}\n")


# ============================================================
# Listopia: collect book URLs
# ============================================================

def build_listopia_page_url(list_url: str, page: int) -> str:
    """
    Build paginated Listopia URL.
    """
    if "?" in list_url:
        return f"{list_url}&page={page}"
    return f"{list_url}?page={page}"


def extract_book_urls_from_list_page(html: str) -> list[str]:
    """
    Extract book detail URLs from a Listopia page.
    """
    soup = BeautifulSoup(html, "lxml")
    urls = []

    for a in soup.select("a.bookTitle"):
        href = a.get("href", "")
        if href.startswith("/book/show/"):
            urls.append(BASE_URL + href.split("?")[0])

    return list(dict.fromkeys(urls))


def collect_book_urls(
    list_url: str,
    target_count: int = 500,
    max_pages: int = 60
) -> list[str]:
    """
    Collect book URLs from Listopia pages until target_count is reached.
    """
    collected = []

    for page in range(1, max_pages + 1):
        page_url = build_listopia_page_url(list_url, page)
        html = fetch_html(page_url)
        page_urls = extract_book_urls_from_list_page(html)

        if not page_urls:
            break

        for url in page_urls:
            if url not in collected:
                collected.append(url)
            if len(collected) >= target_count:
                return collected

        polite_sleep(0.8, 2.0)

    return collected


# ============================================================
# Book detail parsing (JSON-LD + HTML fallback)
# ============================================================

def extract_jsonld_blocks(soup: BeautifulSoup) -> list[dict]:
    """
    Extract all JSON-LD blocks from a page.
    """
    blocks = []
    for tag in soup.select('script[type="application/ld+json"]'):
        raw = tag.get_text(strip=True)
        if not raw:
            continue
        try:
            data = json.loads(raw)
            if isinstance(data, list):
                blocks.extend([x for x in data if isinstance(x, dict)])
            elif isinstance(data, dict):
                blocks.append(data)
        except json.JSONDecodeError:
            continue
    return blocks


def select_book_jsonld(blocks: list[dict]) -> dict | None:
    """
    Select the JSON-LD block that represents a Book.
    """
    for block in blocks:
        if str(block.get("@type", "")).lower() == "book":
            return block

    for block in blocks:
        if "aggregateRating" in block and "author" in block:
            return block

    return None


def parse_book_from_jsonld(book: dict) -> dict:
    """
    Parse core book metadata from JSON-LD.
    """
    author = ""
    a = book.get("author")
    if isinstance(a, dict):
        author = a.get("name", "")
    elif isinstance(a, list) and a:
        author = a[0].get("name", "") if isinstance(a[0], dict) else str(a[0])

    rating = ""
    rating_count = ""
    ar = book.get("aggregateRating")
    if isinstance(ar, dict):
        rating = str(ar.get("ratingValue", ""))
        rating_count = str(ar.get("ratingCount", ""))

    image = book.get("image", "")
    if isinstance(image, list) and image:
        image = image[0]

    return {
        "title": book.get("name", ""),
        "author": author,
        "rating": rating,
        "rating_count": rating_count,
        "description": re.sub(r"\s+", " ", book.get("description", "")).strip(),
        "isbn": book.get("isbn", ""),
        "image": image,
        "url_from_jsonld": book.get("url") or book.get("@id", ""),
    }


def extract_pages(soup: BeautifulSoup) -> int | None:
    text = soup.get_text(" ", strip=True)
    match = PAGES_RE.search(text)
    return int(match.group(1)) if match else None


def extract_published_year(soup: BeautifulSoup) -> int | None:
    node = soup.select_one(".TruncatedContent_text--small")
    if node:
        match = YEAR_RE.search(node.get_text(" ", strip=True))
        if match:
            return int(match.group(0))
    return None


def extract_language(soup: BeautifulSoup) -> str:
    for div in soup.select("div.TruncatedContent_text--small"):
        text = div.get_text(strip=True)
        if text.isalpha() and 3 <= len(text) <= 15:
            return text
    return ""


def extract_genres(soup: BeautifulSoup, top_k: int = 5) -> list[str]:
    genres = []
    for span in soup.select("a.Button.Button--tag span.Button__labelItem"):
        genres.append(span.get_text(strip=True))
    return list(dict.fromkeys(genres))[:top_k]


def parse_full_book(book_url: str) -> dict:
    html = fetch_html(book_url)
    soup = BeautifulSoup(html, "lxml")

    blocks = extract_jsonld_blocks(soup)
    book_json = select_book_jsonld(blocks)

    data = parse_book_from_jsonld(book_json) if book_json else {}
    data["book_url"] = book_url
    data["pages"] = extract_pages(soup)
    data["published_year"] = extract_published_year(soup)
    data["language"] = extract_language(soup)
    data["genres"] = extract_genres(soup)

    return data


# ============================================================
# Main crawl pipeline
# ============================================================

@dataclass
class CrawlConfig:
    list_url: str = "https://www.goodreads.com/list/show/1.Best_Books_Ever"
    target_books: int = 500
    max_pages: int = 60
    sleep_min: float = 1.2
    sleep_max: float = 3.0


def main():
    config = CrawlConfig()

    print(f"List URL: {config.list_url}")
    print(f"Target number of books: {config.target_books}")
    print(f"Output file: {OUTPUT_JSONL}")

    seen_urls = load_existing_urls(OUTPUT_JSONL)
    print(f"Already crawled books: {len(seen_urls)}")

    print("\n[1/2] Collecting book URLs from Listopia...")
    book_urls = collect_book_urls(
        config.list_url,
        target_count=config.target_books,
        max_pages=config.max_pages,
    )

    todo_urls = [u for u in book_urls if u not in seen_urls]
    print(f"Books to crawl: {len(todo_urls)}")

    print("\n[2/2] Crawling book detail pages...")
    for url in tqdm(todo_urls, desc="Books"):
        try:
            record = parse_full_book(url)
            append_jsonl(OUTPUT_JSONL, record)
        except Exception as e:
            log_failed_url(FAILED_URLS, url, str(e))
        polite_sleep(config.sleep_min, config.sleep_max)

    print("\nCrawling completed.")
    print(f"Results saved to: {OUTPUT_JSONL}")
    print(f"Failed URLs logged to: {FAILED_URLS}")


if __name__ == "__main__":
    main()