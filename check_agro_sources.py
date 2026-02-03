"""Проверка что приходит с аграрных источников"""
import feedparser

AGRO_SOURCES = [
    ("The Astana Times", "https://astanatimes.com/feed/"),
    ("World Grain", "https://www.world-grain.com/rss"),
    ("Romania Insider", "https://www.romania-insider.com/feed"),
    ("Grain Central", "https://www.graincentral.com/feed/"),
]

for name, url in AGRO_SOURCES:
    print(f"\n{'='*50}")
    print(f"SOURCE: {name}")
    print(f"URL: {url}")
    print('='*50)

    try:
        feed = feedparser.parse(url)

        if feed.bozo:
            print(f"ERROR: {feed.bozo_exception}")
            continue

        print(f"Total entries: {len(feed.entries)}")
        print(f"\nLatest 5 articles:")

        for i, entry in enumerate(feed.entries[:5], 1):
            title = entry.get('title', 'No title')
            published = entry.get('published', 'No date')
            print(f"\n{i}. {title}")
            print(f"   Date: {published}")

    except Exception as e:
        print(f"EXCEPTION: {e}")
