"""Заполнение базы источниками - прямой метод"""
import os
from dotenv import load_dotenv
from notion_client import Client
import httpx

load_dotenv()

ALL_SOURCES = [
    {"name": "CoinDesk", "url": "https://www.coindesk.com/arc/outboundfeeds/rss/", "verticals": ["RWA", "DeFi"]},
    {"name": "The Block", "url": "https://www.theblock.co/rss.xml", "verticals": ["RWA", "DeFi"]},
    {"name": "The Defiant", "url": "https://thedefiant.io/feed", "verticals": ["RWA", "DeFi"]},
    {"name": "CryptoSlate", "url": "https://cryptoslate.com/feed/", "verticals": ["RWA", "DeFi"]},
    {"name": "Cointelegraph", "url": "https://cointelegraph.com/rss", "verticals": ["RWA", "DeFi"]},
    {"name": "Blockworks", "url": "https://blockworks.co/feed/", "verticals": ["RWA", "DeFi"]},
    {"name": "Decrypt", "url": "https://decrypt.co/feed", "verticals": ["RWA", "DeFi", "Mainstream"]},
    {"name": "CryptoSlate RWA", "url": "https://cryptoslate.com/feed/?post_type=rwa", "verticals": ["RWA"]},
    {"name": "CoinDesk RWA", "url": "https://www.coindesk.com/arc/outboundfeeds/rss/?outputType=xml&tags=real-world-assets", "verticals": ["RWA"]},
    {"name": "Farm Progress", "url": "https://www.farmprogress.com/rss.xml", "verticals": ["Agriculture"]},
    {"name": "Time.kz", "url": "https://time.kz/rss", "verticals": ["Agriculture"]},
    {"name": "Investing.com Commodities", "url": "https://www.investing.com/rss/news_14.rss", "verticals": ["RWA", "Agriculture"]},
    {"name": "Oilprice", "url": "https://oilprice.com/rss/main", "verticals": ["RWA"]},
    {"name": "Financial Times", "url": "https://www.ft.com/rss/home", "verticals": ["Mainstream"]},
    {"name": "TechCrunch Fintech", "url": "https://techcrunch.com/category/fintech/feed/", "verticals": ["Mainstream"]},
]

def main():
    api_key = os.getenv("NOTION_API_KEY")
    db_id = "2f77eb3fb6bb80808c76e64eec0b7523"

    http_client = httpx.Client(timeout=60.0)
    notion = Client(auth=api_key, client=http_client)

    print("=" * 60)
    print("FILLING NOTION DATABASE")
    print("=" * 60)

    # Сначала попробуем добавить одну запись чтобы узнать структуру ошибки
    print("\n[1] Testing with first source...")

    source = ALL_SOURCES[0]

    # Пробуем разные варианты названий полей
    field_variants = [
        # Точные названия из скриншота
        {"title": "Name", "url": "RSS URL", "multiselect": "Verticals", "checkbox": "Active"},
    ]

    for i, fields in enumerate(field_variants, 1):
        print(f"\n  Trying variant {i}: {fields}")
        try:
            props = {
                fields["title"]: {"title": [{"text": {"content": source["name"]}}]},
                fields["url"]: {"url": source["url"]},
                fields["multiselect"]: {"multi_select": [{"name": v} for v in source["verticals"]]},
                fields["checkbox"]: {"checkbox": True},
            }

            page = notion.pages.create(
                parent={"database_id": db_id},
                properties=props
            )
            print(f"  SUCCESS with variant {i}!")
            print(f"  Page created: {page['id']}")

            # Используем эти поля для остальных
            print(f"\n[2] Adding remaining {len(ALL_SOURCES)-1} sources...")

            for src in ALL_SOURCES[1:]:
                props = {
                    fields["title"]: {"title": [{"text": {"content": src["name"]}}]},
                    fields["url"]: {"url": src["url"]},
                    fields["multiselect"]: {"multi_select": [{"name": v} for v in src["verticals"]]},
                    fields["checkbox"]: {"checkbox": True},
                }
                notion.pages.create(parent={"database_id": db_id}, properties=props)
                print(f"    + {src['name']}")

            print(f"\n" + "=" * 60)
            print(f"DONE! Added {len(ALL_SOURCES)} sources")
            print("=" * 60)
            return

        except Exception as e:
            print(f"  Failed: {str(e)[:100]}")

    print("\nAll variants failed. Check database field names in Notion.")

    http_client.close()

if __name__ == "__main__":
    main()
