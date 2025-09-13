import sys
import json
import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add src to path
current_file = Path(__file__).resolve()
project_root = current_file.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from wikipedia_ai_scraper import WikipediaScraper, OptimizedProcessor
from openai import OpenAI


async def main():
    print("🚀 Wikipedia AI Scraper Test")
    print("=" * 40)

    # Test URLs - you can modify these
    test_urls = [
        "https://en.wikipedia.org/wiki/Agentic_AI",
        "https://en.wikipedia.org/wiki/Reinforcement_learning",
        "https://en.wikipedia.org/wiki/Machine_learning",
        "https://en.wikipedia.org/wiki/Deep_learning",
        "https://en.wikipedia.org/wiki/Natural_language_processing"
    ]

    print(f"📄 Testing with {len(test_urls)} Wikipedia articles:")

    # Step 1: Scrape articles
    print(f"\n📥 Scraping articles...")
    scraper = WikipediaScraper(test_urls)
    articles = await scraper.scrape_multiple()

    # Display scraping results
    successful_articles = [a for a in articles if a['success']]
    print(f"✅ Successfully scraped: {len(successful_articles)}/{len(articles)} articles")

    for article in articles:
        status = "✅" if article['success'] else "❌"
        title = article.get('title', 'Unknown')
        content_length = len(article.get('raw_content', ''))
        print(f"  {status} {title}: {content_length:,} characters")

    if not successful_articles:
        print("❌ No articles were successfully scraped. Exiting.")
        return

    # Step 2: Process with AI
    print(f"\n🤖 Processing articles with AI...")

    try:
        client = OpenAI()
        processor = OptimizedProcessor(client)

        structured_outputs = processor.batch_extract(successful_articles)

        # Display AI processing results
        print(f"🎯 AI Analysis Complete! Found {len(structured_outputs)} topics:")
        print("=" * 50)
        list_of_questions = [
            "What is the evolution for Reinforcement Learning?",
            "How is machine learning and deep learning related?",
            "Are agentic AI related to natural language processing?",
            "How should I connect reinforcement learning with deep learning?"
        ]
        results = processor.demonstrate_function_calling(structured_outputs, list_of_questions)
        print(results)


        # Save results to JSON
        output_file = project_root / "test_results.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            # Convert results to JSON-serializable format
            json_results = {}
            for topic_name, topic_data in structured_outputs.items():
                json_results[topic_name] = {
                    'summary': topic_data.summary,
                    'evolution_timeline': getattr(topic_data, 'evolution_timeline', ''),
                    'key_innovations': getattr(topic_data, 'key_innovations', ''),
                    'major_contributors': getattr(topic_data, 'major_contributors', ''),
                    'main_techniques': topic_data.main_techniques,
                    'applications': getattr(topic_data, 'applications', [])
                }
            json.dump(json_results, f, indent=2, ensure_ascii=False)

        print(f"\n💾 Results saved to: {output_file}")

    except Exception as e:
        print(f"❌ AI processing failed: {e}")
        print("💡 Make sure your OpenAI API key is valid and you have credits available")

    print(f"\n🎉 Test completed!")


if __name__ == "__main__":
    asyncio.run(main())