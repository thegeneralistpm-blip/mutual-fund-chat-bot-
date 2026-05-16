import asyncio
import logging
from playwright.async_api import async_playwright
import random
import json
import os

logger = logging.getLogger(__name__)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
]

async def fetch_html(url: str, max_retries: int = 3) -> str:
    """Fetches JS-rendered HTML from a URL using Playwright with retries."""
    for attempt in range(max_retries):
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                user_agent = random.choice(USER_AGENTS)
                context = await browser.new_context(user_agent=user_agent)
                page = await context.new_page()
                
                logger.info(f"Navigating to {url} (Attempt {attempt+1}/{max_retries})")
                await page.goto(url, wait_until="networkidle", timeout=30000)
                
                # Scroll a bit to trigger lazy loading if needed
                await page.evaluate("window.scrollBy(0, 1000)")
                await asyncio.sleep(2)
                
                html = await page.content()
                await browser.close()
                
                # Small delay to respect server
                await asyncio.sleep(random.uniform(2, 4))
                return html
                
        except Exception as e:
            logger.warning(f"Error fetching {url}: {e}")
            if attempt < max_retries - 1:
                wait_time = (3 ** attempt) * 5  # 5s, 15s, 45s
                logger.info(f"Retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)
            else:
                logger.error(f"Failed to fetch {url} after {max_retries} attempts.")
                return None

async def scrape_groww_urls(urls: dict) -> dict:
    """Scrape a list of URLs and return a dictionary of url -> html."""
    results = {}
    for name, url in urls.items():
        html = await fetch_html(url)
        results[name] = {"url": url, "html": html}
    return results

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    urls = {
        "hdfc_mid_cap": "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth"
    }
    results = asyncio.run(scrape_groww_urls(urls))
    if results["hdfc_mid_cap"]["html"]:
        print("Successfully scraped HDFC Mid Cap page.")
