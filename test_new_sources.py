"""Тестирование новых RSS источников"""
import feedparser

# Потенциальные источники для проверки
SOURCES_TO_TEST = [
    # Агро/Commodities
    ("AgWeb", "https://www.agweb.com/rss/news", ["Agriculture"]),
    ("Farm Progress", "https://www.farmprogress.com/rss.xml", ["Agriculture"]),
    ("Farms.com", "https://www.farms.com/FarmsPages/RSS/FarmsNews.xml", ["Agriculture"]),
    ("USDA NASS", "https://www.nass.usda.gov/rss/releases.xml", ["Agriculture"]),
    ("DTN Ag News", "https://www.dtnpf.com/agriculture/web/ag/news/rss", ["Agriculture"]),

    # Trade Finance / Commodities
    ("Commodity-TV", "https://www.commodity-tv.com/api/feeds/rss/", ["Agriculture", "RWA"]),
    ("Tradologie", "https://www.tradologie.com/feed", ["Agriculture", "RWA"]),
    ("Oilprice", "https://oilprice.com/rss/main", ["RWA"]),

    # RWA / Tokenization
    ("CryptoSlate RWA", "https://cryptoslate.com/feed/?post_type=rwa", ["RWA"]),
    ("CoinDesk RWA", "https://www.coindesk.com/arc/outboundfeeds/rss/?outputType=xml&tags=real-world-assets", ["RWA"]),
    ("Security Token Market", "https://stomarket.com/feed", ["RWA"]),

    # Kazakhstan / CIS
    ("Newsline.kz", "https://newsline.kz/rss", ["Agriculture"]),
    ("Time.kz", "https://time.kz/rss", ["Agriculture"]),
    ("Kazpravda", "https://kazpravda.kz/en/rss", ["Agriculture"]),

    # General Finance
    ("Financial Times", "https://www.ft.com/rss/home", ["Mainstream"]),
    ("Investing.com Commodities", "https://www.investing.com/rss/news_14.rss", ["RWA", "Agriculture"]),
]

print("=" * 70)
print("TESTING RSS FEEDS")
print("=" * 70)

working_sources = []

for name, url, verticals in SOURCES_TO_TEST:
    print(f"\n{name}")
    print(f"  URL: {url}")

    try:
        feed = feedparser.parse(url)

        if feed.bozo and not feed.entries:
            print(f"  [FAIL] ERROR: {feed.bozo_exception}")
            continue

        if not feed.entries:
            print(f"  [FAIL] NO ENTRIES")
            continue

        print(f"  [OK] {len(feed.entries)} articles")
        print(f"  Latest: {feed.entries[0].get('title', 'N/A')[:60]}...")

        working_sources.append({
            "name": name,
            "url": url,
            "verticals": verticals
        })

    except Exception as e:
        print(f"  [FAIL] EXCEPTION: {e}")

print("\n" + "=" * 70)
print(f"WORKING SOURCES: {len(working_sources)}/{len(SOURCES_TO_TEST)}")
print("=" * 70)

for s in working_sources:
    print(f"  - {s['name']} ({', '.join(s['verticals'])})")

# Сохраняем рабочие источники
import json
with open("new_sources.json", "w", encoding="utf-8") as f:
    json.dump({"sources": working_sources}, f, indent=2, ensure_ascii=False)

print(f"\nСохранено в new_sources.json")
