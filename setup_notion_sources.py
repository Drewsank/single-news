"""Настройка базы Источники в Notion и добавление записей"""
import os
import json
from dotenv import load_dotenv
from notion_client import Client
import httpx

load_dotenv()

# Все источники (старые + новые рабочие)
ALL_SOURCES = [
    # Крипто/RWA (работающие)
    {"name": "CoinDesk", "url": "https://www.coindesk.com/arc/outboundfeeds/rss/", "verticals": ["RWA", "DeFi"]},
    {"name": "The Block", "url": "https://www.theblock.co/rss.xml", "verticals": ["RWA", "DeFi"]},
    {"name": "The Defiant", "url": "https://thedefiant.io/feed", "verticals": ["RWA", "DeFi"]},
    {"name": "CryptoSlate", "url": "https://cryptoslate.com/feed/", "verticals": ["RWA", "DeFi"]},
    {"name": "Cointelegraph", "url": "https://cointelegraph.com/rss", "verticals": ["RWA", "DeFi"]},
    {"name": "Blockworks", "url": "https://blockworks.co/feed/", "verticals": ["RWA", "DeFi"]},
    {"name": "Decrypt", "url": "https://decrypt.co/feed", "verticals": ["RWA", "DeFi", "Mainstream"]},

    # RWA специализированные (новые)
    {"name": "CryptoSlate RWA", "url": "https://cryptoslate.com/feed/?post_type=rwa", "verticals": ["RWA"]},
    {"name": "CoinDesk RWA", "url": "https://www.coindesk.com/arc/outboundfeeds/rss/?outputType=xml&tags=real-world-assets", "verticals": ["RWA"]},

    # Агро (новые рабочие)
    {"name": "Farm Progress", "url": "https://www.farmprogress.com/rss.xml", "verticals": ["Agriculture"]},
    {"name": "Time.kz", "url": "https://time.kz/rss", "verticals": ["Agriculture"]},
    {"name": "Investing.com Commodities", "url": "https://www.investing.com/rss/news_14.rss", "verticals": ["RWA", "Agriculture"]},

    # Commodities
    {"name": "Oilprice", "url": "https://oilprice.com/rss/main", "verticals": ["RWA"]},

    # Mainstream
    {"name": "Financial Times", "url": "https://www.ft.com/rss/home", "verticals": ["Mainstream"]},
    {"name": "TechCrunch Fintech", "url": "https://techcrunch.com/category/fintech/feed/", "verticals": ["Mainstream"]},
]


def main():
    api_key = os.getenv("NOTION_API_KEY")
    parent_page_id = "2f77eb3f-b6bb-8055-9010-d60da4127656"  # News for Clients page

    http_client = httpx.Client(timeout=60.0)
    notion = Client(auth=api_key, client=http_client)

    print("=" * 60)
    print("SETUP NOTION SOURCES DATABASE")
    print("=" * 60)

    try:
        # Создаём новую базу данных с правильными полями
        print("\n[1] Creating database with proper schema...")

        new_db = notion.databases.create(
            parent={"type": "page_id", "page_id": parent_page_id},
            title=[{"type": "text", "text": {"content": "RSS Sources"}}],
            properties={
                "Name": {"title": {}},
                "RSS URL": {"url": {}},
                "Vertical": {
                    "multi_select": {
                        "options": [
                            {"name": "RWA", "color": "green"},
                            {"name": "Agriculture", "color": "blue"},
                            {"name": "DeFi", "color": "purple"},
                            {"name": "Mainstream", "color": "orange"},
                        ]
                    }
                },
                "Active": {"checkbox": {}},
            }
        )

        db_id = new_db["id"]
        print(f"    Database created: {db_id}")
        print(f"    URL: {new_db['url']}")

        # Проверяем что поля создались
        print(f"\n    Properties:")
        for name, prop in new_db.get("properties", {}).items():
            print(f"      - {name} ({prop['type']})")

        # Добавляем источники
        print(f"\n[2] Adding {len(ALL_SOURCES)} sources...")

        for source in ALL_SOURCES:
            try:
                page = notion.pages.create(
                    parent={"database_id": db_id},
                    properties={
                        "Name": {"title": [{"text": {"content": source["name"]}}]},
                        "RSS URL": {"url": source["url"]},
                        "Vertical": {"multi_select": [{"name": v} for v in source["verticals"]]},
                        "Active": {"checkbox": True},
                    }
                )
                print(f"    + {source['name']}")
            except Exception as e:
                print(f"    x {source['name']}: {e}")

        # Обновляем .env
        print(f"\n[3] Updating .env...")
        env_path = os.path.join(os.path.dirname(__file__), ".env")
        with open(env_path, "r") as f:
            content = f.read()

        # Заменяем старый ID на новый
        import re
        content = re.sub(
            r"NOTION_SOURCES_DB_ID=.*",
            f"NOTION_SOURCES_DB_ID={db_id.replace('-', '')}",
            content
        )
        with open(env_path, "w") as f:
            f.write(content)

        print(f"    NOTION_SOURCES_DB_ID updated")

        print("\n" + "=" * 60)
        print("DONE!")
        print("=" * 60)

    except Exception as e:
        import traceback
        print(f"ERROR: {e}")
        traceback.print_exc()
    finally:
        http_client.close()


if __name__ == "__main__":
    main()
