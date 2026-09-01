#!/usr/bin/env python3
"""
Blogsphere Content Assistant – powered by GitHub Models (free tier)
Uses the OpenAI-compatible GitHub Models endpoint.
"""

import os
import sys
import argparse
from datetime import datetime
from pathlib import Path

# ── OpenAI SDK (used with GitHub Models base URL) ──
try:
    from openai import OpenAI
except ImportError:
    print("⚠️ openai package not installed. Run: pip install openai")
    sys.exit(1)

# ── Optional: Google Trends ──
try:
    from pytrends.request import TrendReq
except ImportError:
    TrendReq = None

# ── Paths ──
BASE_DIR = Path(__file__).resolve().parent.parent
RESEARCH_DIR = BASE_DIR / "content" / "research"
ARTICLES_DIR = BASE_DIR / "content" / "articles"
RESEARCH_DIR.mkdir(parents=True, exist_ok=True)
ARTICLES_DIR.mkdir(parents=True, exist_ok=True)

# ── Load .env ──
try:
    from dotenv import load_dotenv
    load_dotenv(BASE_DIR / ".env")
except ImportError:
    pass

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# ── GitHub Models client (OpenAI-compatible) ──
GITHUB_MODELS_BASE = "https://models.github.ai/inference/chat/completions"

def create_client():
    """Return an OpenAI client pointed at GitHub Models."""
    if not GITHUB_TOKEN:
        print("❌ GITHUB_TOKEN not found. Add it to your .env file.")
        print("   Get one at: https://github.com/settings/tokens")
        print("   (Models → Access: Read-only)")
        sys.exit(1)
    return OpenAI(
        base_url="https://models.github.ai/inference",
        api_key=GITHUB_TOKEN,
    )

# ────────────────────────────────────────────────────────
def get_trending_topics(niche="technology", count=5):
    """Return trending queries from Google Trends."""
    if TrendReq is None:
        print("⚠️ pytrends not installed. Skipping trending topics.")
        return []
    pytrends = TrendReq(hl='en-US', tz=360)
    pytrends.build_payload(kw_list=[niche], timeframe='today 3-m')
    related = pytrends.related_queries()
    rising = related.get(niche, {}).get('rising', None)
    if rising is not None:
        return rising.head(count)['query'].tolist()
    return []

def gather_research(keyword, num_sources=5):
    """Collect research material (placeholder — replace with a real search API)."""
    print(f"Gathering research for '{keyword}'…")
    sources = []
    for i in range(num_sources):
        sources.append({
            "title": f"Research source {i+1} for {keyword}",
            "text": f"Lorem ipsum dolor sit amet… (real content about {keyword})"
        })
    return sources

def generate_outline(topic, research_text):
    """Generate an article outline via GitHub Models."""
    client = create_client()
    prompt = f"""You are a helpful assistant for a writer.
Based on the following research about "{topic}", create a detailed article outline
with 5-7 clear sections. Each section title should be informative and engaging.

Research notes:
{research_text[:3000]}

Outline:"""
    response = client.chat.completions.create(
        model="openai/gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )
    outline_text = response.choices[0].message.content.strip()
    return [line.strip() for line in outline_text.split("\n") if line.strip()]

def generate_draft(topic, outline, research_text):
    """Generate a first draft via GitHub Models."""
    client = create_client()
    outline_str = "\n".join(outline)
    prompt = f"""Write a detailed first draft of an article on "{topic}".
Use the following outline and research notes. Write in a neutral, informative tone.
This is raw material for a human writer – it will be heavily edited and personalised later.
Do not invent statistics; if you don't know something, say so.

Outline:
{outline_str}

Research:
{research_text[:3000]}

Draft (at least 800 words):"""
    response = client.chat.completions.create(
        model="openai/gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8,
        max_tokens=2000,
    )
    return response.choices[0].message.content.strip()

def main():
    parser = argparse.ArgumentParser(description="Blogsphere Content Assistant (GitHub Models)")
    parser.add_argument("--topic", type=str, help="Article topic / keyword")
    parser.add_argument("--niche", type=str, default="technology", help="Niche for trending topics")
    parser.add_argument("--trending", action="store_true", help="Show trending topics and exit")
    parser.add_argument("--full", action="store_true", help="Run full pipeline: research, outline, draft")
    args = parser.parse_args()

    if args.trending:
        topics = get_trending_topics(args.niche)
        if topics:
            print("Trending topics:")
            for t in topics:
                print(f"  - {t}")
        else:
            print("No trending data available. Try another niche.")
        return

    if not args.topic:
        print("Please provide --topic 'Your Topic' or use --trending to see ideas.")
        return

    topic = args.topic
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    slug = topic.lower().replace(" ", "-").replace("'", "")

    # 1. Research
    sources = gather_research(topic)
    research_path = RESEARCH_DIR / f"{slug}_research_{timestamp}.md"
    with open(research_path, "w", encoding="utf-8") as f:
        f.write(f"# Research for: {topic}\n\n")
        for src in sources:
            f.write(f"## {src['title']}\n\n{src['text']}\n\n")
    print(f"✓ Research saved to {research_path}")

    if not args.full:
        print("Run with --full to generate outline and draft.")
        return

    # 2. Outline
    research_text = "\n\n".join([s['text'] for s in sources])
    outline = generate_outline(topic, research_text)
    print("✓ Outline generated:")
    for i, sec in enumerate(outline, 1):
        print(f"  {i}. {sec}")

    # 3. Draft
    draft = generate_draft(topic, outline, research_text)
    article_path = ARTICLES_DIR / f"{slug}_draft_{timestamp}.md"
    with open(article_path, "w", encoding="utf-8") as f:
        f.write(f"# {topic}\n\n")
        f.write(f"*Auto-generated draft – requires heavy human editing.*\n\n")
        f.write("## Outline\n")
        for i, sec in enumerate(outline, 1):
            f.write(f"{i}. {sec}\n")
        f.write("\n## First Draft\n\n")
        f.write(draft)
    print(f"✓ Draft saved to {article_path}")
    print("\n⏳ Now open the draft in PyCharm, rewrite it completely with your own experience and voice, then place the final Markdown in `content/articles/`.")

if __name__ == "__main__":
    main()