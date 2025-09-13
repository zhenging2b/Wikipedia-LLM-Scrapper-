import asyncio
import time
import re
from typing import List, Dict, Any
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode
from crawl4ai.chunking_strategy import SlidingWindowChunking
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator

class WikipediaScraper:
  def __init__(self, base_urls: List[str]):
    self.base_urls = base_urls

  async def scrape_article(self, url: str) -> Dict[str, Any]:
    """Scrape a single Wikipedia article"""

    # Configure optimized crawling
    chunking_strategy = SlidingWindowChunking(
        window_size=1000,    # Optimal for LLM processing
        step=500            # 50% overlap for context preservation
    )

    config = CrawlerRunConfig(
        markdown_generator=DefaultMarkdownGenerator(),
        chunking_strategy=chunking_strategy,
        cache_mode=CacheMode.WRITE_ONLY,  # results of this crawl are saved to the cache
        page_timeout=15000,  # Faster timeout for efficiency
        verbose=False       # Reduce logging for speed
    )
    async with AsyncWebCrawler() as crawler:
      try:
        result = await crawler.arun(url=url, config=config)
        if result.success:
          raw_content = result.markdown.raw_markdown
          cleaned_content = self.clean_content(raw_content)
          return {
              "url": url,
              "title": result.metadata.get("title", "Unknown"),
              "raw_content": cleaned_content,
              "success": True
          }
        else:
          print(f"   ❌ Failed: {result.error_message}")
          return {
              "url": url,
              "title": "Unknown",
              "raw_content": result.error_message,
              "success": False,
          }
      except Exception as e:
        print(f"   ❌ Exception: {e}")
        return {
            "url": url,
            "title": "Unknown",
            "raw_content": str(e),
            "success": False,
        }


  async def scrape_multiple(self) -> List[Dict[str, Any]]:
    """Scrape all articles in the URL list"""
    results =[]
    start_time= time.time()
    for url in self.base_urls:
      print(f"⚡ Scraping: {url}")
      article_result = await self.scrape_article(url)
      results.append(article_result)
    elapsed = time.time() - start_time
    print(f"✅ Finished scraping {len(self.base_urls)} articles in {elapsed:.2f} seconds")

    return results

  def clean_content(self, raw_content: str) -> str:
    """Clean and preprocess scraped content"""
    text = raw_content

    # 1. Keep only from the first H1 (# Title) onwards
    match = re.search(r"^# .+", text, flags=re.MULTILINE)
    if match:
        text = text[match.start():]

    # 2. Remove navigation / sidebar / account / tools sections by keyword
    remove_keywords = [
        "Main menu", "Navigation", "Contribute", "Appearance", "Personal tools",
        "Pages for logged out editors", "Toggle the table of contents",
        "Tools", "Print/export", "In other projects",
        "Edit links", "Create account", "Log in", "Donate",
        "move to sidebar hide", "Search", "Width", "Color (beta)", "Actions",
    ]
    pattern = re.compile(rf"^.*({'|'.join(map(re.escape, remove_keywords))}).*$",
                         re.MULTILINE | re.IGNORECASE)
    text = pattern.sub("", text)

    # 3. Remove [edit] links
    text = re.sub(r"\[\[edit.*?\]\]", "", text, flags=re.IGNORECASE)


    # 4. Remove inline citation tooltips (#cite_note stuff)
    text = re.sub(r"\[\d+\]\(https:\/\/en\.wikipedia\.org\/wiki\/[^)]+#cite_note[^\)]*\)",
                  lambda m: "[" + re.search(r"\d+", m.group()).group() + "]",
                  text)

    # 5. Remove excess blank lines
    text = re.sub(r"\n{2,}", "\n\n", text)

    return text.strip()